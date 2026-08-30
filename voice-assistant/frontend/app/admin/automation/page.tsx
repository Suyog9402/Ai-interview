"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusChip } from "@/components/admin/premium/status-chip";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Workflow,
  Play,
  Pause,
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp,
  Plus,
} from "lucide-react";
import { Automation, AutomationLog } from "@/types/admin";
import { formatDistanceToNow } from "@/lib/date-utils";
import { cn } from "@/lib/utils";

export default function AdminAutomationPage() {
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [selectedAutomation, setSelectedAutomation] = useState<Automation | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAutomations();
  }, []);

  const loadAutomations = async () => {
    try {
      setIsLoading(true);
      // Replace with actual API call
      // Mock data for now
      setAutomations([
        {
          id: '1',
          name: 'Resume Upload → Parse → Match → Schedule',
          description: 'Automatically processes uploaded resumes and schedules interviews for matched candidates',
          trigger: 'resume_uploaded',
          actions: ['parse_resume', 'match_to_jobs', 'schedule_interview', 'notify_candidate'],
          status: 'enabled',
          last_run: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          success_rate: 98.5,
          recent_errors: [],
        },
        {
          id: '2',
          name: 'Interview Complete → Evaluate → Notify',
          description: 'Evaluates completed interviews and sends notifications',
          trigger: 'interview_completed',
          actions: ['evaluate_interview', 'send_notification'],
          status: 'enabled',
          last_run: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
          success_rate: 99.2,
          recent_errors: [],
        },
        // Add more mock automations
      ]);
    } catch (err) {
      console.error("Error loading automations:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleAutomation = (id: string) => {
    setAutomations(prev =>
      prev.map(automation =>
        automation.id === id
          ? { ...automation, status: automation.status === 'enabled' ? 'disabled' : 'enabled' }
          : automation
      )
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading automations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">Automation</h1>
          <p className="text-muted-foreground mt-2">
            Manage workflow automations
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Create Workflow
        </Button>
      </div>

      {/* Automations List */}
      <div className="grid gap-4">
        {automations.map((automation) => (
          <Card
            key={automation.id}
            className={cn(
              "border-border/50 bg-card/50 backdrop-blur-sm",
              "hover:border-primary/20 hover:shadow-lg hover:shadow-primary/5 transition-all",
              selectedAutomation?.id === automation.id && "border-primary/30"
            )}
            onClick={() => setSelectedAutomation(automation)}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <CardTitle className="text-lg">{automation.name}</CardTitle>
                    <StatusChip status={automation.status} size="sm" />
                  </div>
                  <p className="text-sm text-muted-foreground">{automation.description}</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleAutomation(automation.id);
                  }}
                >
                  {automation.status === 'enabled' ? (
                    <>
                      <Pause className="h-4 w-4 mr-2" />
                      Disable
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Enable
                    </>
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-1">
                  <p className="text-xs font-medium text-muted-foreground">Trigger</p>
                  <Badge variant="outline" className="text-xs">
                    {automation.trigger}
                  </Badge>
                </div>
                <div className="space-y-1">
                  <p className="text-xs font-medium text-muted-foreground">Success Rate</p>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-green-500" />
                    <span className="font-medium">{automation.success_rate}%</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-xs font-medium text-muted-foreground">Last Run</p>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    {automation.last_run
                      ? formatDistanceToNow(new Date(automation.last_run), { addSuffix: true })
                      : 'Never'}
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-border/50">
                <p className="text-xs font-medium text-muted-foreground mb-2">Actions</p>
                <div className="flex flex-wrap gap-2">
                  {automation.actions.map((action, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {index + 1}. {action}
                    </Badge>
                  ))}
                </div>
              </div>

              {automation.recent_errors && automation.recent_errors.length > 0 && (
                <div className="mt-4 pt-4 border-t border-border/50">
                  <div className="flex items-center gap-2 text-yellow-500">
                    <AlertCircle className="h-4 w-4" />
                    <span className="text-xs font-medium">
                      {automation.recent_errors.length} recent error{automation.recent_errors.length > 1 ? 's' : ''}
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {automations.length === 0 && (
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <Workflow className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground mb-4">No automations configured</p>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Workflow
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

