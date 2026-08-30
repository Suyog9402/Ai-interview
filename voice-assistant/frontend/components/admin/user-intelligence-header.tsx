"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Brain, Zap, Shield, Calendar } from "lucide-react";

interface UserIntelligenceHeaderProps {
  userDetails: any;
}

export function UserIntelligenceHeader({ userDetails }: UserIntelligenceHeaderProps) {
  const aiMetrics = useMemo(() => {
    const avgScore = userDetails.average_score || 0;
    const latestScore = userDetails.latest_score || 0;
    const bestScore = userDetails.best_score || 0;
    const totalInterviews = userDetails.total_interviews || 0;

    // Confidence Index (0-1 scale)
    const confidenceIndex = avgScore / 100;
    
    // Learning Velocity (improvement trend)
    const improvement = latestScore - avgScore;
    const learningVelocity = totalInterviews > 1 ? (improvement / totalInterviews) * 10 : 0;
    
    // Consistency Score (variance-based)
    const variance = bestScore - (userDetails.interview_history?.[0]?.percentage || avgScore);
    const consistencyScore = Math.max(0, 1 - (variance / 100));

    // Risk Signals
    const riskLevel = avgScore < 40 ? "HIGH" : avgScore < 60 ? "MEDIUM" : "LOW";

    return {
      confidenceIndex,
      confidenceDelta: (latestScore - avgScore) / 100,
      learningVelocity,
      consistencyScore,
      riskLevel,
    };
  }, [userDetails]);

  const fullName = userDetails.full_name || userDetails.username || "Unknown";
  const lastInterview = userDetails.interview_history?.[0];
  const lastInterviewTime = lastInterview?.created_at 
    ? new Date(lastInterview.created_at).toLocaleString()
    : "Never";

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-2xl mb-2">{fullName}</CardTitle>
            <div className="flex items-center gap-4 text-sm text-muted-foreground mt-2">
              <div className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                <span>Joined {new Date(userDetails.created_at || Date.now()).toLocaleDateString()}</span>
              </div>
              <span>•</span>
              <span>Last interview: {lastInterviewTime}</span>
            </div>
          </div>
          <Badge variant={userDetails.is_active ? "default" : "secondary"}>
            {userDetails.is_active ? "Active" : "Inactive"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {/* AI Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Confidence Index */}
          <div className="p-4 border rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Brain className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Confidence Index</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">
                {aiMetrics.confidenceIndex.toFixed(2)}
              </span>
              {aiMetrics.confidenceDelta !== 0 && (
                <span className={`text-sm flex items-center gap-1 ${
                  aiMetrics.confidenceDelta > 0 ? "text-green-600" : "text-red-600"
                }`}>
                  {aiMetrics.confidenceDelta > 0 ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  {Math.abs(aiMetrics.confidenceDelta).toFixed(2)}
                </span>
              )}
            </div>
          </div>

          {/* Learning Velocity */}
          <div className="p-4 border rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Learning Velocity</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">
                {aiMetrics.learningVelocity > 0 ? "+" : ""}{aiMetrics.learningVelocity.toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Risk Signals */}
          <div className="p-4 border rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Risk Signals</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className={`text-2xl font-bold ${
                aiMetrics.riskLevel === "LOW" ? "text-green-600" :
                aiMetrics.riskLevel === "MEDIUM" ? "text-yellow-600" : "text-red-600"
              }`}>
                {aiMetrics.riskLevel}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

