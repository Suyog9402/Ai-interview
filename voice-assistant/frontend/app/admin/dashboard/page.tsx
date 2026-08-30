"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api";
import { StatCard } from "@/components/admin/premium/stat-card";
import { FunnelCard } from "@/components/admin/premium/funnel-card";
import { ActivityTimeline } from "@/components/admin/premium/activity-timeline";
import { HealthPanel } from "@/components/admin/premium/health-panel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Users,
  UserCheck,
  FileText,
  Calendar,
  TrendingUp,
  Award,
  Clock,
  Plus,
  FileCheck,
  Download,
  RefreshCw,
} from "lucide-react";
import { DashboardStats, PipelineMetrics, SystemHealth, ActivityEvent } from "@/types/admin";
import { toast } from "sonner";

export default function AdminDashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [pipeline, setPipeline] = useState<PipelineMetrics | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [activities, setActivities] = useState<ActivityEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getAdminOverviewStats();
      setStats({
        total_users: data.total_users || 0,
        active_users: data.active_users || 0,
        interviews_today: data.interviews_today || 0,
        interviews_this_week: data.interviews_this_week || 0,
        total_interviews: data.total_interviews || 0,
        avg_score: data.avg_score ?? data.average_score ?? 0,
        pass_rate: data.pass_rate || 0,
        avg_interview_duration: data.avg_interview_duration ?? 0,
      });

      const [pipelineData, healthData] = await Promise.all([
        apiClient.getAdminPipelineStats().catch(() => null),
        apiClient.getAdminSystemHealth().catch(() => null),
      ]);
      if (pipelineData) {
        setPipeline({
          resume_uploaded: pipelineData.resume_uploaded ?? 0,
          parsed: pipelineData.parsed ?? 0,
          matched: pipelineData.matched ?? 0,
          interview_started: pipelineData.interview_started ?? 0,
          completed: pipelineData.completed ?? 0,
          hired_recommended: pipelineData.hired_recommended ?? 0,
        });
      }
      if (healthData) {
        setHealth({
          queue_size: healthData.queue_size ?? 0,
          failure_rate: healthData.failure_rate ?? 0,
          avg_latency_ms: healthData.avg_latency_ms ?? 0,
          token_usage_today: healthData.token_usage_today ?? 0,
          cost_today: healthData.cost_today ?? 0,
          uptime_status: healthData.uptime_status ?? "healthy",
        });
      }
      
      // Fetch real activity data
      try {
        const realActivities = await apiClient.getRecentActivity(3);
        if (realActivities && realActivities.length > 0) {
          setActivities(realActivities);
        } else {
          // If no real activities, show empty array
          setActivities([]);
        }
      } catch (activityError) {
        console.error("Error loading activities:", activityError);
        // Fallback to empty array if API fails
        setActivities([]);
      }
    } catch (err) {
      console.error("Error loading dashboard:", err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-32 bg-muted/50 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const statCards = stats ? [
    {
      title: "Total Users",
      value: stats.total_users,
      icon: Users,
      description: "Registered users",
    },
    {
      title: "Active Users",
      value: stats.active_users,
      icon: UserCheck,
      description: "Active this month",
    },
    {
      title: "Interviews Today",
      value: stats.interviews_today,
      icon: Calendar,
      description: "Conducted today",
    },
    {
      title: "This Week",
      value: stats.interviews_this_week,
      icon: TrendingUp,
      description: "Interviews this week",
    },
    {
      title: "Total Interviews",
      value: stats.total_interviews,
      icon: FileText,
      description: "All time",
    },
    {
      title: "Avg Score",
      value: `${Number(stats.avg_score ?? 0).toFixed(1)}%`,
      icon: Award,
      description: "Average interview score",
    },
    {
      title: "Pass Rate",
      value: `${Number(stats.pass_rate ?? 0).toFixed(1)}%`,
      icon: TrendingUp,
      description: "Candidates passing",
    },
    {
      title: "Avg Duration",
      value: `${stats.avg_interview_duration ?? 0}min`,
      icon: Clock,
      description: "Average interview time",
    },
  ] : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            AI Interview Operations Overview
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={loadDashboardData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <StatCard
              key={index}
              title={stat.title}
              value={stat.value}
              icon={Icon}
              description={stat.description}
            />
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Pipeline Funnel */}
        {pipeline && <FunnelCard metrics={pipeline} />}

        {/* Recent Activity */}
        <ActivityTimeline events={activities} limit={3} />
      </div>

      {/* System Health */}
      {health && <HealthPanel health={health} />}

      {/* Quick Actions */}
      <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Button 
              variant="outline" 
              className="h-auto py-4 flex-col gap-2 cursor-pointer hover:bg-primary/10 hover:border-primary/50 transition-all"
              onClick={() => router.push("/admin/jobs/create")}
            >
              <Plus className="h-5 w-5" />
              <span className="text-sm">Create Job</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto py-4 flex-col gap-2 cursor-pointer hover:bg-primary/10 hover:border-primary/50 transition-all"
              onClick={() => {
                toast.info("Rubric management feature coming soon. This will allow you to create and manage evaluation rubrics for interviews.");
                // Future: router.push("/admin/rubrics");
              }}
            >
              <FileCheck className="h-5 w-5" />
              <span className="text-sm">Add Rubric</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto py-4 flex-col gap-2 cursor-pointer hover:bg-primary/10 hover:border-primary/50 transition-all"
              onClick={async () => {
                try {
                  toast.loading("Running re-match for all candidates...");
                  const result = await apiClient.runRematchAll();
                  toast.success(
                    `Re-match completed! ${result.matches_created || 0} matches created.`
                  );
                } catch (error: any) {
                  toast.error(error.message || "Failed to run re-match");
                }
              }}
            >
              <RefreshCw className="h-5 w-5" />
              <span className="text-sm">Run Re-match</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto py-4 flex-col gap-2 cursor-pointer hover:bg-primary/10 hover:border-primary/50 transition-all"
              onClick={async () => {
                try {
                  toast.loading("Exporting data...");
                  const blob = await apiClient.exportInterviews("csv");
                  
                  // Create download link
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `interviews_export_${new Date().toISOString().split('T')[0]}.csv`;
                  document.body.appendChild(a);
                  a.click();
                  window.URL.revokeObjectURL(url);
                  document.body.removeChild(a);
                  
                  toast.success("Data exported successfully");
                } catch (error: any) {
                  toast.error(error.message || "Failed to export data");
                }
              }}
            >
              <Download className="h-5 w-5" />
              <span className="text-sm">Export Data</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
