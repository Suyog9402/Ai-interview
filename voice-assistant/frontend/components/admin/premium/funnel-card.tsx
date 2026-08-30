"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PipelineMetrics } from "@/types/admin";
import { cn } from "@/lib/utils";

interface FunnelCardProps {
  metrics: PipelineMetrics;
}

export function FunnelCard({ metrics }: FunnelCardProps) {
  const stages = [
    { label: 'Resume Uploaded', value: metrics.resume_uploaded, color: 'bg-blue-500' },
    { label: 'Parsed', value: metrics.parsed, color: 'bg-purple-500' },
    { label: 'Matched', value: metrics.matched, color: 'bg-indigo-500' },
    { label: 'Interview Started', value: metrics.interview_started, color: 'bg-pink-500' },
    { label: 'Completed', value: metrics.completed, color: 'bg-orange-500' },
    { label: 'Hired/Recommended', value: metrics.hired_recommended, color: 'bg-green-500' },
  ];

  const maxValue = Math.max(...stages.map(s => s.value));

  return (
    <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Pipeline Funnel</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {stages.map((stage, index) => {
          const percentage = maxValue > 0 ? (stage.value / maxValue) * 100 : 0;
          const conversionRate = index > 0 && stages[index - 1].value > 0
            ? ((stage.value / stages[index - 1].value) * 100).toFixed(1)
            : '100';

          return (
            <div key={stage.label} className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{stage.label}</span>
                <div className="flex items-center gap-3">
                  <span className="text-muted-foreground">{stage.value.toLocaleString()}</span>
                  {index > 0 && (
                    <span className="text-xs text-muted-foreground">
                      {conversionRate}%
                    </span>
                  )}
                </div>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className={cn("h-full transition-all duration-500", stage.color)}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}

