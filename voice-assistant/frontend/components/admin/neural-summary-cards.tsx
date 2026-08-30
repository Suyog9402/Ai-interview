"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Brain, MessageSquare, Code, TrendingUp, CheckCircle } from "lucide-react";

interface NeuralSummaryCardsProps {
  userDetails: any;
}

export function NeuralSummaryCards({ userDetails }: NeuralSummaryCardsProps) {
  const metrics = useMemo(() => {
    const interviews = userDetails.interview_history || [];
    const avgScore = userDetails.average_score || 0;
    
    // Calculate metrics from interview history
    const cognitiveScore = avgScore / 100;
    const communicationScore = avgScore * 0.9 / 100; // Proxy metric
    const technicalDepth = avgScore * 0.85 / 100;
    const consistency = interviews.length > 1 
      ? 1 - (Math.max(...interviews.map((i: any) => i.percentage || 0)) - Math.min(...interviews.map((i: any) => i.percentage || 0))) / 100
      : 0.5;
    const completionRate = interviews.length > 0 ? 1.0 : 0;

    return {
      cognitive: { score: cognitiveScore, label: cognitiveScore >= 0.7 ? "Strong" : cognitiveScore >= 0.4 ? "Moderate" : "Below expected" },
      communication: { score: communicationScore, label: communicationScore >= 0.7 ? "Clear" : "Needs work" },
      technical: { score: technicalDepth, label: technicalDepth >= 0.7 ? "Deep" : "Surface level" },
      consistency: { score: consistency, label: consistency >= 0.8 ? "Stable" : "Variable" },
      completion: { score: completionRate, label: "100%" },
    };
  }, [userDetails]);

  const cards = [
    { key: "cognitive", icon: Brain, label: "Cognitive Score", color: "cyan" },
    { key: "communication", icon: MessageSquare, label: "Communication Clarity", color: "blue" },
    { key: "technical", icon: Code, label: "Technical Depth", color: "purple" },
    { key: "consistency", icon: TrendingUp, label: "Behavioral Consistency", color: "amber" },
    { key: "completion", icon: CheckCircle, label: "Interview Completion", color: "emerald" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {cards.map(({ key, icon: Icon, label }) => {
        const metric = metrics[key as keyof typeof metrics];
        
        return (
          <Card key={key}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{label}</CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.score.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground mt-1">{metric.label}</p>
              <p className="text-xs text-muted-foreground mt-2">
                Based on {userDetails.total_interviews || 0} interviews
              </p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}

