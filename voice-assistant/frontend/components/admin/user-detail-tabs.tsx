"use client";

import * as React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  User,
  Calendar,
  TrendingUp,
  TrendingDown,
  Award,
  AlertCircle,
  CheckCircle,
  XCircle,
  FileText,
  BarChart2,
  Target,
  Lightbulb,
  MessageSquare,
  Download,
} from "lucide-react";
import { SkillRadarChart, SkillData } from "./skill-radar-chart";
import { ScoreProgressionChart } from "./score-progression-chart";

interface UserDetails {
  user_id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  total_interviews?: number;
  average_score?: number;
  best_score?: number;
  latest_score?: number;
  interview_history?: Array<{
    session_id: string;
    total_score: number;
    max_score: number;
    percentage: number;
    created_at: string | Date;
    detailed_feedback?: Array<{
      question: string;
      answer: string;
      score: number;
      feedback: string;
      strengths?: string[];
      weaknesses?: string[];
    }>;
  }>;
  progression?: Array<{
    date: string;
    score: number;
  }>;
  strengths?: string[];
  weaknesses?: string[];
  recommendations?: string[];
}

interface UserDetailTabsProps {
  userDetails: UserDetails;
  onClose?: () => void;
}

export function UserDetailTabs({ userDetails, onClose }: UserDetailTabsProps) {
  const [activeTab, setActiveTab] = React.useState("overview");

  // Calculate hire recommendation
  const getHireRecommendation = () => {
    const avgScore = userDetails.average_score || 0;
    const latestScore = userDetails.latest_score || 0;
    const bestScore = userDetails.best_score || 0;

    if (latestScore >= 75 && avgScore >= 70) {
      return { status: "Strong Hire", color: "text-green-600", variant: "default" as const };
    } else if (latestScore >= 65 || avgScore >= 65) {
      return { status: "Hire", color: "text-green-600", variant: "default" as const };
    } else if (latestScore >= 50 || avgScore >= 50) {
      return { status: "Borderline", color: "text-yellow-600", variant: "secondary" as const };
    } else {
      return { status: "No Hire", color: "text-red-600", variant: "destructive" as const };
    }
  };

  const getRiskLevel = () => {
    const avgScore = userDetails.average_score || 0;
    const latestScore = userDetails.latest_score || 0;
    const improvement = latestScore - avgScore;

    if (avgScore >= 75 && improvement >= 0) {
      return { level: "Low", color: "text-green-600" };
    } else if (avgScore >= 60 && improvement >= -5) {
      return { level: "Medium", color: "text-yellow-600" };
    } else {
      return { level: "High", color: "text-red-600" };
    }
  };

  // Calculate skill data (mock - in real implementation, extract from interview data)
  const calculateSkillData = (): SkillData => {
    const baseScore = userDetails.average_score || 70;
    // Distribute scores with some variance
    return {
      problemSolving: Math.min(100, baseScore + (Math.random() * 20 - 10)),
      systemDesign: Math.min(100, baseScore + (Math.random() * 20 - 10)),
      codingLogic: Math.min(100, baseScore + (Math.random() * 20 - 10)),
      communication: Math.min(100, baseScore + (Math.random() * 20 - 10)),
      depthOfKnowledge: Math.min(100, baseScore + (Math.random() * 20 - 10)),
      realWorldThinking: Math.min(100, baseScore + (Math.random() * 20 - 10)),
    };
  };

  const skillData = calculateSkillData();
  const hireRec = getHireRecommendation();
  const riskLevel = getRiskLevel();

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
      <TabsList className="grid w-full grid-cols-6">
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="skills">Skills</TabsTrigger>
        <TabsTrigger value="history">History</TabsTrigger>
        <TabsTrigger value="analytics">Analytics</TabsTrigger>
        <TabsTrigger value="comparison">Comparison</TabsTrigger>
        <TabsTrigger value="evidence">Evidence</TabsTrigger>
      </TabsList>

      {/* Overview Tab */}
      <TabsContent value="overview" className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* User Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                User Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Email</label>
                <p className="text-base">{userDetails.email}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Username</label>
                <p className="text-base">{userDetails.username}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Full Name</label>
                <p className="text-base">{userDetails.full_name || "Not provided"}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Status</label>
                <div className="mt-1">
                  <Badge variant={userDetails.is_active ? "default" : "secondary"}>
                    {userDetails.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Final Verdict */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Final Verdict
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Overall Score</label>
                <div className="text-3xl font-bold mt-1">
                  {userDetails.average_score?.toFixed(1) || "N/A"}%
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Hire Recommendation</label>
                <div className="mt-1">
                  <Badge variant={hireRec.variant} className="text-base px-3 py-1">
                    {hireRec.status}
                  </Badge>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">Risk Level</label>
                <div className="mt-1">
                  <Badge variant="outline" className={riskLevel.color}>
                    {riskLevel.level} Risk
                  </Badge>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="text-xs text-muted-foreground">Best Score</label>
                  <div className="text-lg font-semibold flex items-center gap-1">
                    <Award className="h-4 w-4 text-yellow-600" />
                    {userDetails.best_score?.toFixed(1) || "N/A"}%
                  </div>
                </div>
                <div>
                  <label className="text-xs text-muted-foreground">Latest Score</label>
                  <div className="text-lg font-semibold flex items-center gap-1">
                    {userDetails.latest_score && userDetails.average_score ? (
                      userDetails.latest_score > userDetails.average_score ? (
                        <TrendingUp className="h-4 w-4 text-green-600" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-red-600" />
                      )
                    ) : null}
                    {userDetails.latest_score?.toFixed(1) || "N/A"}%
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Stats */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold">{userDetails.total_interviews || 0}</div>
                <div className="text-sm text-muted-foreground mt-1">Total Interviews</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold">
                  {userDetails.average_score?.toFixed(1) || "N/A"}%
                </div>
                <div className="text-sm text-muted-foreground mt-1">Average Score</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold">
                  {userDetails.best_score?.toFixed(1) || "N/A"}%
                </div>
                <div className="text-sm text-muted-foreground mt-1">Best Score</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold">
                  {userDetails.latest_score && userDetails.average_score
                    ? (userDetails.latest_score - userDetails.average_score).toFixed(1)
                    : "N/A"}
                  %
                </div>
                <div className="text-sm text-muted-foreground mt-1">Improvement</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      {/* Skills Tab */}
      <TabsContent value="skills" className="space-y-4">
        <Card>
          <CardContent className="pt-6">
            <SkillRadarChart
              userSkills={skillData}
              showComparison={false}
            />
          </CardContent>
        </Card>

        {/* Strengths & Weaknesses */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-600">
                <CheckCircle className="h-5 w-5" />
                Strengths
              </CardTitle>
            </CardHeader>
            <CardContent>
              {userDetails.strengths && userDetails.strengths.length > 0 ? (
                <ul className="space-y-2">
                  {userDetails.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{strength}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">No strengths identified yet</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-600">
                <AlertCircle className="h-5 w-5" />
                Areas for Improvement
              </CardTitle>
            </CardHeader>
            <CardContent>
              {userDetails.weaknesses && userDetails.weaknesses.length > 0 ? (
                <ul className="space-y-2">
                  {userDetails.weaknesses.map((weakness, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{weakness}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">No weaknesses identified yet</p>
              )}
            </CardContent>
          </Card>
        </div>
      </TabsContent>

      {/* History Tab */}
      <TabsContent value="history" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Interview Timeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            {userDetails.interview_history && userDetails.interview_history.length > 0 ? (
              <div className="space-y-4">
                {userDetails.interview_history.map((interview, index) => (
                  <div
                    key={interview.session_id}
                    className="p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-medium">
                            Interview #{userDetails.interview_history!.length - index}
                          </span>
                          <Badge
                            variant={
                              interview.percentage >= 70
                                ? "default"
                                : interview.percentage >= 50
                                ? "secondary"
                                : "destructive"
                            }
                          >
                            {interview.percentage >= 70
                              ? "Pass"
                              : interview.percentage >= 50
                              ? "Borderline"
                              : "Fail"}
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground flex items-center gap-4">
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {new Date(
                              typeof interview.created_at === "string"
                                ? interview.created_at
                                : interview.created_at
                            ).toLocaleString()}
                          </span>
                          <span>
                            Score: {interview.total_score} / {interview.max_score}
                          </span>
                        </div>
                        {interview.questions && interview.questions.length > 0 && (
                          <div className="mt-4 space-y-3">
                            {interview.questions.map((qa, qIndex) => (
                              <div key={qIndex} className="p-3 bg-muted rounded-lg">
                                <div className="font-medium text-sm mb-1">Q{qIndex + 1}: {qa.question}</div>
                                <div className="text-sm text-muted-foreground mb-2">
                                  Answer: {qa.answer}
                                </div>
                                <div className="flex items-center justify-between">
                                  <Badge variant={qa.score >= 70 ? "default" : qa.score >= 50 ? "secondary" : "destructive"}>
                                    Score: {qa.score}%
                                  </Badge>
                                  <span className="text-xs text-muted-foreground">{qa.feedback}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="text-right ml-4">
                        <div className="text-2xl font-bold">
                          {interview.percentage != null ? Number(interview.percentage).toFixed(1) : "N/A"}%
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No interviews yet</p>
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>

      {/* Analytics Tab */}
      <TabsContent value="analytics" className="space-y-4">
        {userDetails.progression && userDetails.progression.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart2 className="h-5 w-5" />
                Score Progression
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScoreProgressionChart data={userDetails.progression} />
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Performance Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Average Score</span>
                  <span className="font-semibold">{userDetails.average_score?.toFixed(1) || "N/A"}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Best Performance</span>
                  <span className="font-semibold">{userDetails.best_score?.toFixed(1) || "N/A"}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Latest Performance</span>
                  <span className="font-semibold">{userDetails.latest_score?.toFixed(1) || "N/A"}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Improvement Trend</span>
                  <span className={`font-semibold flex items-center gap-1 ${
                    userDetails.latest_score && userDetails.average_score
                      ? userDetails.latest_score > userDetails.average_score
                        ? "text-green-600"
                        : "text-red-600"
                      : ""
                  }`}>
                    {userDetails.latest_score && userDetails.average_score ? (
                      <>
                        {userDetails.latest_score > userDetails.average_score ? (
                          <TrendingUp className="h-4 w-4" />
                        ) : (
                          <TrendingDown className="h-4 w-4" />
                        )}
                        {Math.abs(userDetails.latest_score - userDetails.average_score).toFixed(1)}%
                      </>
                    ) : (
                      "N/A"
                    )}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Interview Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Total Interviews</span>
                  <span className="font-semibold">{userDetails.total_interviews || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Pass Rate</span>
                  <span className="font-semibold">
                    {userDetails.interview_history
                      ? (
                          (userDetails.interview_history.filter((i) => i.percentage >= 70).length /
                            userDetails.interview_history.length) *
                          100
                        ).toFixed(1)
                      : "N/A"}
                    %
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Average Improvement</span>
                  <span className="font-semibold">
                    {userDetails.progression && userDetails.progression.length > 1
                      ? (
                          (userDetails.progression[userDetails.progression.length - 1].score -
                            userDetails.progression[0].score) /
                          (userDetails.progression.length - 1)
                        ).toFixed(1)
                      : "N/A"}
                    %
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </TabsContent>

      {/* Comparison Tab */}
      <TabsContent value="comparison" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>User vs Benchmarks</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Compare this user's performance against role benchmarks and top performers.
            </p>
            <div className="space-y-4">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Average Score</span>
                  <span className="text-sm text-muted-foreground">vs Role Benchmark (70%)</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary transition-all"
                        style={{
                          width: `${userDetails.average_score || 0}%`,
                        }}
                      />
                    </div>
                  </div>
                  <span className="font-semibold w-16 text-right">
                    {userDetails.average_score?.toFixed(1) || "N/A"}%
                  </span>
                </div>
              </div>
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Best Score</span>
                  <span className="text-sm text-muted-foreground">vs Top Performers (85%)</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary transition-all"
                        style={{
                          width: `${userDetails.best_score || 0}%`,
                        }}
                      />
                    </div>
                  </div>
                  <span className="font-semibold w-16 text-right">
                    {userDetails.best_score?.toFixed(1) || "N/A"}%
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      {/* Evidence Tab */}
      <TabsContent value="evidence" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5" />
              AI Explanations & Evidence
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Detailed explanations of scoring decisions and evidence from interviews.
            </p>
            {userDetails.interview_history && userDetails.interview_history.length > 0 ? (
              <div className="space-y-4">
                {userDetails.interview_history.map((interview, index) => (
                  <div key={interview.session_id} className="p-4 border rounded-lg">
                    <div className="font-medium mb-2">
                      Interview #{userDetails.interview_history!.length - index}
                    </div>
                    {interview.detailed_feedback && interview.detailed_feedback.length > 0 ? (
                      <div className="space-y-3">
                        {interview.detailed_feedback.map((qa, qIndex) => (
                          <div key={qIndex} className="p-3 bg-muted rounded-lg">
                            <div className="font-medium text-sm mb-2">Question {qIndex + 1}</div>
                            <div className="text-sm mb-2">
                              <span className="font-medium">Q:</span> {qa.question}
                            </div>
                            <div className="text-sm mb-2">
                              <span className="font-medium">A:</span> {qa.answer}
                            </div>
                            <div className="text-sm mb-2">
                              <span className="font-medium">Feedback:</span> {qa.feedback}
                            </div>
                            {qa.strengths && qa.strengths.length > 0 && (
                              <div className="text-sm mb-2">
                                <span className="font-medium">Strengths:</span> {qa.strengths.join(", ")}
                              </div>
                            )}
                            {qa.weaknesses && qa.weaknesses.length > 0 && (
                              <div className="text-sm mb-2">
                                <span className="font-medium">Weaknesses:</span> {qa.weaknesses.join(", ")}
                              </div>
                            )}
                            <div className="mt-2">
                              <Badge variant={qa.score >= 70 ? "default" : qa.score >= 50 ? "secondary" : "destructive"}>
                                Score: {qa.score}%
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">No detailed question breakdown available</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No interview evidence available</p>
            )}
          </CardContent>
        </Card>

        {userDetails.recommendations && userDetails.recommendations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {userDetails.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <Lightbulb className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{rec}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </TabsContent>
    </Tabs>
  );
}

