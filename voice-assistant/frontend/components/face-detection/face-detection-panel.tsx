"use client";

import React, {
  useEffect,
  useRef,
  useState,
  useCallback,
  forwardRef,
  useImperativeHandle,
} from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Camera, Eye, Smiley, Warning, X } from "@phosphor-icons/react";

interface AnalysisData {
  emotion?: string;
  eye_state?: string;
  face_detected?: boolean;
  confidence?: number;
  attention_score?: number;
  engagement_level?: string;
  recommendations?: string[];
  suspicious_behavior?: string[];
  eye_tracking?: {
    eye_state?: string;
    eye_tracking?: string;
    eye_aspect_ratio?: number;
    screen_distance?: number;
  };
  head_pose?: {
    looking_at_screen?: boolean;
    head_pose?: string;
    gaze_distance?: number;
  };
  multiple_faces?: {
    face_count?: number;
    multiple_faces_detected?: boolean;
  };
  screen_sharing?: {
    screen_sharing_detected?: boolean;
    time_since_last_activity?: number;
    switching_reason?: string[];
  };
  mobile_devices?: {
    mobile_devices_detected?: boolean;
    device_count?: number;
    devices?: { type: string; confidence: number }[];
  };
  suspicious_objects?: {
    suspicious_objects_detected?: boolean;
    object_count?: number;
    objects?: { type: string; confidence: number }[];
  };
  voice_analysis?: {
    speaking?: boolean;
    confidence?: number;
    nervousness?: number;
    speech_patterns?: string[];
  };
}

interface FaceDetectionPanelProps {
  isActive: boolean;
  onToggle: () => void;
  className?: string;
  shouldStartCamera?: boolean;
  onAnalysisDataChange?: (data: AnalysisData) => void;
}

export const FaceDetectionPanel = forwardRef<
  { forceDisconnect: () => void },
  FaceDetectionPanelProps
>(function FaceDetectionPanel(
  {
    isActive,
    onToggle,
    className = "",
    shouldStartCamera = false,
    onAnalysisDataChange,
  },
  ref,
) {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cameraStarted, setCameraStarted] = useState(false);
  const [analysisData, setAnalysisData] = useState<AnalysisData>({});

  const wsRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null); // visible preview
  const canvasRef = useRef<HTMLCanvasElement | null>(null); // offscreen for encoding
  const rafIdRef = useRef<number | null>(null);
  const pingTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastSentRef = useRef<number>(0);
  const clientId = useRef(
    `client_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`,
  );
  const retryCountRef = useRef(0);
  const MAX_RETRIES = 3;
  const TARGET_FPS = 10; // ~10fps upstream

  // Expose a hard disconnect to parent
  const forceDisconnect = useCallback(() => {
    setError(null);
    stopCamera();
    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch { }
      wsRef.current = null;
    }
    setIsConnected(false);
    setIsConnecting(false);
    setIsLoading(false);
    retryCountRef.current = 0;
    setAnalysisData({});
  }, []);

  useImperativeHandle(ref, () => ({ forceDisconnect }), [forceDisconnect]);

  const clearPing = () => {
    if (pingTimerRef.current) {
      clearInterval(pingTimerRef.current);
      pingTimerRef.current = null;
    }
  };
  const startPing = () => {
    clearPing();
    pingTimerRef.current = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ping" }));
      }
    }, 15000);
  };

  const stopCamera = useCallback(() => {
    if (rafIdRef.current !== null) {
      cancelAnimationFrame(rafIdRef.current);
      rafIdRef.current = null;
    }
    if (videoRef.current) {
      try {
        videoRef.current.pause();
        videoRef.current.srcObject = null;
      } catch { }
    }
    if (streamRef.current) {
      try {
        streamRef.current.getTracks().forEach((t) => t.stop());
      } catch { }
    }
    streamRef.current = null;
    setCameraStarted(false);
  }, []);

  const frameLoop = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      rafIdRef.current = null;
      return;
    }

    const now = performance.now();
    const minInterval = 1000 / TARGET_FPS;
    if (now - lastSentRef.current < minInterval) {
      rafIdRef.current = requestAnimationFrame(frameLoop);
      return;
    }

    const video = videoRef.current;
    let canvas = canvasRef.current;
    if (!video || video.readyState < 2) {
      rafIdRef.current = requestAnimationFrame(frameLoop);
      return;
    }
    if (!canvas) {
      canvas = document.createElement("canvas");
      canvasRef.current = canvas;
    }
    const w = video.videoWidth || 640;
    const h = video.videoHeight || 480;
    if (canvas.width !== w) canvas.width = w;
    if (canvas.height !== h) canvas.height = h;

    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    if (ctx) {
      ctx.drawImage(video, 0, 0, w, h);
      try {
        const frameData = canvas.toDataURL("image/jpeg", 0.7);
        wsRef.current.send(
          JSON.stringify({
            type: "video_frame",
            data: {
              image: frameData,
              timestamp: Date.now(),
              client_id: clientId.current,
            },
          }),
        );
        lastSentRef.current = now;
      } catch { }
    }
    rafIdRef.current = requestAnimationFrame(frameLoop);
  }, []);

  const startCamera = useCallback(async () => {
    if (cameraStarted) return;
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user",
        },
        audio: false,
      });

      if (!videoRef.current) {
        setError("Video element not ready.");
        return;
      }
      videoRef.current.autoplay = true;
      videoRef.current.muted = true;
      videoRef.current.playsInline = true;
      videoRef.current.srcObject = stream;
      await videoRef.current.play();

      streamRef.current = stream;
      setCameraStarted(true);
      rafIdRef.current = requestAnimationFrame(frameLoop);
    } catch (err) {
      console.error("Camera error:", err);
      setError(
        "Failed to access camera. Please allow permissions and try again.",
      );
      stopCamera();
    }
  }, [cameraStarted, frameLoop, stopCamera]);

  const connectWebSocket = useCallback(() => {
    if (isConnecting || isConnected || wsRef.current) return;

    setIsConnecting(true);
    setIsLoading(true);
    setError(null);

    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api/v1";
    const wsProtocol = baseUrl.startsWith("https") ? "wss" : "ws";
    const wsUrl = baseUrl.replace(/^https?:\/\//, `${wsProtocol}://`) + `/face-detection/ws/${clientId.current}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      wsRef.current = ws;
      setIsConnecting(false);
      setIsLoading(false);
      setIsConnected(true);
      retryCountRef.current = 0;
      startPing();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "analysis_result") {
          const newAnalysis: AnalysisData = data.data?.analysis ?? {};
          setAnalysisData(newAnalysis);
          onAnalysisDataChange?.(newAnalysis);
        } else if (data.type === "error") {
          setError(data.message || "Face detection error");
        }
      } catch (e) {
        console.error("WS parse error:", e);
      }
    };

    ws.onerror = () => {
      setError("Failed to connect to face detection service.");
    };

    ws.onclose = () => {
      clearPing();
      setIsConnected(false);
      setIsConnecting(false);
      setIsLoading(false);
      wsRef.current = null;
      stopCamera();
      setCameraStarted(false);

      if (isActive && retryCountRef.current < MAX_RETRIES) {
        retryCountRef.current += 1;
        setTimeout(() => {
          connectWebSocket();
        }, 1500);
      } else if (isActive && retryCountRef.current >= MAX_RETRIES) {
        setError("Unable to connect after multiple attempts.");
      }
    };
  }, [isActive, isConnecting, isConnected, onAnalysisDataChange, stopCamera]);

  // Lifecycle: connect/disconnect WS
  useEffect(() => {
    if (isActive) {
      connectWebSocket();
    } else {
      forceDisconnect();
    }
    return () => {
      forceDisconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isActive]);

  // Start/stop camera based on prop + connection
  useEffect(() => {
    if (shouldStartCamera && isConnected && !cameraStarted) {
      startCamera();
    } else if ((!shouldStartCamera || !isConnected) && cameraStarted) {
      stopCamera();
    }
  }, [shouldStartCamera, isConnected, cameraStarted, startCamera, stopCamera]);

  // UI helpers
  const getEmotionColor = (emotion?: string) => {
    switch ((emotion || "").toLowerCase()) {
      case "happy":
        return "bg-green-100 text-green-800";
      case "sad":
        return "bg-blue-100 text-blue-800";
      case "angry":
        return "bg-red-100 text-red-800";
      case "neutral":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };
  const getEyeStateColor = (eyeState?: string) => {
    switch ((eyeState || "").toLowerCase()) {
      case "open":
        return "bg-green-100 text-green-800";
      case "closed":
        return "bg-red-100 text-red-800";
      case "blinking":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };
  const getEngagementColor = (level?: string) => {
    switch ((level || "").toLowerCase()) {
      case "high":
        return "bg-green-100 text-green-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "low":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <AnimatePresence>
      {isActive && (
        <motion.div
          initial={{ opacity: 0, x: 300 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 300 }}
          transition={{ duration: 0.25 }}
          className={`fixed right-2 sm:right-4 top-2 sm:top-4 bottom-2 sm:bottom-auto w-[calc(100%-1rem)] sm:w-80 max-w-sm z-50 ${className}`}
        >
          <Card className="shadow-lg border-2 h-full sm:h-auto flex flex-col max-h-[calc(100vh-1rem)] sm:max-h-none">
            <CardHeader className="pb-2 sm:pb-3 p-3 sm:p-6">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-1.5 sm:gap-2 text-sm sm:text-lg">
                  <Camera size={16} className="sm:w-5 sm:h-5" />
                  Face Analysis
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onToggle}
                  className="h-7 w-7 sm:h-8 sm:w-8 p-0"
                >
                  <X size={14} className="sm:w-4 sm:h-4" />
                </Button>
              </div>
            </CardHeader>

            <CardContent className="space-y-2 sm:space-y-4 p-3 sm:p-6 pt-0 overflow-y-auto flex-1">
              {/* Connection Status */}
              <div className="flex items-center gap-1.5 sm:gap-2">
                <div
                  className={`w-2 h-2 sm:w-3 sm:h-3 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`}
                />
                <span className="text-xs sm:text-sm font-medium">
                  {isConnected ? "Connected" : "Disconnected"}
                </span>
                {isLoading && (
                  <span className="text-xs sm:text-sm text-muted-foreground">
                    Connecting...
                  </span>
                )}
              </div>

              {/* Error */}
              {error && (
                <Alert variant="destructive" className="p-2 sm:p-3">
                  <Warning size={14} className="sm:w-4 sm:h-4" />
                  <AlertDescription className="text-xs sm:text-sm break-words">{error}</AlertDescription>
                </Alert>
              )}

              {/* Visible Camera Preview */}
              <div className="relative">
                <video
                  ref={videoRef}
                  className="w-full h-32 sm:h-48 object-cover rounded-lg border bg-black"
                  playsInline
                  muted
                  autoPlay
                />
                {cameraStarted && analysisData.face_detected === false && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/40 rounded-lg">
                    <div className="text-white text-xs">No face detected</div>
                  </div>
                )}
                {!cameraStarted && !error && (
                  <div className="absolute inset-0 flex items-center justify-center text-white/80 text-xs sm:text-sm px-2 text-center">
                    {isConnected
                      ? "Camera not started yet…"
                      : "Waiting for connection…"}
                  </div>
                )}
              </div>

              {/* Analysis */}
              {Object.keys(analysisData).length > 0 && (
                <div className="space-y-2 sm:space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs sm:text-sm font-medium">Face Detected:</span>
                    <Badge
                      variant={
                        analysisData.face_detected ? "default" : "secondary"
                      }
                      className="text-xs px-1.5 py-0.5"
                    >
                      {analysisData.face_detected ? "Yes" : "No"}
                    </Badge>
                  </div>

                  {analysisData.emotion && (
                    <div className="flex items-center justify-between">
                      <span className="text-xs sm:text-sm font-medium flex items-center gap-1">
                        <Smiley size={12} className="sm:w-4 sm:h-4" />
                        Emotion:
                      </span>
                      <Badge className={`${getEmotionColor(analysisData.emotion)} text-xs px-1.5 py-0.5`}>
                        {analysisData.emotion}
                      </Badge>
                    </div>
                  )}

                  {analysisData.eye_state && (
                    <div className="flex items-center justify-between">
                      <span className="text-xs sm:text-sm font-medium flex items-center gap-1">
                        <Eye size={12} className="sm:w-4 sm:h-4" />
                        Eye State:
                      </span>
                      <Badge
                        className={`${getEyeStateColor(analysisData.eye_state)} text-xs px-1.5 py-0.5`}
                      >
                        {analysisData.eye_state}
                      </Badge>
                    </div>
                  )}

                  {analysisData.engagement_level && (
                    <div className="flex items-center justify-between">
                      <span className="text-xs sm:text-sm font-medium">Engagement:</span>
                      <Badge
                        className={`${getEngagementColor(analysisData.engagement_level)} text-xs px-1.5 py-0.5`}
                      >
                        {analysisData.engagement_level}
                      </Badge>
                    </div>
                  )}

                  {typeof analysisData.confidence === "number" && (
                    <div className="flex items-center justify-between">
                      <span className="text-xs sm:text-sm font-medium">Confidence:</span>
                      <span className="text-xs sm:text-sm text-muted-foreground">
                        {Math.round(analysisData.confidence * 100)}%
                      </span>
                    </div>
                  )}

                  {typeof analysisData.attention_score === "number" && (
                    <div className="flex items-center justify-between">
                      <span className="text-xs sm:text-sm font-medium">Attention:</span>
                      <span className="text-xs sm:text-sm text-muted-foreground">
                        {Math.round(analysisData.attention_score * 100)}%
                      </span>
                    </div>
                  )}

                  {/* Enhanced */}
                  <div className="border-t pt-2 sm:pt-3 mt-2 sm:mt-3">
                    <h4 className="text-xs sm:text-sm font-medium mb-1.5 sm:mb-2 text-blue-600">
                      Enhanced Analysis
                    </h4>

                    {analysisData.eye_tracking && (
                      <div className="space-y-1.5 sm:space-y-2 mb-2 sm:mb-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium">
                            Eye Tracking:
                          </span>
                          <Badge
                            variant={
                              analysisData.eye_tracking.eye_tracking ===
                                "looking_at_screen"
                                ? "default"
                                : "secondary"
                            }
                            className="text-xs px-1.5 py-0.5"
                          >
                            {analysisData.eye_tracking.eye_tracking ||
                              "unknown"}
                          </Badge>
                        </div>
                        {typeof analysisData.eye_tracking.eye_aspect_ratio ===
                          "number" && (
                            <div className="flex items-center justify-between">
                              <span className="text-xs">Eye Aspect Ratio:</span>
                              <span className="text-xs text-muted-foreground">
                                {analysisData.eye_tracking.eye_aspect_ratio.toFixed(
                                  3,
                                )}
                              </span>
                            </div>
                          )}
                      </div>
                    )}

                    {analysisData.head_pose && (
                      <div className="space-y-1.5 sm:space-y-2 mb-2 sm:mb-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium">
                            Head Pose:
                          </span>
                          <Badge
                            variant={
                              analysisData.head_pose.looking_at_screen
                                ? "default"
                                : "secondary"
                            }
                            className="text-xs px-1.5 py-0.5"
                          >
                            {analysisData.head_pose.head_pose || "unknown"}
                          </Badge>
                        </div>
                        {typeof analysisData.head_pose.gaze_distance ===
                          "number" && (
                            <div className="flex items-center justify-between">
                              <span className="text-xs">Gaze Distance:</span>
                              <span className="text-xs text-muted-foreground">
                                {Math.round(analysisData.head_pose.gaze_distance)}
                                px
                              </span>
                            </div>
                          )}
                      </div>
                    )}

                    {analysisData.multiple_faces && (
                      <div className="space-y-1.5 sm:space-y-2 mb-2 sm:mb-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium">
                            Face Count:
                          </span>
                          <Badge
                            variant={
                              analysisData.multiple_faces
                                .multiple_faces_detected
                                ? "destructive"
                                : "default"
                            }
                            className="text-xs px-1.5 py-0.5"
                          >
                            {analysisData.multiple_faces.face_count || 0}
                          </Badge>
                        </div>
                        {analysisData.multiple_faces
                          .multiple_faces_detected && (
                            <div className="text-xs text-red-600">
                              ⚠️ Multiple people detected
                            </div>
                          )}
                      </div>
                    )}

                    {analysisData.mobile_devices && (
                      <div className="space-y-1.5 sm:space-y-2 mb-2 sm:mb-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium">
                            Mobile devices:
                          </span>
                          <Badge
                            variant={
                              analysisData.mobile_devices
                                .mobile_devices_detected
                                ? "destructive"
                                : "default"
                            }
                            className="text-xs px-1.5 py-0.5"
                          >
                            {analysisData.mobile_devices.device_count ?? 0}
                          </Badge>
                        </div>
                        {analysisData.mobile_devices
                          .mobile_devices_detected && (
                            <div className="text-xs text-red-600">
                              ⚠️ Phone or device in view
                            </div>
                          )}
                      </div>
                    )}




                    {analysisData.voice_analysis && (
                      <div className="space-y-1.5 sm:space-y-2 mb-2 sm:mb-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium">Voice:</span>
                          <Badge
                            variant={
                              analysisData.voice_analysis.speaking
                                ? "default"
                                : "secondary"
                            }
                            className="text-xs px-1.5 py-0.5"
                          >
                            {analysisData.voice_analysis.speaking
                              ? "Speaking"
                              : "Silent"}
                          </Badge>
                        </div>
                        {typeof analysisData.voice_analysis.confidence ===
                          "number" && (
                            <div className="flex items-center justify-between">
                              <span className="text-xs">Confidence:</span>
                              <span className="text-xs text-muted-foreground">
                                {Math.round(
                                  analysisData.voice_analysis.confidence * 100,
                                )}
                                %
                              </span>
                            </div>
                          )}
                        {typeof analysisData.voice_analysis.nervousness ===
                          "number" && (
                            <div className="flex items-center justify-between">
                              <span className="text-xs">Nervousness:</span>
                              <span className="text-xs text-muted-foreground">
                                {Math.round(
                                  analysisData.voice_analysis.nervousness * 100,
                                )}
                                %
                              </span>
                            </div>
                          )}
                      </div>
                    )}
                  </div>

                  {/* Recommendations */}
                  {analysisData.recommendations &&
                    analysisData.recommendations.length > 0 && (
                      <div className="mt-2 sm:mt-3">
                        <h4 className="text-xs sm:text-sm font-medium mb-1.5 sm:mb-2">
                          Recommendations:
                        </h4>
                        <ul className="text-xs text-muted-foreground space-y-0.5 sm:space-y-1">
                          {analysisData.recommendations.map((rec, i) => (
                            <li key={i} className="flex items-start gap-1 break-words">
                              <span className="text-blue-500 shrink-0">•</span>
                              <span className="flex-1">{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                  {/* Suspicious Behavior */}
                  {analysisData.suspicious_behavior &&
                    analysisData.suspicious_behavior.length > 0 && (
                      <div className="mt-2 sm:mt-3">
                        <h4 className="text-xs sm:text-sm font-medium mb-1.5 sm:mb-2 text-red-600">
                          ⚠️ Suspicious Behavior:
                        </h4>
                        <ul className="text-xs text-red-600 space-y-0.5 sm:space-y-1">
                          {analysisData.suspicious_behavior.map((b, i) => (
                            <li key={i} className="flex items-start gap-1 break-words">
                              <span className="text-red-500 shrink-0">⚠</span>
                              <span className="flex-1">{b}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  );
});
