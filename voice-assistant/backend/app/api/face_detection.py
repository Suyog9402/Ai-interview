from __future__ import annotations

import asyncio
import base64
import json
import logging
import time
from typing import Any, Dict

import cv2
import mediapipe as mp
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from scipy.spatial import distance as dist

from app.services.voice_analysis import voice_analysis_service

logger = logging.getLogger("face-detection")

# Lazy-loaded object detector for cell phone / device detection (optional; model files may be missing)
_object_detector_instance = None

def _get_object_detector():
    """Get or create ObjectDetector instance. Returns None if model files are missing."""
    global _object_detector_instance
    if _object_detector_instance is None:
        try:
            from app.utils.object_detector import ObjectDetector
            _object_detector_instance = ObjectDetector()
            if _object_detector_instance.net is None:
                _object_detector_instance = None
        except Exception as e:
            logger.debug("ObjectDetector not available: %s", e)
            _object_detector_instance = None
    return _object_detector_instance
router = APIRouter(prefix="/face-detection", tags=["face-detection"])


# -----------------------------x
# Enhanced Face Detector
# -----------------------------
class EnhancedFaceDetector:
    def __init__(self) -> None:
        # MediaPipe modules - lazy loaded to handle API changes
        self.mp_face_detection = None
        self.mp_face_mesh = None
        self.face_detection = None
        self.face_mesh = None
        self._mediapipe_available = False
        
        # Try to initialize MediaPipe (may fail with newer versions)
        try:
            if hasattr(mp, 'solutions'):
                self.mp_face_detection = mp.solutions.face_detection
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_detection = self.mp_face_detection.FaceDetection(
                    model_selection=1, min_detection_confidence=0.5
                )
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=10,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
                self._mediapipe_available = True
            else:
                logger.warning("MediaPipe solutions API not available. Using OpenCV fallback only.")
        except Exception as e:
            logger.warning(f"Failed to initialize MediaPipe: {e}. Using OpenCV fallback only.")

        # OpenCV cascades as fallback
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        # Screen activity tracking
        self.last_activity_time = time.time()
        self.last_face_position = None
        self.face_movement_threshold = 50  # pixels
        self.screen_switch_detected = False
        self.screen_switch_start_time = None

        # Temporal smoothing for presence (hysteresis)
        self.with_face_frames = 0
        self.no_face_frames = 0
        self.state_face_detected = False
        self.flip_up = 2     # need 2 consecutive frames w/ face to switch to True
        self.flip_down = 5   # need 5 consecutive frames w/o face to switch to False

        # Mobile device detection
        self.mobile_device_detected = False
        self.suspicious_objects_detected = []

    # ---- Mobile device detection: DNN only (no heuristic = no false positives) ----
    def detect_mobile_devices(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Report mobile devices only when MobileNetSSD DNN detects 'cell phone'.
        No contour/heuristic fallback - avoids false positives (windows, lamps, etc.).
        Add model files to backend/app/models/ for phone detection.
        """
        try:
            mobile_objects = []
            obj_det = _get_object_detector()
            if obj_det is not None and obj_det.net is not None:
                dnn_objects = obj_det.detect_objects(frame, confidence_threshold=0.4)
                for obj in dnn_objects:
                    label = obj.get("label", "")
                    if label and "phone" in label.lower():
                        bbox = obj.get("bbox", [0, 0, 0, 0])
                        mobile_objects.append({
                            "type": label,
                            "confidence": float(obj.get("confidence", 0.5)),
                            "bbox": {"x": bbox[0], "y": bbox[1], "width": bbox[2] - bbox[0], "height": bbox[3] - bbox[1]},
                            "area": obj.get("area", 0),
                            "aspect_ratio": 1.0,
                        })
            if mobile_objects:
                logger.info("Mobile devices (DNN): %d", len(mobile_objects))
            return {
                "mobile_devices_detected": len(mobile_objects) > 0,
                "device_count": len(mobile_objects),
                "devices": mobile_objects,
            }
        except Exception as e:
            logger.exception("Error in mobile device detection: %s", e)
            return {
                "mobile_devices_detected": False,
                "device_count": 0,
                "devices": [],
            }

    # ---- Suspicious object detection ----
    def detect_suspicious_objects(self, frame: np.ndarray) -> Dict[str, Any]:
        """Detect suspicious objects like papers, books, notes, etc. using OpenCV."""
        try:
            suspicious_objects = []
            
            # Detect rectangular objects that might be papers/notes using contour detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 2000:  # Filter small contours
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Paper-like aspect ratios (typically 0.7-1.4)
                    if 0.5 <= aspect_ratio <= 2.0 and area > 3000:
                        # Check if it's not a face
                        face_roi = gray[y:y+h, x:x+w]
                        faces_in_roi = self.face_cascade.detectMultiScale(face_roi, 1.1, 4)
                        if len(faces_in_roi) == 0:
                            suspicious_objects.append({
                                'type': 'potential_paper_note',
                                'confidence': 0.6,
                                'bbox': {'x': x, 'y': y, 'width': w, 'height': h}
                            })
            
            return {
                'suspicious_objects_detected': len(suspicious_objects) > 0,
                'object_count': len(suspicious_objects),
                'objects': suspicious_objects
            }
        except Exception as e:
            logger.exception("Error in suspicious object detection: %s", e)
            return {
                'suspicious_objects_detected': False,
                'object_count': 0,
                'objects': []
            }

    # ---- Enhanced screen switching detection ----
    def detect_screen_sharing(self, analysis: Dict[str, Any], face_landmarks=None) -> Dict[str, Any]:
        """Enhanced screen switching detection - only triggers for actual tab/app switching."""
        now = time.time()
        time_since_last = now - self.last_activity_time
        
        # Update activity time if face is detected and looking at screen
        if analysis.get("face_detected") and analysis.get("head_pose", {}).get("looking_at_screen"):
            self.last_activity_time = now
            self.screen_switch_detected = False
            self.screen_switch_start_time = None
        
        # Detect screen switching based on more specific criteria for tab/app switching
        screen_switching = False
        switching_reason = []
        
        # 1. Extended time-based detection (no face activity for longer period - more likely tab switching)
        if time_since_last > 5.0 and not analysis.get("face_detected"):
            screen_switching = True
            switching_reason.append("No face detected for extended period (likely tab switching)")
        
        # 2. Sudden disappearance followed by reappearance (tab switching pattern)
        if face_landmarks and analysis.get("face_detected"):
            current_face_center = self._get_face_center(face_landmarks)
            if self.last_face_position is not None:
                movement = np.linalg.norm(current_face_center - self.last_face_position)
                # Only trigger for very large movements (likely tab switching)
                if movement > self.face_movement_threshold * 2:  # Double the threshold
                    screen_switching = True
                    switching_reason.append("Sudden large face movement (possible tab switching)")
            self.last_face_position = current_face_center
        
        # 3. Head pose changes - only trigger for sustained looking away (not brief glances)
        head_pose = analysis.get("head_pose", {})
        if not head_pose.get("looking_at_screen") and analysis.get("face_detected"):
            # Only consider it screen switching if sustained for multiple frames
            if not hasattr(self, 'looking_away_frames'):
                self.looking_away_frames = 0
            self.looking_away_frames += 1
            
            # Only trigger after sustained looking away (3+ seconds worth of frames at 10fps)
            if self.looking_away_frames > 30:  # 3 seconds at 10fps
                screen_switching = True
                switching_reason.append("Sustained looking away (possible tab switching)")
        else:
            # Reset counter when looking back at screen
            if hasattr(self, 'looking_away_frames'):
                self.looking_away_frames = 0
        
        # 4. Eye tracking changes - only for sustained looking away
        eye_tracking = analysis.get("eye_tracking", {})
        if eye_tracking.get("eye_tracking") == "looking_away" and analysis.get("face_detected"):
            # Only consider it screen switching if sustained
            if not hasattr(self, 'eyes_away_frames'):
                self.eyes_away_frames = 0
            self.eyes_away_frames += 1
            
            # Only trigger after sustained eye movement away (2+ seconds worth of frames)
            if self.eyes_away_frames > 20:  # 2 seconds at 10fps
                screen_switching = True
                switching_reason.append("Sustained eye movement away (possible tab switching)")
        else:
            # Reset counter when eyes back on screen
            if hasattr(self, 'eyes_away_frames'):
                self.eyes_away_frames = 0
        
        # 5. Additional check: rapid head movements followed by stillness (tab switching pattern)
        if hasattr(self, 'last_head_pose') and head_pose.get("head_pose"):
            current_head_pose = head_pose.get("head_pose")
            if self.last_head_pose != current_head_pose:
                # Head pose changed
                if not hasattr(self, 'head_pose_change_time'):
                    self.head_pose_change_time = now
                elif now - self.head_pose_change_time > 2.0:  # If head pose changed and stayed changed for 2+ seconds
                    screen_switching = True
                    switching_reason.append("Sustained head pose change (possible tab switching)")
            else:
                # Reset if head pose is stable
                if hasattr(self, 'head_pose_change_time'):
                    delattr(self, 'head_pose_change_time')
            self.last_head_pose = current_head_pose
        
        # Track screen switching state
        if screen_switching and not self.screen_switch_detected:
            self.screen_switch_detected = True
            self.screen_switch_start_time = now
        elif not screen_switching and self.screen_switch_detected:
            self.screen_switch_detected = False
            self.screen_switch_start_time = None
        
        return {
            "screen_sharing_detected": bool(screen_switching),
            "time_since_last_activity": float(time_since_last),
            "switching_reason": switching_reason,
            "switch_duration": float(now - self.screen_switch_start_time) if self.screen_switch_start_time else 0.0
        }

    def _get_face_center(self, face_landmarks):
        """Get the center point of the face from landmarks."""
        try:
            landmarks = face_landmarks.landmark
            if len(landmarks) < 468:
                return np.array([0, 0])
            
            # Use nose tip as face center
            nose_tip = landmarks[4]  # nose tip landmark
            return np.array([nose_tip.x, nose_tip.y])
        except Exception:
            return np.array([0, 0])

    # ---- Face detection (MP + fallback) ----
    def detect_faces_mediapipe(self, frame: np.ndarray):
        if not self._mediapipe_available or self.face_detection is None:
            return []
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb_frame)
            return results.detections if results and results.detections else []
        except Exception as e:
            logger.warning(f"MediaPipe face detection error: {e}")
            return []

    def detect_faces_opencv(self, frame: np.ndarray):
        """Detect faces with OpenCV Haar cascade and merge overlapping detections (one face = one box)."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        raw_faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        if raw_faces is None or len(raw_faces) == 0:
            return np.array([])
        # Merge overlapping boxes so we get one box per face (industry standard: groupRectangles)
        try:
            # groupThreshold=1: keep group if at least 1 rect; eps=0.2: overlap ratio to merge
            grouped, _ = cv2.groupRectangles(raw_faces.tolist(), 1, 0.2)
            if grouped:
                return np.array(grouped)
            # Some OpenCV versions return [] for a single rect; never drop the only face
            return raw_faces
        except Exception as e:
            logger.debug("groupRectangles fallback: %s", e)
            return raw_faces

    # ---- Head pose (simple heuristic using eye positions) ----
    def analyze_head_pose(self, frame: np.ndarray, face_landmarks) -> Dict[str, Any]:
        if not face_landmarks:
            return {"looking_at_screen": False, "head_pose": "unknown", "gaze_distance": 0.0}

        try:
            h, w = frame.shape[:2]
            landmarks = face_landmarks.landmark
            if len(landmarks) < 468:
                return {"looking_at_screen": False, "head_pose": "unknown", "gaze_distance": 0.0}

            left_eye = np.array([landmarks[33].x * w, landmarks[33].y * h], dtype=float)
            right_eye = np.array([landmarks[263].x * w, landmarks[263].y * h], dtype=float)
            eye_center = (left_eye + right_eye) / 2.0

            screen_center = np.array([w / 2.0, h / 2.0], dtype=float)
            gaze_vector = eye_center - screen_center
            gaze_distance = float(np.linalg.norm(gaze_vector))
            looking_at_screen = gaze_distance < (w * 0.3)

            head_pose = "center"
            if left_eye[0] < (w * 0.4):
                head_pose = "left"
            elif right_eye[0] > (w * 0.6):
                head_pose = "right"
            elif eye_center[1] < (h * 0.4):
                head_pose = "up"
            elif eye_center[1] > (h * 0.6):
                head_pose = "down"

            return {
                "looking_at_screen": bool(looking_at_screen),
                "head_pose": str(head_pose),
                "gaze_distance": float(gaze_distance),
            }
        except Exception as e:
            logger.exception("Error in head pose analysis: %s", e)
            return {"looking_at_screen": False, "head_pose": "unknown", "gaze_distance": 0.0}

    # ---- Multiple faces check (industry-grade: no false positives) ----
    def detect_multiple_faces(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Count distinct faces. OpenCV detections are merged (groupRectangles) so one face = one box.
        We only set multiple_faces_detected=True when BOTH pipelines agree on >= 2 faces,
        to avoid false positives (reflections, duplicate boxes, posters).
        """
        try:
            mp_count = 0
            if self._mediapipe_available and self.face_mesh is not None:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(rgb_frame)
                if results and getattr(results, "multi_face_landmarks", None):
                    landmarks_list = results.multi_face_landmarks
                    # Filter out duplicate/reflection: count only faces with distinct centers (min distance)
                    if len(landmarks_list) >= 2:
                        h, w = frame.shape[:2]
                        centers = []
                        for lm in landmarks_list:
                            if lm and len(lm.landmark) > 4:
                                nose = lm.landmark[4]
                                centers.append((nose.x * w, nose.y * h))
                        if len(centers) >= 2:
                            min_dist = float("inf")
                            for i in range(len(centers)):
                                for j in range(i + 1, len(centers)):
                                    d = np.sqrt((centers[i][0] - centers[j][0]) ** 2 + (centers[i][1] - centers[j][1]) ** 2)
                                    min_dist = min(min_dist, d)
                            # If two "faces" are very close (< 15% of frame diag), treat as one (reflection/dup)
                            if min_dist < 0.15 * np.sqrt(w * w + h * h):
                                mp_count = 1
                            else:
                                mp_count = len(landmarks_list)
                        else:
                            mp_count = len(landmarks_list)
                    else:
                        mp_count = len(landmarks_list)

            ocv_faces = self.detect_faces_opencv(frame)
            ocv_count = len(ocv_faces) if ocv_faces is not None else 0

            final_count = max(int(mp_count), int(ocv_count))
            # Enterprise: only flag multiple when BOTH pipelines agree on >= 2 (zero false positives)
            multiple_faces_detected = (mp_count >= 2 and ocv_count >= 2)
            return {
                "face_count": final_count,
                "multiple_faces_detected": bool(multiple_faces_detected),
                "mediapipe_faces": int(mp_count),
                "opencv_faces": int(ocv_count),
            }
        except Exception as e:
            logger.exception("Error in detect_multiple_faces: %s", e)
            return {
                "face_count": 0,
                "multiple_faces_detected": False,
                "mediapipe_faces": 0,
                "opencv_faces": 0,
            }

    # ---- Eyes / gaze ----
    def analyze_eye_tracking(self, frame: np.ndarray, face_landmarks) -> Dict[str, Any]:
        if not face_landmarks:
            return {"eye_state": "unknown", "eye_tracking": "unknown", "eye_aspect_ratio": 0.0, "screen_distance": 0.0}

        try:
            h, w = frame.shape[:2]
            landmarks = face_landmarks.landmark
            if len(landmarks) < 468:
                return {"eye_state": "unknown", "eye_tracking": "unknown", "eye_aspect_ratio": 0.0, "screen_distance": 0.0}

            left_points = np.array(
                [
                    [landmarks[33].x * w, landmarks[33].y * h],
                    [landmarks[7].x * w, landmarks[7].y * h],
                    [landmarks[163].x * w, landmarks[163].y * h],
                    [landmarks[145].x * w, landmarks[145].y * h],
                ],
                dtype=float,
            )

            right_points = np.array(
                [
                    [landmarks[263].x * w, landmarks[263].y * h],
                    [landmarks[386].x * w, landmarks[386].y * h],
                    [landmarks[362].x * w, landmarks[362].y * h],
                    [landmarks[374].x * w, landmarks[374].y * h],
                ],
                dtype=float,
            )

            def ear(pts: np.ndarray) -> float:
                try:
                    A = dist.euclidean(pts[1], pts[3])  # vertical
                    B = dist.euclidean(pts[0], pts[2])  # diagonal (approx)
                    C = dist.euclidean(pts[0], pts[2])  # horizontal
                    return float((A + B) / (2.0 * C)) if C > 0 else 0.3
                except Exception:
                    return 0.3

            left_ear = ear(left_points)
            right_ear = ear(right_points)
            avg_ear = (left_ear + right_ear) / 2.0

            if avg_ear < 0.2:
                eye_state = "closed"
            elif avg_ear < 0.25:
                eye_state = "blinking"
            else:
                eye_state = "open"

            left_center = np.mean(left_points, axis=0)
            right_center = np.mean(right_points, axis=0)
            eye_center = (left_center + right_center) / 2.0

            screen_center = np.array([w / 2.0, h / 2.0], dtype=float)
            dist_to_center = float(np.linalg.norm(eye_center - screen_center))
            looking_at_screen = dist_to_center < (w * 0.3)

            return {
                "eye_state": str(eye_state),
                "eye_tracking": "looking_at_screen" if looking_at_screen else "looking_away",
                "eye_aspect_ratio": float(avg_ear),
                "screen_distance": float(dist_to_center),
            }
        except Exception as e:
            logger.exception("Error in eye tracking analysis: %s", e)
            return {"eye_state": "unknown", "eye_tracking": "unknown", "eye_aspect_ratio": 0.0, "screen_distance": 0.0}

    # ---- Voice analysis integration ----
    def analyze_voice_patterns(self) -> Dict[str, Any]:
        state = voice_analysis_service.get_analysis_state()
        return {
            "speaking": bool(state.get("speaking", False)),
            "confidence": float(state.get("confidence", 0.0)),
            "nervousness": float(state.get("nervousness", 0.0)),
            "speech_patterns": list(state.get("speech_patterns", [])),
        }

    # ---- Main per-frame processor ----
    def process_frame(self, frame: np.ndarray):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        analysis: Dict[str, Any] = {
            "face_detected": False,
            "face_count": 0,
            "confidence": 0.0,
            "attention_score": 0.0,
            "engagement_level": "low",
            "eye_tracking": {},
            "head_pose": {},
            "multiple_faces": {},
            "screen_sharing": {},
            "voice_analysis": {},
            "mobile_devices": {},
            "suspicious_objects": {},
            "suspicious_behavior": [],
            "recommendations": [],
        }

        # 1) detection
        face_dets = self.detect_faces_mediapipe(frame)
        face_landmarks = None
        confidence = 0.0

        if face_dets:
            det = max(face_dets, key=lambda d: d.score[0] if d.score else 0.0)
            confidence = float(det.score[0] if det.score else 0.0)
            if self._mediapipe_available and self.face_mesh is not None:
                face_mesh_results = self.face_mesh.process(rgb_frame)
                if face_mesh_results and face_mesh_results.multi_face_landmarks:
                    face_landmarks = face_mesh_results.multi_face_landmarks[0]
        else:
            ocv_faces = self.detect_faces_opencv(frame)
            if ocv_faces is not None and len(ocv_faces) > 0:
                confidence = 0.6  # fallback heuristic

        # 2) temporal smoothing state machine
        if confidence > 0.0:
            self.with_face_frames += 1
            self.no_face_frames = 0
            if not self.state_face_detected and self.with_face_frames >= self.flip_up:
                self.state_face_detected = True
        else:
            self.no_face_frames += 1
            self.with_face_frames = 0
            if self.state_face_detected and self.no_face_frames >= self.flip_down:
                self.state_face_detected = False

        # 3) Always run multi-face, mobile, suspicious (even when no face) for enterprise proctoring
        multi = self.detect_multiple_faces(frame)
        mobile = self.detect_mobile_devices(frame)
        suspicious = self.detect_suspicious_objects(frame)

        # 4) features & output
        if confidence > 0.0:
            head_pose = self.analyze_head_pose(frame, face_landmarks)
            eye_track = self.analyze_eye_tracking(frame, face_landmarks)

            attention_score = 0.0
            if head_pose.get("looking_at_screen"):
                attention_score += 0.4
            if eye_track.get("eye_state") == "open":
                attention_score += 0.3
            if eye_track.get("eye_tracking") == "looking_at_screen":
                attention_score += 0.3

            engagement_level = (
                "high" if (attention_score > 0.8 and confidence > 0.7)
                else "medium" if (attention_score > 0.5 and confidence > 0.5)
                else "low"
            )

            analysis.update(
                {
                    "face_detected": bool(self.state_face_detected),
                    "face_count": int(multi["face_count"]),
                    "confidence": float(confidence),
                    "attention_score": float(attention_score),
                    "engagement_level": str(engagement_level),
                    "eye_tracking": eye_track,
                    "head_pose": head_pose,
                    "multiple_faces": multi,
                    "mobile_devices": mobile,
                    "suspicious_objects": suspicious,
                }
            )

            analysis["screen_sharing"] = self.detect_screen_sharing(analysis, face_landmarks)
            voice_state = self.analyze_voice_patterns()
            analysis["voice_analysis"] = voice_state

            recs, sus = [], []
            
            # Face and attention recommendations
            if not head_pose.get("looking_at_screen"):
                recs.append("Please look directly at the camera")
                sus.append("User not looking at screen")
            
            hp = head_pose.get("head_pose", "center")
            if hp in {"left", "right", "up", "down"}:
                recs.append(f"Please face the camera directly (currently looking {hp})")
                sus.append(f"Head turned {hp}")
            
            if eye_track.get("eye_state") == "closed":
                recs.append("Keep your eyes open and focused")
                sus.append("Eyes closed - may indicate inattention")
            
            if eye_track.get("eye_tracking") == "looking_away":
                recs.append("Please look at the camera")
                sus.append("Eyes not focused on screen")
            
            # Multiple faces
            if multi.get("multiple_faces_detected"):
                recs.append("Only one person should be visible in the camera")
                sus.append(f"Multiple faces detected ({multi.get('face_count', 0)} people)")
            
            # Screen switching
            if analysis["screen_sharing"].get("screen_sharing_detected"):
                recs.append("Please stay focused on the interview - avoid switching tabs or applications")
                sus.append("Potential tab/application switching detected")
            
            # Mobile devices
            if mobile.get("mobile_devices_detected"):
                recs.append("Please remove mobile devices from camera view")
                sus.append(f"Mobile device detected ({mobile.get('device_count', 0)} devices)")
            
            # Suspicious objects
            if suspicious.get("suspicious_objects_detected"):
                recs.append("Please remove any papers, notes, or reference materials")
                sus.append(f"Suspicious objects detected ({suspicious.get('object_count', 0)} objects)")
            
            # Voice analysis
            if voice_state.get("nervousness", 0.0) > 0.7:
                recs.append("Try to speak more confidently and clearly")
                sus.append("High nervousness detected in voice")
            
            if voice_state.get("confidence", 0.0) < 0.3:
                recs.append("Speak with more confidence and clarity")
                sus.append("Low confidence detected in voice")
            
            if engagement_level == "low":
                recs.append("Please maintain focus and engagement")
                sus.append("Low engagement detected")

            analysis["recommendations"] = recs
            analysis["suspicious_behavior"] = sus
        else:
            recs, sus = [], []
            if multi.get("multiple_faces_detected"):
                recs.append("Only one person should be visible in the camera")
                sus.append(f"Multiple faces detected ({multi.get('face_count', 0)} people)")
            if mobile.get("mobile_devices_detected"):
                recs.append("Please remove mobile devices from camera view")
                sus.append(f"Mobile device detected ({mobile.get('device_count', 0)} devices)")
            if suspicious.get("suspicious_objects_detected"):
                recs.append("Please remove any papers, notes, or reference materials")
                sus.append(f"Suspicious objects detected ({suspicious.get('object_count', 0)} objects)")
            analysis.update(
                {
                    "face_detected": bool(self.state_face_detected),
                    "face_count": int(multi.get("face_count", 0)),
                    "confidence": 0.0,
                    "attention_score": 0.0,
                    "engagement_level": "low",
                    "eye_tracking": {"eye_state": "unknown", "eye_tracking": "unknown"},
                    "head_pose": {"looking_at_screen": False, "head_pose": "unknown"},
                    "multiple_faces": multi,
                    "mobile_devices": mobile,
                    "suspicious_objects": suspicious,
                    "recommendations": recs,
                    "suspicious_behavior": sus,
                }
            )
            analysis["screen_sharing"] = self.detect_screen_sharing(analysis)
            analysis["voice_analysis"] = self.analyze_voice_patterns()

        return frame, analysis


# Lazy initialization - only create when needed to avoid import errors
_face_detector_instance = None

def get_face_detector():
    """Get or create the face detector instance (lazy initialization)."""
    global _face_detector_instance
    if _face_detector_instance is None:
        _face_detector_instance = EnhancedFaceDetector()
    return _face_detector_instance


# -----------------------------
# Connections / Manager
# -----------------------------
class FaceDetectionManager:
    """Tracks connected clients. No physical camera is used (client sends frames)."""

    def __init__(self) -> None:
        self.is_streaming: bool = False
        self.connections: Dict[str, Dict[str, Any]] = {}

    async def start_camera(self) -> None:
        if not self.is_streaming:
            logger.info("Starting face detection streaming (client-provided frames).")
            self.is_streaming = True

    async def stop_camera(self) -> None:
        if self.is_streaming:
            logger.info("Stopping face detection streaming.")
            self.is_streaming = False


face_manager = FaceDetectionManager()


# -----------------------------
# WebSocket endpoint
# -----------------------------
@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Accepts base64-encoded image frames from the client and returns analysis."""
    await websocket.accept()
    logger.info("Client %s connected to enhanced face detection", client_id)

    face_manager.connections[client_id] = {"websocket": websocket, "last_active": time.time()}
    try:
        while True:
            msg = await websocket.receive_json()
            msg_type = msg.get("type")

            if msg_type == "video_frame":
                frame_data = msg.get("data", {})
                image_b64 = frame_data.get("image")
                if not image_b64:
                    continue

                try:
                    header, encoded = image_b64.split(",", 1) if "," in image_b64 else ("", image_b64)
                    binary = base64.b64decode(encoded)
                    nparr = np.frombuffer(binary, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if frame is None:
                        continue
                    # Resize small frames so face detection works (e.g. small preview from frontend)
                    h, w = frame.shape[:2]
                    min_side = 320
                    if h < min_side or w < min_side:
                        scale = min_side / min(h, w)
                        new_w, new_h = int(round(w * scale)), int(round(h * scale))
                        frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

                    detector = get_face_detector()
                    _, analysis = detector.process_frame(frame)

                    # Check if websocket is still open before sending
                    if websocket.client_state.name == "CONNECTED":
                        try:
                            await websocket.send_json(
                                {
                                    "type": "analysis_result",
                                    "data": {"analysis": analysis, "timestamp": time.time()},
                                }
                            )
                        except Exception as send_error:
                            logger.warning("Failed to send analysis result: %s", send_error)
                            break  # Exit the loop if we can't send
                except Exception as e:
                    logger.exception("Error processing incoming frame: %s", e)
                    # Check if websocket is still open before sending error response
                    if websocket.client_state.name == "CONNECTED":
                        try:
                            await websocket.send_json(
                                {
                                    "type": "analysis_result",
                                    "data": {
                                        "analysis": {
                                            "face_detected": False,
                                            "face_count": 0,
                                            "confidence": 0.0,
                                            "attention_score": 0.0,
                                            "engagement_level": "low",
                                            "eye_tracking": {"eye_state": "unknown", "eye_tracking": "unknown"},
                                            "head_pose": {"looking_at_screen": False, "head_pose": "unknown"},
                                            "multiple_faces": {"face_count": 0, "multiple_faces_detected": False},
                                            "mobile_devices": {"mobile_devices_detected": False, "device_count": 0, "devices": []},
                                            "suspicious_objects": {"suspicious_objects_detected": False, "object_count": 0, "objects": []},
                                            "screen_sharing": {"screen_sharing_detected": False, "time_since_last_activity": 0.0},
                                            "voice_analysis": {"speaking": False, "confidence": 0.0, "nervousness": 0.0, "speech_patterns": []},
                                            "suspicious_behavior": ["Frame processing error"],
                                            "recommendations": ["Please check camera connection"],
                                            "error": str(e),
                                        },
                                        "timestamp": time.time(),
                                    },
                                }
                            )
                        except Exception as send_error:
                            logger.warning("Failed to send error response: %s", send_error)
                            break  # Exit the loop if we can't send

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            await asyncio.sleep(0)

    except WebSocketDisconnect:
        logger.info("Client %s disconnected", client_id)
    except Exception as e:
        logger.exception("WebSocket error for client %s: %s", client_id, e)
    finally:
        face_manager.connections.pop(client_id, None)
        logger.info("Removed client %s from connections", client_id)


# -----------------------------
# REST endpoints
# -----------------------------
@router.post("/start")
async def start_face_detection():
    try:
        await face_manager.start_camera()
        return {"status": "success", "message": "Enhanced face detection started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/stop")
async def stop_face_detection():
    try:
        await face_manager.stop_camera()
        return {"status": "success", "message": "Enhanced face detection stopped"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/start-camera/{client_id}")
async def start_camera_for_client(client_id: str):
    try:
        if client_id in face_manager.connections:
            await face_manager.start_camera()
            return {"status": "success", "message": "Camera started successfully"}
        return {"status": "error", "message": "Client not connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/stop-camera/{client_id}")
async def stop_camera_for_client(client_id: str):
    try:
        if client_id in face_manager.connections:
            await face_manager.stop_camera()
            return {"status": "success", "message": "Camera stopped successfully"}
        return {"status": "error", "message": "Client not connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/update-voice-analysis")
async def update_voice_analysis(voice_data: Dict[str, Any]):
    """Pass text or audio-derived info to the voice analysis service."""
    try:
        if "text_data" in voice_data:
            voice_analysis_service.update_voice_analysis(text_data=voice_data["text_data"])
        elif "audio_data" in voice_data:
            voice_analysis_service.update_voice_analysis(audio_data=voice_data["audio_data"])
        return {"status": "success", "message": "Voice analysis updated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/status")
async def get_face_detection_status():
    """Return the service status (no local camera used; client supplies frames)."""
    return {
        "is_streaming": face_manager.is_streaming,
        "camera_available": False,
        "camera_started": face_manager.is_streaming,
        "active_connections": len(face_manager.connections),
        "features": [
            "Eye tracking",
            "Head pose detection",
            "Multiple face detection",
            "Screen sharing detection",
            "Voice analysis integration",
            "Temporal smoothing",
        ],
    }
