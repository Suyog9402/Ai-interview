"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function AdminAnalyticsPage() {
  const [dateRange, setDateRange] = useState("30d");
  const [isLoading, setIsLoading] = useState(true);
  const [interviewsOverTime, setInterviewsOverTime] = useState<{ date: string; count: number }[]>([]);
  const [scoreDistribution, setScoreDistribution] = useState<{ range: string; count: number }[]>([]);

  useEffect(() => {
    loadAnalytics();
  }, [dateRange]);

  async function loadAnalytics() {
    try {
      setIsLoading(true);
      const [scoreRes, interviewsRes] = await Promise.all([
        apiClient.getScoreDistribution().catch(() => ({ total: 0, ranges: {} })),
        apiClient.getAllInterviews({ skip: 0, limit: 5000 }).catch(() => []),
      ]);

      const ranges = (scoreRes?.ranges ?? {}) as Record<string, number>;
      setScoreDistribution([
        { range: "0-20", count: ranges["0-20"] ?? 0 },
        { range: "21-40", count: ranges["21-40"] ?? 0 },
        { range: "41-60", count: ranges["41-60"] ?? 0 },
        { range: "61-80", count: ranges["61-80"] ?? 0 },
        { range: "81-100", count: ranges["81-100"] ?? 0 },
      ]);

      const list = Array.isArray(interviewsRes) ? interviewsRes : [];
      const byDate: Record<string, number> = {};
      list.forEach((row: any) => {
        const created = row.created_at;
        if (!created) return;
        const d = new Date(created);
        const key = d.toISOString().slice(0, 10);
        byDate[key] = (byDate[key] || 0) + 1;
      });
      const sorted = Object.entries(byDate)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([date, count]) => ({ date, count }));
      setInterviewsOverTime(sorted);
    } catch (e) {
      setInterviewsOverTime([]);
      setScoreDistribution([]);
    } finally {
      setIsLoading(false);
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground mt-2">
            Insights and performance metrics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2">
            <Button
              variant={dateRange === "7d" ? "default" : "outline"}
              size="sm"
              onClick={() => setDateRange("7d")}
            >
              7d
            </Button>
            <Button
              variant={dateRange === "30d" ? "default" : "outline"}
              size="sm"
              onClick={() => setDateRange("30d")}
            >
              30d
            </Button>
            <Button
              variant={dateRange === "90d" ? "default" : "outline"}
              size="sm"
              onClick={() => setDateRange("90d")}
            >
              90d
            </Button>
          </div>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Interviews Over Time - real data only */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Interviews Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            {interviewsOverTime.length === 0 ? (
              <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                No interview data yet
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={interviewsOverTime}>
                  <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
                  <XAxis dataKey="date" stroke="currentColor" opacity={0.7} />
                  <YAxis stroke="currentColor" opacity={0.7} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="hsl(var(--primary))"
                    strokeWidth={2}
                    dot={{ fill: "hsl(var(--primary))" }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Score Distribution - real data only */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Score Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {scoreDistribution.every((s) => s.count === 0) ? (
              <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                No score data yet
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={scoreDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
                  <XAxis dataKey="range" stroke="currentColor" opacity={0.7} />
                  <YAxis stroke="currentColor" opacity={0.7} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                  />
                  <Bar dataKey="count" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
