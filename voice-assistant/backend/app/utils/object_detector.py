import cv2
import numpy as np
import logging
from typing import List, Dict, Any
import os

class ObjectDetector:
    def __init__(self):
        # Define the classes the model can detect
        self.CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                       "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                       "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                       "sofa", "train", "tvmonitor", "cell phone"]
        
        # Define suspicious objects we want to detect
        self.SUSPICIOUS_OBJECTS = ["cell phone", "laptop", "tablet", "book", "paper", "notebook"]
        
        # Model paths (resolve relative to this package so it works from any CWD)
        _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.prototxt = os.path.join(_root, "models", "MobileNetSSD_deploy.prototxt")
        self.model = os.path.join(_root, "models", "MobileNetSSD_deploy.caffemodel")
        
        # Initialize the model if files exist
        self.net = None
        if os.path.exists(self.prototxt) and os.path.exists(self.model):
            try:
                self.net = cv2.dnn.readNetFromCaffe(self.prototxt, self.model)
                logging.info("Successfully loaded object detection model")
            except Exception as e:
                logging.error(f"Failed to load object detection model: {e}")
        else:
            logging.warning("Object detection model files not found. Object detection will be disabled.")
    
    def detect_objects(self, frame, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Detect objects in the given frame.
        
        Args:
            frame: Input image frame (BGR format)
            confidence_threshold: Minimum confidence score for detection
            
        Returns:
            List of detected objects with their properties
        """
        if self.net is None:
            return []
            
        try:
            (h, w) = frame.shape[:2]
            
            # Create a blob from the frame and perform a forward pass
            blob = cv2.dnn.blobFromImage(
                cv2.resize(frame, (300, 300)), 
                0.007843, 
                (300, 300), 
                127.5
            )
            self.net.setInput(blob)
            detections = self.net.forward()
            
            detected_objects = []
            
            # Loop over the detections
            for i in range(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                # Filter out weak detections
                if confidence > confidence_threshold:
                    idx = int(detections[0, 0, i, 1])
                    
                    # Skip if class index is out of range
                    if idx >= len(self.CLASSES):
                        continue
                        
                    class_name = self.CLASSES[idx]
                    
                    # Skip if not a suspicious object
                    if class_name not in self.SUSPICIOUS_OBJECTS:
                        continue
                    
                    # Compute the (x, y)-coordinates of the bounding box
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    
                    # Ensure the bounding boxes fall within the dimensions of the frame
                    (startX, startY) = (max(0, startX), max(0, startY))
                    (endX, endY) = (min(w - 1, endX), min(h - 1, endY))
                    
                    # Calculate area of the bounding box
                    bbox_area = (endX - startX) * (endY - startY)
                    
                    # Skip if the bounding box is too small
                    if bbox_area < 1000:  # Minimum area threshold
                        continue
                    
                    detected_objects.append({
                        "label": class_name,
                        "confidence": float(confidence),
                        "bbox": [int(startX), int(startY), int(endX), int(endY)],
                        "area": bbox_area
                    })
            
            return detected_objects
            
        except Exception as e:
            logging.error(f"Error in object detection: {e}")
            return []
    
    def draw_detections(self, frame, detections):
        """Draw bounding boxes and labels on the frame"""
        for obj in detections:
            startX, startY, endX, endY = obj["bbox"]
            label = f"{obj['label']}: {obj['confidence']:.2f}"
            
            # Draw rectangle and label
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(
                frame, 
                label, 
                (startX, y), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                (0, 0, 255), 
                2
            )
        
        return frame
