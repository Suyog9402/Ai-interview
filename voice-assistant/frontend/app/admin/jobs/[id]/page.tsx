"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatusChip } from "@/components/admin/premium/status-chip";
import {
  ArrowLeft,
  Briefcase,
  Users,
  RefreshCw,
  TrendingUp,
  Award,
  CheckCircle2,
  Eye,
} from "lucide-react";
import { Job, TopCandidate } from "@/types/admin";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface JDVersion {
  id: number;
  version_number: number;
  content: string;
  requirements?: any;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface JDDetail {
  id: number;
  title: string;
  description?: string;
  current_version_id?: number;
  current_version?: JDVersion;
  versions?: JDVersion[];
  created_at: string;
  updated_at: string;
}

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = parseInt(params.id as string);
  
  const [jdDetail, setJdDetail] = useState<JDDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedVersion, setSelectedVersion] = useState<JDVersion | null>(null);

  useEffect(() => {
    if (jobId) {
      loadJobDetails();
    }
  }, [jobId]);

  const loadJobDetails = async () => {
    try {
      setIsLoading(true);
      const jd = await apiClient.getJD(jobId);
      setJdDetail(jd);
      // Set selected version to current active version
      if (jd.current_version) {
        setSelectedVersion(jd.current_version);
      } else if (jd.versions && jd.versions.length > 0) {
        setSelectedVersion(jd.versions.find((v: JDVersion) => v.is_active) || jd.versions[0]);
      }
    } catch (err: any) {
      console.error("Error loading job details:", err);
      toast.error(err.message || "Failed to load job details");
    } finally {
      setIsLoading(false);
    }
  };

  const handleActivateVersion = async (versionId: number) => {
    try {
      await apiClient.activateJDVersion(jobId, versionId);
      toast.success("Version activated successfully");
      loadJobDetails();
    } catch (err: any) {
      toast.error(err.message || "Failed to activate version");
    }
  };

  const handleViewVersion = (version: JDVersion) => {
    setSelectedVersion(version);
  };

  // Transform JD detail to Job type for compatibility
  const job: Job | null = jdDetail ? {
    id: jdDetail.id,
    title: jdDetail.title,
    description: jdDetail.description || "",
    required_skills: jdDetail.current_version?.requirements?.must_have_skills || [],
    nice_to_have_skills: jdDetail.current_version?.requirements?.nice_to_have_skills || [],
    experience_range: {
      min: jdDetail.current_version?.requirements?.min_experience_years || 0,
      max: jdDetail.current_version?.requirements?.min_experience_years ? 
        jdDetail.current_version.requirements.min_experience_years + 5 : 10,
    },
    status: jdDetail.current_version?.is_active ? "open" : "closed",
    total_candidates_matched: 0,
  } : null;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading job details...</p>
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="w-full max-w-md border-border/50 bg-card/50 backdrop-blur-sm">
          <CardContent className="pt-6">
            <div className="text-center">
              <Briefcase className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-foreground mb-4">Job not found</p>
              <Button onClick={() => router.push("/admin/jobs")} variant="outline">
                Back to Jobs
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

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
          <h1 className="text-4xl font-bold tracking-tight">{job.title}</h1>
          <p className="text-muted-foreground mt-2">
            {job.description}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <StatusChip status={job.status} />
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Re-run Matching
          </Button>
        </div>
      </div>

      {/* Job Details Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Required Skills */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Required Skills</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {job.required_skills.map((skill) => (
                <Badge key={skill} variant="default" className="text-sm">
                  {skill}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Nice to Have Skills */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Nice to Have</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {job.nice_to_have_skills.map((skill) => (
                <Badge key={skill} variant="secondary" className="text-sm">
                  {skill}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Experience Range */}
      <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Experience Range</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-lg font-medium">
            {job.experience_range.min} - {job.experience_range.max} years
          </p>
        </CardContent>
      </Card>

      {/* Match Distribution Chart */}
      {job.match_distribution && job.match_distribution.length > 0 && (
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Match Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={job.match_distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
                <XAxis dataKey="range" stroke="currentColor" opacity={0.7} />
                <YAxis stroke="currentColor" opacity={0.7} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="count" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* JD Content */}
      {selectedVersion && (
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">
              JD Content {selectedVersion.is_active && (
                <Badge className="ml-2">Active Version {selectedVersion.version_number}</Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="p-4 border rounded-lg bg-muted/50 max-h-[500px] overflow-auto">
              <pre className="text-sm whitespace-pre-wrap font-mono">
                {selectedVersion.content}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Version History */}
      {jdDetail?.versions && jdDetail.versions.length > 0 && (
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Version History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {jdDetail.versions
                .sort((a, b) => b.version_number - a.version_number)
                .map((version) => (
                <div
                  key={version.id}
                  className={`p-4 border rounded-lg transition-colors ${
                    version.is_active 
                      ? "border-primary bg-primary/5" 
                      : "border-border/50 hover:border-primary/20"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div>
                        <p className="font-medium flex items-center gap-2">
                          Version {version.version_number}
                          {version.is_active && (
                            <Badge variant="default" className="text-xs">
                              <CheckCircle2 className="h-3 w-3 mr-1" />
                              Active
                            </Badge>
                          )}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          Created: {new Date(version.created_at).toLocaleDateString()} at{" "}
                          {new Date(version.created_at).toLocaleTimeString()}
                        </p>
                        {version.content.length > 0 && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {version.content.length} characters
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {!version.is_active && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleActivateVersion(version.id)}
                        >
                          Activate
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleViewVersion(version)}
                        className={selectedVersion?.id === version.id ? "bg-primary/10" : ""}
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        View
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Top Candidates - Keep if needed */}
      {job?.top_candidates && job.top_candidates.length > 0 && (
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold">Top Candidates</CardTitle>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Users className="h-4 w-4" />
                <span>{job.total_candidates_matched} total matched</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {job.top_candidates.map((candidate) => (
                <div
                  key={candidate.user_id}
                  className="p-4 border border-border/50 rounded-xl hover:border-primary/20 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="font-medium">{candidate.name}</p>
                      <p className="text-sm text-muted-foreground">User ID: {candidate.user_id}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Award className="h-4 w-4 text-yellow-500" />
                      <span className="font-bold text-lg">{candidate.match_percentage}%</span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {candidate.key_skills.map((skill) => (
                      <Badge key={skill} variant="outline" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

