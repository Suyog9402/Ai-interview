"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ActivityEvent } from "@/types/admin";
import { formatDistanceToNow } from "@/lib/date-utils";
import {
  FileText,
  CheckCircle,
  AlertTriangle,
  Webhook,
  Zap,
  Briefcase,
} from "lucide-react";

interface ActivityTimelineProps {
  events: ActivityEvent[];
  limit?: number;
}

const eventIcons: Record<string, React.ComponentType<any>> = {
  resume_parsed: FileText,
  interview_completed: CheckCircle,
  flagged_event: AlertTriangle,
  webhook_triggered: Webhook,
  automation_ran: Zap,
  jd_created: Briefcase,
};

export function ActivityTimeline({ events, limit = 3 }: ActivityTimelineProps) {
  const displayEvents = events.slice(0, limit);

  return (
    <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-base font-semibold">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-2">
          {displayEvents.length === 0 ? (
            <div className="text-center py-6 text-muted-foreground text-xs">
              No recent activity
            </div>
          ) : (
            displayEvents.map((event, index) => {
              const Icon = eventIcons[event.type] || FileText;
              return (
                <div key={event.id} className="flex gap-3 items-start">
                  <div className="flex flex-col items-center pt-0.5">
                    <div className="p-1.5 rounded-md bg-primary/10">
                      <Icon className="h-3.5 w-3.5 text-primary" />
                    </div>
                    {index < displayEvents.length - 1 && (
                      <div className="w-px h-4 bg-border mt-1" />
                    )}
                  </div>
                  <div className="flex-1 pb-2 min-w-0">
                    <p className="text-xs font-medium leading-tight">{event.description}</p>
                    <p className="text-[10px] text-muted-foreground mt-0.5">
                      {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                    </p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </CardContent>
    </Card>
  );
}

