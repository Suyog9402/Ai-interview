"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SystemHealth } from "@/types/admin";
import { StatusChip } from "./status-chip";
import {
  Activity,
  AlertCircle,
  Clock,
  DollarSign,
  Database,
  TrendingDown,
} from "lucide-react";

interface HealthPanelProps {
  health: SystemHealth;
}

export function HealthPanel({ health }: HealthPanelProps) {
  const metrics = [
    {
      label: 'Queue Size',
      value: health.queue_size.toLocaleString(),
      icon: Database,
      status: health.queue_size > 1000 ? 'warning' : 'normal',
    },
    {
      label: 'Failure Rate',
      value: `${health.failure_rate.toFixed(2)}%`,
      icon: TrendingDown,
      status: health.failure_rate > 5 ? 'error' : 'normal',
    },
    {
      label: 'Avg Latency',
      value: `${health.avg_latency_ms}ms`,
      icon: Clock,
      status: health.avg_latency_ms > 5000 ? 'warning' : 'normal',
    },
    {
      label: 'Token Usage',
      value: health.token_usage_today.toLocaleString(),
      icon: Activity,
      status: 'normal',
    },
    {
      label: 'Cost Today',
      value: `$${health.cost_today.toFixed(2)}`,
      icon: DollarSign,
      status: 'normal',
    },
  ];

  return (
    <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">System Health</CardTitle>
          <StatusChip
            status={health.uptime_status}
            variant={
              health.uptime_status === 'healthy' ? 'success' :
              health.uptime_status === 'degraded' ? 'warning' : 'error'
            }
          />
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {metrics.map((metric) => {
            const Icon = metric.icon;
            return (
              <div key={metric.label} className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Icon className="h-4 w-4" />
                  <span>{metric.label}</span>
                </div>
                <p className="text-xl font-semibold">{metric.value}</p>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

