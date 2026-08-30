"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { StatusChip } from "@/components/admin/premium/status-chip";
import { ScoreRing } from "@/components/admin/premium/score-ring";
import {
  ArrowLeft,
  AlertCircle,
  Calendar,
  Clock,
  User,
  FileText,
  BarChart3,
  Video,
  Activity,
  Sparkles,
} from "lucide-react";
import { Interview, Evaluation } from "@/types/admin";
import { formatDistanceToNow } from "@/lib/date-utils";
import { cn } from "@/lib/utils";

export default function InterviewDetailPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.session_id as string;
  
  const [interview, setInterview] = useState<Interview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (sessionId) {
      loadInterviewDetails();
    }
  }, [sessionId]);

  const loadInterviewDetails = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getInterviewDetails(sessionId);
      setInterview(data as Interview);
      setError("");
    } catch (err) {
      console.error("Error loading interview details:", err);
      setError(err instanceof Error ? err.message : "Failed to load interview details");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading interview details...</p>
        </div>
      </div>
    );
  }

  if (error || !interview) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="w-full max-w-md border-border/50 bg-card/50 backdrop-blur-sm">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
              <p className="text-foreground mb-4">{error || "Interview not found"}</p>
              <Button onClick={() => router.push("/admin/interviews")} variant="outline">
                Back to Interviews
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const evaluation = interview.evaluation;
  const recommendation = evaluation?.recommendation || 'maybe';

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Button onClick={() => router.back()} variant="ghost" className="mb-2">
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back
      </Button>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">Interview Details</h1>
          <p className="text-muted-foreground mt-2">
            Session: {sessionId}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <StatusChip status={interview.status} />
          {interview.risk_flags && interview.risk_flags.length > 0 && (
            <Badge variant="destructive" className="gap-1">
              <AlertCircle className="h-3 w-3" />
              {interview.risk_flags.length} flag{interview.risk_flags.length > 1 ? 's' : ''}
            </Badge>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-muted-foreground">Overall Score</p>
              <ScoreRing score={interview.percentage || 0} size="sm" />
            </div>
            <p className="text-3xl font-bold">{interview.percentage?.toFixed(1) || 0}%</p>
          </CardContent>
        </Card>
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-6">
            <p className="text-sm font-medium text-muted-foreground mb-2">Recommendation</p>
            <StatusChip status={recommendation} size="lg" />
          </CardContent>
        </Card>
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <p className="text-sm font-medium text-muted-foreground">Duration</p>
            </div>
            <p className="text-3xl font-bold">{interview.duration_minutes || 0}min</p>
          </CardContent>
        </Card>
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <p className="text-sm font-medium text-muted-foreground">Date</p>
            </div>
            <p className="text-sm font-medium">
              {formatDistanceToNow(new Date(interview.created_at), { addSuffix: true })}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Rubric Breakdown */}
      {evaluation && evaluation.rubric_breakdown && evaluation.rubric_breakdown.length > 0 && (
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Rubric Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {evaluation.rubric_breakdown.map((rubric, index) => (
                <div key={index} className="p-4 border border-border/50 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium">{rubric.criterion}</p>
                    <Badge variant="outline">
                      {rubric.score}/{rubric.max_score}
                    </Badge>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden mb-2">
                    <div
                      className="h-full bg-primary transition-all"
                      style={{ width: `${(rubric.score / rubric.max_score) * 100}%` }}
                    />
                  </div>
                  <p className="text-sm text-muted-foreground">{rubric.feedback}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Tabs defaultValue="transcript" className="space-y-4">
        <TabsList className="bg-muted/50">
          <TabsTrigger value="transcript">
            <FileText className="h-4 w-4 mr-2" />
            Transcript
          </TabsTrigger>
          <TabsTrigger value="evaluation">
            <BarChart3 className="h-4 w-4 mr-2" />
            Evaluation
          </TabsTrigger>
          <TabsTrigger value="events">
            <Activity className="h-4 w-4 mr-2" />
            Events/Logs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="transcript" className="space-y-4">
          <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-lg font-semibold">Interview Transcript</CardTitle>
            </CardHeader>
            <CardContent>
              {interview.transcript && interview.transcript.length > 0 ? (
                <div className="space-y-4">
                  {interview.transcript.map((segment, index) => (
                    <div
                      key={index}
                      className={cn(
                        "p-4 rounded-xl border",
                        segment.speaker === 'interviewer'
                          ? "bg-primary/5 border-primary/20 ml-8"
                          : "bg-muted/30 border-border/50 mr-8"
                      )}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {segment.speaker === 'interviewer' ? (
                            <User className="h-4 w-4 text-primary" />
                          ) : (
                            <User className="h-4 w-4 text-muted-foreground" />
                          )}
                          <span className="text-xs font-medium capitalize">{segment.speaker}</span>
                        </div>
                        <span className="text-xs text-muted-foreground">{segment.timestamp}</span>
                      </div>
                      <p className="text-sm">{segment.text}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  No transcript available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="evaluation" className="space-y-4">
          {evaluation && (
            <>
              <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold">Detailed Evaluation</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {evaluation.strengths && evaluation.strengths.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-green-500 mb-2">Strengths</p>
                      <ul className="space-y-1">
                        {evaluation.strengths.map((strength, index) => (
                          <li key={index} className="text-sm flex items-start gap-2">
                            <span className="text-green-500 mt-1">•</span>
                            <span>{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {evaluation.weaknesses && evaluation.weaknesses.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-red-500 mb-2">Weaknesses</p>
                      <ul className="space-y-1">
                        {evaluation.weaknesses.map((weakness, index) => (
                          <li key={index} className="text-sm flex items-start gap-2">
                            <span className="text-red-500 mt-1">•</span>
                            <span>{weakness}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {evaluation.suspicious_patterns && evaluation.suspicious_patterns.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-yellow-500 mb-2 flex items-center gap-2">
                        <AlertCircle className="h-4 w-4" />
                        Suspicious Patterns
                      </p>
                      <ul className="space-y-1">
                        {evaluation.suspicious_patterns.map((pattern, index) => (
                          <li key={index} className="text-sm flex items-start gap-2">
                            <span className="text-yellow-500 mt-1">•</span>
                            <span>{pattern}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="events" className="space-y-4">
          <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-lg font-semibold">System Events & Logs</CardTitle>
            </CardHeader>
            <CardContent>
              {interview.events && interview.events.length > 0 ? (
                <div className="space-y-3">
                  {interview.events.map((event) => (
                    <div key={event.id} className="p-3 border border-border/50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium">{event.description}</p>
                        <span className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1 capitalize">
                        {event.type.replace('_', ' ')}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  No events logged
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* AI Insights */}
      {evaluation && (
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm border-primary/20">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg font-semibold">AI Insights</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium mb-2">Recommendation</p>
              <StatusChip status={recommendation} size="lg" />
            </div>
            {evaluation.strengths && evaluation.strengths.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">Key Strengths</p>
                <div className="flex flex-wrap gap-2">
                  {evaluation.strengths.slice(0, 3).map((strength, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {strength}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {evaluation.weaknesses && evaluation.weaknesses.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">Areas to Improve</p>
                <div className="flex flex-wrap gap-2">
                  {evaluation.weaknesses.slice(0, 3).map((weakness, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {weakness}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
