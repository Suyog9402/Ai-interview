"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { StatusChip } from "@/components/admin/premium/status-chip";
import { Badge } from "@/components/ui/badge";
import {
  Search,
  Briefcase,
  Users,
  ExternalLink,
  Plus,
  Trash2,
  RotateCcw,
} from "lucide-react";
import { Job } from "@/types/admin";
import { cn } from "@/lib/utils";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";

export default function AdminJobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [filteredJobs, setFilteredJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    loadJobs();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [jobs, searchQuery]);

  const loadJobs = async () => {
    try {
      setIsLoading(true);
      const jds = await apiClient.getAllJDs();
      // Transform backend response to match Job type
      const transformedJobs: Job[] = jds.map((jd: any) => ({
        id: jd.id,
        title: jd.title,
        description: jd.description || "",
        required_skills: jd.current_version?.requirements?.must_have_skills || [],
        nice_to_have_skills: jd.current_version?.requirements?.nice_to_have_skills || [],
        experience_range: {
          min: jd.current_version?.requirements?.min_experience_years || 0,
          max: jd.current_version?.requirements?.min_experience_years ? 
            jd.current_version.requirements.min_experience_years + 5 : 10,
        },
        status: jd.current_version?.is_active ? "open" : "closed",
        total_candidates_matched: 0, // TODO: Calculate from match results
      }));
      setJobs(transformedJobs);
    } catch (err: any) {
      console.error("Error loading jobs:", err);
      toast.error(err.message || "Failed to load jobs");
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...jobs];
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (job) =>
          job.title.toLowerCase().includes(query) ||
          job.description.toLowerCase().includes(query) ||
          job.required_skills.some(skill => skill.toLowerCase().includes(query))
      );
    }
    
    setFilteredJobs(filtered);
  };

  const handleViewDetails = (jobId: number) => {
    router.push(`/admin/jobs/${jobId}`);
  };

  const handleDelete = async (jobId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this job? This action cannot be undone.")) {
      return;
    }
    
    try {
      await apiClient.deleteJD(jobId);
      toast.success("Job deleted successfully");
      loadJobs();
    } catch (err: any) {
      toast.error(err.message || "Failed to delete job");
    }
  };

  const handleReopen = async (jobId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiClient.reopenJD(jobId);
      toast.success("Job reopened successfully – it’s now available to candidates");
      loadJobs();
    } catch (err: any) {
      toast.error(err.message || "Failed to reopen job");
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading jobs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">Jobs</h1>
          <p className="text-muted-foreground mt-2">
            Manage job postings and matching
          </p>
        </div>
        <Button onClick={() => router.push("/admin/jobs/create")}>
          <Plus className="h-4 w-4 mr-2" />
          Create Job
        </Button>
      </div>

      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search jobs by title, skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 bg-muted/50 border-border/50"
          />
        </div>
      </div>

      {/* Jobs Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredJobs.length === 0 ? (
          <Card className="col-span-full border-border/50 bg-card/50 backdrop-blur-sm">
            <CardContent className="pt-6">
              <div className="text-center py-12">
                <Briefcase className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  {searchQuery ? "No jobs match your search" : "No jobs found"}
                </p>
              </div>
            </CardContent>
          </Card>
        ) : (
          filteredJobs.map((job) => (
            <Card
              key={job.id}
              className="border-border/50 bg-card/50 backdrop-blur-sm hover:border-primary/20 hover:shadow-lg hover:shadow-primary/5 transition-all cursor-pointer"
              onClick={() => handleViewDetails(job.id)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg">{job.title}</CardTitle>
                  <StatusChip status={job.status} size="sm" />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Users className="h-4 w-4" />
                    <span>{job.total_candidates_matched} candidates matched</span>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Experience: {job.experience_range.min}-{job.experience_range.max} years
                  </div>
                </div>
                
                <div className="space-y-2">
                  <p className="text-xs font-medium text-muted-foreground">Required Skills</p>
                  <div className="flex flex-wrap gap-1">
                    {job.required_skills.slice(0, 3).map((skill) => (
                      <Badge key={skill} variant="secondary" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                    {job.required_skills.length > 3 && (
                      <Badge variant="secondary" className="text-xs">
                        +{job.required_skills.length - 3}
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 min-w-0"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewDetails(job.id);
                    }}
                  >
                    View Details
                    <ExternalLink className="h-4 w-4 ml-2" />
                  </Button>
                  {job.status === "closed" && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => handleReopen(job.id, e)}
                      title="Reopen job (make available to candidates)"
                    >
                      <RotateCcw className="h-4 w-4 mr-1" />
                      Reopen
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={(e) => handleDelete(job.id, e)}
                    className="text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

