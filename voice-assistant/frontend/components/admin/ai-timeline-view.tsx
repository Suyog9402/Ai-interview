"use client";

import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, TrendingUp, TrendingDown, Award, Calendar } from "lucide-react";

interface AITimelineViewProps {
  interviewHistory: any[];
  userId: number;
}

export function AITimelineView({ interviewHistory, userId }: AITimelineViewProps) {
  const router = useRouter();

  if (!interviewHistory || interviewHistory.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">No interview history available</p>
        </CardContent>
      </Card>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Interview History
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {interviewHistory.map((interview, index) => {
            const interviewNum = interviewHistory.length - index;
            const score = interview.percentage || 0;
            const isBest = score === Math.max(...interviewHistory.map((i: any) => i.percentage || 0));
            const prevScore = index < interviewHistory.length - 1 
              ? interviewHistory[index + 1].percentage || 0 
              : null;
            const trend = prevScore !== null ? score - prevScore : 0;
            const interviewDate = interview.created_at 
              ? new Date(interview.created_at).toLocaleDateString()
              : "";

            return (
              <div
                key={interview.session_id}
                className="p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                onClick={() => router.push(`/admin/interviews/${interview.session_id}`)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-medium">Interview #{interviewNum}</span>
                      {isBest && (
                        <Badge variant="default">
                          <Award className="h-3 w-3 mr-1" />
                          Best Score
                        </Badge>
                      )}
                      {interviewDate && (
                        <span className="text-sm text-muted-foreground flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {interviewDate}
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-4 mb-2">
                      <span className={`text-2xl font-bold ${getScoreColor(score)}`}>
                        {score.toFixed(1)}%
                      </span>
                      {trend !== 0 && (
                        <div className={`flex items-center gap-1 text-sm ${
                          trend > 0 ? "text-green-600" : "text-red-600"
                        }`}>
                          {trend > 0 ? (
                            <TrendingUp className="h-4 w-4" />
                          ) : (
                            <TrendingDown className="h-4 w-4" />
                          )}
                          {Math.abs(trend).toFixed(1)}%
                        </div>
                      )}
                    </div>

                    {interview.detailed_feedback && interview.detailed_feedback.length > 0 && (
                      <div className="text-sm text-muted-foreground mb-2">
                        {interview.detailed_feedback.length} questions evaluated
                      </div>
                    )}

                    {interview.overall_analysis && (
                      <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
                        {interview.overall_analysis.substring(0, 150)}...
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

