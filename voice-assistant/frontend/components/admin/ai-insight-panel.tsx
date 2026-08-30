"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Lightbulb, TrendingUp, AlertTriangle, Target } from "lucide-react";

interface AIInsightPanelProps {
  userDetails: any;
}

export function AIInsightPanel({ userDetails }: AIInsightPanelProps) {
  const insights = useMemo(() => {
    const interviews = userDetails.interview_history || [];
    const avgScore = userDetails.average_score || 0;
    
    // Analyze weaknesses
    const allFeedback = interviews.flatMap((i: any) => i.detailed_feedback || []);
    const weaknessCounts: Record<string, number> = {};
    allFeedback.forEach((fb: any) => {
      (fb.weaknesses || []).forEach((w: string) => {
        weaknessCounts[w] = (weaknessCounts[w] || 0) + 1;
      });
    });
    const primaryWeakness = Object.entries(weaknessCounts)
      .sort(([, a], [, b]) => b - a)[0]?.[0] || "Explanation clarity";

    // Calculate improvement
    if (interviews.length < 2) return null;
    const recentScores = interviews.slice(0, 3).map((i: any) => i.percentage || 0);
    const olderScores = interviews.slice(-3).map((i: any) => i.percentage || 0);
    const recentAvg = recentScores.reduce((a, b) => a + b, 0) / recentScores.length;
    const olderAvg = olderScores.reduce((a, b) => a + b, 0) / olderScores.length;
    const improvement = recentAvg - olderAvg;

    // Find consistent drop point
    const q3Scores = allFeedback
      .filter((_: any, idx: number) => idx % 5 === 2) // Q3 indices
      .map((fb: any) => fb.score || 0);
    const avgQ3Score = q3Scores.length > 0 
      ? q3Scores.reduce((a: number, b: number) => a + b, 0) / q3Scores.length 
      : 0;
    const confidenceDrop = avgQ3Score < avgScore * 0.8;

    return {
      primaryWeakness,
      improvement,
      confidenceDrop,
      recommendedNext: "DSA + Verbal Reasoning",
    };
  }, [userDetails]);

  if (!insights) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">More interview data needed for insights</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="sticky top-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5" />
          Insights
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Primary Weakness */}
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <span className="text-xs font-semibold text-red-600 uppercase">Primary Weakness</span>
          </div>
          <p className="text-sm">{insights.primaryWeakness}</p>
        </div>

        {/* Improvement */}
        {insights.improvement > 0 && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="text-xs font-semibold text-green-600 uppercase">Strength Improved</span>
            </div>
            <p className="text-sm">
              Improved by <span className="font-bold text-green-600">{insights.improvement.toFixed(1)}%</span> in last 3 interviews
            </p>
          </div>
        )}

        {/* Confidence Drop */}
        {insights.confidenceDrop && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <span className="text-xs font-semibold text-yellow-600 uppercase">Pattern Detected</span>
            </div>
            <p className="text-sm">
              Confidence drops after Q3 consistently
            </p>
          </div>
        )}

        {/* Recommendation */}
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <Target className="h-4 w-4 text-blue-600" />
            <span className="text-xs font-semibold text-blue-600 uppercase">Recommended Next</span>
          </div>
          <p className="text-sm">{insights.recommendedNext}</p>
        </div>
      </CardContent>
    </Card>
  );
}

