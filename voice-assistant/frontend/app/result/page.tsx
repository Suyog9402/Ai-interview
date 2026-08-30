"use client";

import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "next/navigation";

interface FaceAnalysisData {
  emotion?: string;
  eye_state?: string;
  face_detected?: boolean;
  confidence?: number;
  attention_score?: number;
  engagement_level?: string;
  recommendations?: string[];
  suspicious_behavior?: string[];
}

export interface InterviewResult {
  session_id: string;
  user_id: number;
  total_score: number;
  max_score: number;
  percentage?: number; // optional on some APIs; we compute anyway
  questions_evaluated: number;
  overall_analysis: string;
  detailed_feedback: Array<{
    question: string;
    answer: string;
    score: number; // 0..100
    feedback: string;
    strengths: string[];
    weaknesses: string[];
  }>;
  strengths: string[];
  areas_for_improvement: string[];
  recommendations: string[];
  transcript?: Array<{
    role: string; // "user" | "assistant"
    content: string;
    timestamp?: string;
  }>;
  face_analysis?: {
    face_detected: boolean;
    face_count: number;
    confidence: number;
    attention_score: number;
    engagement_level: string;
    eye_tracking?: {
      eye_state: string;
      eye_tracking: string;
      eye_aspect_ratio: number;
      screen_distance: number;
    };
    head_pose?: {
      looking_at_screen: boolean;
      head_pose: string;
      gaze_distance: number;
    };
    multiple_faces?: {
      face_count: number;
      multiple_faces_detected: boolean;
    };
    screen_sharing?: {
      screen_sharing_detected: boolean;
      time_since_last_activity: number;
      switching_reason?: string[];
    };
    suspicious_behavior: string[];
    recommendations: string[];
    mobile_devices?: {
      mobile_devices_detected: boolean;
      device_count: number;
      devices?: Array<{
        type: string;
        confidence: number;
      }>;
    };
    suspicious_objects?: {
      suspicious_objects_detected: boolean;
      object_count: number;
      objects?: Array<{
        type: string;
        confidence: number;
      }>;
    };
  };
  voice_analysis?: {
    speaking: boolean;
    confidence: number; // 0..1
    nervousness: number; // 0..1
    speech_patterns: string[];
    // optional extended fields if backend supplies them
    voice_quality?: number; // 0..1
    speech_rate?: number; // WPM
    volume_level?: number; // 0..1
  };
  created_at: string;
  updated_at: string;
}

export default function ResultPage() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("sessionId");

  const [result, setResult] = useState<InterviewResult | null>(null);
  const [faceAnalysisData, setFaceAnalysisData] =
    useState<FaceAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);

  // Compute + guards
  const calculatePercentage = (score: number = 0, maxScore: number = 1) => {
    if (!maxScore) return 0;
    return (score / maxScore) * 100;
  };
  const getScoreColor = (pct?: number) => {
    if (pct === undefined) return "text-gray-600";
    if (pct >= 80) return "text-green-600";
    if (pct >= 60) return "text-yellow-600";
    return "text-red-600";
  };
  const getScoreLabel = (pct?: number) => {
    if (pct === undefined) return "Not Available";
    if (pct >= 90) return "Exceptional";
    if (pct >= 80) return "Excellent";
    if (pct >= 70) return "Good";
    if (pct >= 60) return "Satisfactory";
    if (pct >= 50) return "Needs Improvement";
    return "Poor";
  };

  // Fetch interview result from API (by sessionId or latest)
  const fetchInterviewResult = useCallback(async () => {
    setLoading(true);
    try {
      const url = sessionId
        ? `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api/v1"}/interview/${sessionId}`
        : `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api/v1"}/interview/history/latest`;

      const res = await fetch(url, { credentials: "include" });
      if (res.ok) {
        const data = await res.json();
        const normalized: InterviewResult = Array.isArray(data)
          ? data[0]
          : data;

        if (normalized) {
          // ensure percentage
          const pct =
            normalized.percentage ??
            calculatePercentage(normalized.total_score, normalized.max_score);

          const merged = { ...normalized, percentage: pct };
          setResult(merged);
          // cache
          if (merged.session_id) {
            localStorage.setItem(
              `interview_result_${merged.session_id}`,
              JSON.stringify(merged),
            );
            localStorage.setItem("latest_interview_session", merged.session_id);
          }
        } else {
          setResult(null);
        }
      } else {
        // fallback to localStorage latest if API fails
        const latest = localStorage.getItem("latest_interview_session");
        if (latest) {
          const cached = localStorage.getItem(`interview_result_${latest}`);
          if (cached) setResult(JSON.parse(cached));
        }
      }
    } catch (e) {
      console.error("Error fetching interview result:", e);
      // fallback to any cached
      const latest = localStorage.getItem("latest_interview_session");
      if (latest) {
        const cached = localStorage.getItem(`interview_result_${latest}`);
        if (cached) setResult(JSON.parse(cached));
      }
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    fetchInterviewResult();
  }, [fetchInterviewResult]);

  // Extract light face analysis view model (used at top, optional)
  useEffect(() => {
    if (result?.face_analysis) {
      setFaceAnalysisData({
        eye_state: result.face_analysis.eye_tracking?.eye_state,
        face_detected: result.face_analysis.face_detected,
        confidence: result.face_analysis.confidence,
        attention_score: result.face_analysis.attention_score,
        engagement_level: result.face_analysis.engagement_level,
        recommendations: result.face_analysis.recommendations || [],
        suspicious_behavior: result.face_analysis.suspicious_behavior || [],
      });
    } else {
      setFaceAnalysisData(null);
    }
  }, [result]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Analyzing your interview...</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center p-8">
        <div className="w-full max-w-2xl bg-card rounded-lg shadow-lg p-8 text-center">
          <h1 className="text-3xl font-bold mb-4">No Interview Results</h1>
          <p className="text-muted-foreground mb-6">
            No interview results found. Please complete an interview first.
          </p>
          <a
            href="/interview"
            className="bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:bg-primary/90 transition-colors"
          >
            Start Interview
          </a>
        </div>
      </div>
    );
  }

  const percentage =
    result.percentage ??
    calculatePercentage(result.total_score, result.max_score);

  const strengths = result.strengths ?? [];
  const areasForImprovement = result.areas_for_improvement ?? [];
  const detailedFeedback = result.detailed_feedback ?? [];
  const recommendations = result.recommendations ?? [];
  const hasFaceAnalysis = result.face_analysis != null;
  const hasVoiceAnalysis = result.voice_analysis != null;

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="bg-card rounded-lg shadow-lg p-8 text-center">
          <h1 className="text-4xl font-bold mb-4">Interview Results</h1>
          <div className="flex items-center justify-center space-x-4 mb-6">
            <div className={`text-6xl font-bold ${getScoreColor(percentage)}`}>
              {result.total_score}/{result.max_score}
            </div>
            <div className="text-left">
              <div
                className={`text-2xl font-semibold ${getScoreColor(percentage)}`}
              >
                {percentage.toFixed(1)}%
              </div>
              <div className="text-lg text-muted-foreground">
                {getScoreLabel(percentage)}
              </div>
            </div>
          </div>
          <p className="text-muted-foreground">
            {result.questions_evaluated} questions evaluated
          </p>
        </div>

        {/* Analysis summary: one place for score + overall + face/voice highlights */}
        <div className="bg-card rounded-lg shadow-lg p-6 border-l-4 border-primary">
          <h2 className="text-xl font-bold mb-3">Analysis Summary</h2>
          <p className="text-muted-foreground mb-4 leading-relaxed">
            {result.overall_analysis || "No overall analysis available."}
          </p>
          <div className="flex flex-wrap gap-4 text-sm">
            <span className="font-medium">Score: {percentage.toFixed(1)}% ({getScoreLabel(percentage)})</span>
            <span className="text-muted-foreground">•</span>
            <span className="font-medium">{result.questions_evaluated} Q&A analyzed</span>
            {hasFaceAnalysis && (
              <>
                <span className="text-muted-foreground">•</span>
                <span>
                  Face: {result.face_analysis?.engagement_level ?? "—"} engagement
                  {typeof result.face_analysis?.attention_score === "number" &&
                    `, ${Math.round((result.face_analysis.attention_score ?? 0) * 100)}% attention`}
                </span>
              </>
            )}
            {hasVoiceAnalysis && (
              <>
                <span className="text-muted-foreground">•</span>
                <span>
                  Voice: {Math.round((result.voice_analysis?.confidence ?? 0) * 100)}% confidence
                  {typeof result.voice_analysis?.nervousness === "number" &&
                    `, ${Math.round((result.voice_analysis.nervousness ?? 0) * 100)}% nervousness`}
                </span>
              </>
            )}
          </div>
          <p className="text-xs text-muted-foreground mt-3">
            This report includes: overall score, per-question feedback, strengths &amp; improvements, recommendations
            {hasFaceAnalysis && ", face/engagement analysis"}
            {hasVoiceAnalysis && ", voice analysis"}.
          </p>
        </div>

        {/* Strengths and Areas for Improvement */}
        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-card rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-4 text-green-600">
              Strengths
            </h2>
            {strengths.length > 0 ? (
              <ul className="space-y-2">
                {strengths.map((strength, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    <span>{strength}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-muted-foreground">No specific strengths recorded in this analysis.</p>
            )}
          </div>

          <div className="bg-card rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-4 text-orange-600">
              Areas for Improvement
            </h2>
            {areasForImprovement.length > 0 ? (
              <ul className="space-y-2">
                {areasForImprovement.map((area, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-orange-500 mr-2">•</span>
                    <span>{area}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-muted-foreground">No specific areas for improvement recorded.</p>
            )}
          </div>
        </div>

        {/* Detailed Feedback — analysis for every question */}
        <div className="bg-card rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-6">Detailed Feedback</h2>
          <p className="text-muted-foreground mb-4">
            Per-question analysis for all {detailedFeedback.length} questions.
          </p>
          <div className="space-y-6">
            {detailedFeedback.length === 0 ? (
              <p className="text-muted-foreground">No per-question feedback available for this session.</p>
            ) : (
              detailedFeedback.map((feedback, idx) => {
                const fStrengths = feedback.strengths ?? [];
                const fWeaknesses = feedback.weaknesses ?? [];
                return (
                  <div key={idx} className="border rounded-lg p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-semibold">Question {idx + 1}</h3>
                      <div
                        className={`text-lg font-bold ${getScoreColor(feedback.score)}`}
                      >
                        {feedback.score}/100
                      </div>
                    </div>

                    <div className="mb-4">
                      <p className="font-medium mb-2 text-lg">Question:</p>
                      <p className="text-muted-foreground mb-4 p-3 bg-gray-50 rounded-lg border-l-4 border-blue-500">
                        {feedback.question || "No question provided"}
                      </p>

                      <p className="font-medium mb-2 text-lg">Your Answer:</p>
                      <p className={`text-muted-foreground mb-4 p-3 rounded-lg border-l-4 ${
                        feedback.answer && feedback.answer !== "No answer provided"
                          ? "bg-green-50 border-green-500"
                          : "bg-red-50 border-red-500"
                      }`}>
                        {feedback.answer || "No answer provided"}
                      </p>

                      <p className="font-medium mb-2 text-lg">Feedback:</p>
                      <p className="text-muted-foreground mb-4 p-3 bg-blue-50 rounded-lg border-l-4 border-purple-500">
                        {feedback.feedback || "No feedback for this question."}
                      </p>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium text-green-600 mb-2">
                          Strengths:
                        </h4>
                        {fStrengths.length > 0 ? (
                          <ul className="space-y-1">
                            {fStrengths.map((s, sIdx) => (
                              <li key={sIdx} className="text-sm text-muted-foreground">
                                • {s}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-sm text-muted-foreground">None noted.</p>
                        )}
                      </div>
                      <div>
                        <h4 className="font-medium text-orange-600 mb-2">
                          Weaknesses:
                        </h4>
                        {fWeaknesses.length > 0 ? (
                          <ul className="space-y-1">
                            {fWeaknesses.map((w, wIdx) => (
                              <li key={wIdx} className="text-sm text-muted-foreground">
                                • {w}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-sm text-muted-foreground">None noted.</p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Enhanced Face Analysis Results */}
        {result.face_analysis && (
          <div className="bg-card rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-6">
              Enhanced Face Analysis Results
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              {/* Face Detection */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Face Detection</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="font-medium">Face Detected:</span>
                    <span
                      className={
                        result.face_analysis.face_detected
                          ? "text-green-600"
                          : "text-red-600"
                      }
                    >
                      {result.face_analysis.face_detected ? "Yes" : "No"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Face Count:</span>
                    <span className="text-muted-foreground">
                      {result.face_analysis.face_count ?? 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Confidence:</span>
                    <span className="text-muted-foreground">
                      {Math.round((result.face_analysis.confidence ?? 0) * 100)}
                      %
                    </span>
                  </div>
                </div>
              </div>

              {/* Engagement */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Engagement Analysis</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="font-medium">Engagement Level:</span>
                    <span
                      className={`font-medium ${!result.face_analysis.engagement_level
                        ? "text-gray-600"
                        : result.face_analysis.engagement_level === "high"
                          ? "text-green-600"
                          : result.face_analysis.engagement_level === "medium"
                            ? "text-yellow-600"
                            : "text-red-600"
                        }`}
                    >
                      {result.face_analysis.engagement_level
                        ? result.face_analysis.engagement_level
                          .charAt(0)
                          .toUpperCase() +
                        result.face_analysis.engagement_level.slice(1)
                        : "N/A"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Attention Score:</span>
                    <span className="text-muted-foreground">
                      {Math.round(
                        (result.face_analysis.attention_score ?? 0) * 100,
                      )}
                      %
                    </span>
                  </div>
                </div>
              </div>

              {/* Eye Tracking */}
              {result.face_analysis.eye_tracking && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Eye Tracking</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="font-medium">Eye State:</span>
                      <span
                        className={`font-medium ${result.face_analysis.eye_tracking.eye_state === "open"
                          ? "text-green-600"
                          : result.face_analysis.eye_tracking.eye_state ===
                            "closed"
                            ? "text-red-600"
                            : "text-yellow-600"
                          }`}
                      >
                        {result.face_analysis.eye_tracking.eye_state
                          ? result.face_analysis.eye_tracking.eye_state
                            .charAt(0)
                            .toUpperCase() +
                          result.face_analysis.eye_tracking.eye_state.slice(1)
                          : "N/A"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Eye Tracking:</span>
                      <span
                        className={`font-medium ${result.face_analysis.eye_tracking.eye_tracking ===
                          "looking_at_screen"
                          ? "text-green-600"
                          : "text-red-600"
                          }`}
                      >
                        {result.face_analysis.eye_tracking.eye_tracking ===
                          "looking_at_screen"
                          ? "Looking at Screen"
                          : "Looking Away"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Eye Aspect Ratio:</span>
                      <span className="text-muted-foreground">
                        {typeof result.face_analysis.eye_tracking
                          .eye_aspect_ratio === "number"
                          ? result.face_analysis.eye_tracking.eye_aspect_ratio.toFixed(
                            3,
                          )
                          : "N/A"}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Head Pose */}
              {result.face_analysis.head_pose && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Head Pose</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="font-medium">Looking at Screen:</span>
                      <span
                        className={`font-medium ${result.face_analysis.head_pose.looking_at_screen
                          ? "text-green-600"
                          : "text-red-600"
                          }`}
                      >
                        {result.face_analysis.head_pose.looking_at_screen
                          ? "Yes"
                          : "No"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Head Pose:</span>
                      <span className="text-muted-foreground capitalize">
                        {result.face_analysis.head_pose.head_pose ?? "N/A"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Gaze Distance:</span>
                      <span className="text-muted-foreground">
                        {typeof result.face_analysis.head_pose.gaze_distance ===
                          "number"
                          ? `${Math.round(result.face_analysis.head_pose.gaze_distance)}px`
                          : "N/A"}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Multiple Faces */}
              {result.face_analysis.multiple_faces && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">
                    Multiple Face Detection
                  </h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="font-medium">Multiple Faces:</span>
                      <span
                        className={`font-medium ${result.face_analysis.multiple_faces
                          .multiple_faces_detected
                          ? "text-red-600"
                          : "text-green-600"
                          }`}
                      >
                        {result.face_analysis.multiple_faces
                          .multiple_faces_detected
                          ? "Detected"
                          : "None"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">Face Count:</span>
                      <span className="text-muted-foreground">
                        {result.face_analysis.multiple_faces.face_count ?? 0}
                      </span>
                    </div>
                  </div>
                </div>
              )}






            </div>

            {/* Suspicious Behavior */}
            {result.face_analysis.suspicious_behavior &&
              result.face_analysis.suspicious_behavior.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-red-600 mb-3">
                    ⚠️ Suspicious Behavior Detected
                  </h3>
                  <ul className="space-y-2">
                    {result.face_analysis.suspicious_behavior.map((b, i) => (
                      <li key={i} className="flex items-start">
                        <span className="text-red-500 mr-2 mt-1">⚠</span>
                        <span className="text-sm text-red-600">{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            {/* Face Recommendations */}
            {result.face_analysis.recommendations &&
              result.face_analysis.recommendations.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-3">
                    Face Analysis Recommendations
                  </h3>
                  <ul className="space-y-2">
                    {result.face_analysis.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start">
                        <span className="text-blue-500 mr-2 mt-1">•</span>
                        <span className="text-sm">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
          </div>
        )}

        {/* Voice Analysis Results */}
        {result.voice_analysis && (
          <div className="bg-card rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-6">Voice Analysis Results</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {/* Status */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Voice Status</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="font-medium">Speaking:</span>
                    <span
                      className={`font-medium ${result.voice_analysis.speaking ? "text-green-600" : "text-red-600"}`}
                    >
                      {result.voice_analysis.speaking ? "Yes" : "No"}
                    </span>
                  </div>
                  {"speech_rate" in result.voice_analysis && (
                    <div className="flex justify-between">
                      <span className="font-medium">Speech Rate:</span>
                      <span className="text-muted-foreground">
                        {Math.round(
                          (result.voice_analysis.speech_rate ?? 0) as number,
                        )}{" "}
                        WPM
                      </span>
                    </div>
                  )}
                  {"volume_level" in result.voice_analysis && (
                    <div className="flex justify-between">
                      <span className="font-medium">Volume Level:</span>
                      <span className="text-muted-foreground">
                        {Math.round(
                          (result.voice_analysis.volume_level ?? 0) * 100,
                        )}
                        %
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Quality / Affect */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Voice Quality</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="font-medium">Confidence:</span>
                    <span className="text-muted-foreground">
                      {Math.round(result.voice_analysis.confidence * 100)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Nervousness:</span>
                    <span
                      className={`font-medium ${result.voice_analysis.nervousness > 0.7
                        ? "text-red-600"
                        : result.voice_analysis.nervousness > 0.4
                          ? "text-yellow-600"
                          : "text-green-600"
                        }`}
                    >
                      {Math.round(result.voice_analysis.nervousness * 100)}%
                    </span>
                  </div>
                  {"voice_quality" in result.voice_analysis && (
                    <div className="flex justify-between">
                      <span className="font-medium">
                        Voice Quality (proxy):
                      </span>
                      <span className="text-muted-foreground">
                        {Math.round(
                          (result.voice_analysis.voice_quality ?? 0) * 100,
                        )}
                        %
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Patterns */}
              {result.voice_analysis.speech_patterns &&
                result.voice_analysis.speech_patterns.length > 0 && (
                  <div className="md:col-span-2 space-y-4">
                    <h3 className="text-lg font-semibold">Speech Patterns</h3>
                    <ul className="space-y-2">
                      {result.voice_analysis.speech_patterns.map((p, i) => (
                        <li key={i} className="flex items-start">
                          <span className="text-blue-500 mr-2 mt-1">•</span>
                          <span className="text-sm">{p}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
            </div>
          </div>
        )}

        {/* Global Recommendations */}
        <div className="bg-card rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-4">Recommendations</h2>
          {recommendations.length > 0 ? (
            <ul className="space-y-3">
              {recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-blue-500 mr-3 mt-1">→</span>
                  <span className="text-lg">{rec}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground">No specific recommendations for this session.</p>
          )}
        </div>

        {/* Actions */}
        <div className="bg-card rounded-lg shadow-lg p-8 text-center">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/interview"
              className="bg-primary text-primary-foreground px-8 py-3 rounded-lg hover:bg-primary/90 transition-colors"
            >
              Practice Again
            </a>
            <a
              href="/resume"
              className="bg-secondary text-secondary-foreground px-8 py-3 rounded-lg hover:bg-secondary/90 transition-colors"
            >
              Upload Resume
            </a>
            <a
              href="/jobs"
              className="bg-muted text-muted-foreground px-8 py-3 rounded-lg hover:bg-muted/90 transition-colors"
            >
              Back to Home
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
