"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { StatusChip } from "@/components/admin/premium/status-chip";
import { ScoreRing } from "@/components/admin/premium/score-ring";
import {
  Search,
  FileText,
  Calendar,
  Clock,
  AlertTriangle,
  ExternalLink,
  User,
} from "lucide-react";
import { Interview } from "@/types/admin";
import { formatDistanceToNow } from "@/lib/date-utils";

export default function AdminInterviewsPage() {
  const router = useRouter();
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [filteredInterviews, setFilteredInterviews] = useState<Interview[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  useEffect(() => {
    loadInterviews();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [interviews, searchQuery, statusFilter]);

  const loadInterviews = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getAllInterviews({ skip: 0, limit: 1000 });
      const mapped: Interview[] = (data || []).map((row: any) => ({
        id: row.session_id || String(row.session_id),
        session_id: row.session_id,
        user_id: row.user_id,
        candidate_name: undefined,
        job_title: undefined,
        status: "completed" as const,
        total_score: row.total_score,
        max_score: row.max_score,
        percentage: row.percentage != null ? Number(row.percentage) : undefined,
        duration_minutes: undefined,
        created_at: row.created_at || new Date().toISOString(),
        risk_flags: [],
      }));
      setInterviews(mapped);
    } catch (err) {
      console.error("Error loading interviews:", err);
      setInterviews([]);
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...interviews];
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (interview) =>
          interview.candidate_name?.toLowerCase().includes(query) ||
          interview.job_title?.toLowerCase().includes(query) ||
          (interview.session_id && String(interview.session_id).toLowerCase().includes(query)) ||
          (interview.user_id && String(interview.user_id).toLowerCase().includes(query))
      );
    }
    if (statusFilter !== "all") {
      filtered = filtered.filter((interview) => interview.status === statusFilter);
    }
    setFilteredInterviews(filtered);
  };

  const handleViewDetails = (sessionId: string) => {
    router.push(`/admin/interviews/${sessionId}`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading interviews...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">Interviews</h1>
          <p className="text-muted-foreground mt-2">
            View and manage all interview sessions
          </p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search by candidate, job, session ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 bg-muted/50 border-border/50"
          />
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={statusFilter === "all" ? "default" : "outline"}
            size="sm"
            onClick={() => setStatusFilter("all")}
          >
            All
          </Button>
          <Button
            variant={statusFilter === "completed" ? "default" : "outline"}
            size="sm"
            onClick={() => setStatusFilter("completed")}
          >
            Completed
          </Button>
          <Button
            variant={statusFilter === "running" ? "default" : "outline"}
            size="sm"
            onClick={() => setStatusFilter("running")}
          >
            Running
          </Button>
          <Button
            variant={statusFilter === "failed" ? "default" : "outline"}
            size="sm"
            onClick={() => setStatusFilter("failed")}
          >
            Failed
          </Button>
        </div>
      </div>

      {/* Interviews Table */}
      <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle>Interviews</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredInterviews.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                {searchQuery || statusFilter !== "all"
                  ? "No interviews match your filters"
                  : "No interviews found"}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border/50">
                    <th className="text-left p-4 font-medium text-sm text-muted-foreground">Candidate</th>
                    <th className="text-left p-4 font-medium text-sm text-muted-foreground">Job</th>
                    <th className="text-left p-4 font-medium text-sm text-muted-foreground">Status</th>
                    <th className="text-left p-4 font-medium text-sm text-muted-foreground">Score</th>
                    <th className="text-left p-4 font-medium text-sm text-muted-foreground">Duration</th>
                    <th className="text-left p-4 font-medium text-sm text-muted-foreground">Date</th>
                    <th className="text-left p-4 font-medium text-sm text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredInterviews.map((interview) => (
                    <tr
                      key={interview.id}
                      className="border-b border-border/50 hover:bg-muted/30 transition-colors cursor-pointer"
                      onClick={() => handleViewDetails(interview.session_id)}
                    >
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-muted-foreground" />
                          <span className="font-medium">
                            {interview.candidate_name || `User ${interview.user_id}`}
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <span className="text-sm">{interview.job_title || "—"}</span>
                      </td>
                      <td className="p-4">
                        <StatusChip status={interview.status} size="sm" />
                        {interview.risk_flags && interview.risk_flags.length > 0 && (
                          <div className="flex items-center gap-1 mt-1">
                            <AlertTriangle className="h-3 w-3 text-yellow-500" />
                            <span className="text-xs text-yellow-500">
                              {interview.risk_flags.length} flag{interview.risk_flags.length > 1 ? 's' : ''}
                            </span>
                          </div>
                        )}
                      </td>
                      <td className="p-4">
                        {interview.percentage != null && Number(interview.percentage) === interview.percentage ? (
                          <div className="flex items-center gap-3">
                            <ScoreRing score={Number(interview.percentage)} size="sm" />
                            <span className="font-medium">{Number(interview.percentage).toFixed(1)}%</span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                      <td className="p-4">
                        {interview.duration_minutes ? (
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            <span>{interview.duration_minutes}min</span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Calendar className="h-4 w-4" />
                          {formatDistanceToNow(new Date(interview.created_at), { addSuffix: true })}
                        </div>
                      </td>
                      <td className="p-4">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewDetails(interview.session_id);
                          }}
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
