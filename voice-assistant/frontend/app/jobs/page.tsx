"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Building, ArrowLeft, FileText } from "@phosphor-icons/react";
import { useUser } from "@/lib/user-context";
import { JobRecommendations } from "@/components/jobs/job-recommendations";

export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  salary: string;
  match: number;
  description: string;
  fullAnalysis?: string;
  keyMatches?: string[];
  missingSkills?: string[];
  recommendations?: string;
  jdSource?: string;
}

export default function JobsPage() {
  const router = useRouter();
  const { user, isLoading } = useUser();
  const [jobRecommendations, setJobRecommendations] = useState<Job[]>([]);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }

    // Fetch job recommendations from localStorage or API
    const fetchJobRecommendations = () => {
      try {
        const savedJobs = localStorage.getItem("jobRecommendations");
        if (savedJobs) {
          setJobRecommendations(JSON.parse(savedJobs));
        }
      } catch (error) {
        console.error("Error loading job recommendations:", error);
      } finally {
        setIsLoadingJobs(false);
      }
    };

    fetchJobRecommendations();
  }, [user, isLoading, router]);

  if (isLoading || isLoadingJobs) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading jobs...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
          <div className="flex flex-row items-center justify-between gap-2 sm:gap-4 h-auto sm:h-16 py-2 sm:py-0">
            {/* Left side: Back button only on mobile, Back + Title on desktop */}
            <div className="flex items-center space-x-2 sm:space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push("/resume")}
                className="flex items-center space-x-1 sm:space-x-2 h-8 sm:h-9"
              >
                <ArrowLeft className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline text-xs sm:text-sm">Back</span>
              </Button>
              {/* Title only visible on desktop */}
              <h1 className="hidden sm:flex text-base sm:text-xl font-semibold items-center">
                <Building className="h-4 w-4 sm:h-5 sm:w-5 mr-1.5 sm:mr-2" />
                <span className="break-words text-sm sm:text-base">Recommended Jobs</span>
              </h1>
            </div>
            
            {/* Right side: Title on mobile, Upload button on desktop */}
            <div className="flex items-center gap-2 sm:gap-0">
              {/* Title visible only on mobile, positioned at right */}
              <h1 className="flex sm:hidden text-sm font-semibold items-center">
                <Building className="h-4 w-4 mr-1.5" />
                <span className="break-words">Recommended Jobs</span>
              </h1>
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push("/resume")}
                className="flex items-center space-x-1.5 sm:space-x-2 h-8 sm:h-9 text-xs sm:text-sm px-2 sm:px-4 shrink-0"
              >
                <FileText className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">Upload New Resume</span>
                <span className="sm:hidden">Upload</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-3 sm:py-8">
        {jobRecommendations.length > 0 ? (
          <JobRecommendations
            jobs={jobRecommendations}
            onJobSelect={async (job) => {
              try {
                // Automatically set the JD file for the LiveKit worker
                if (job.jdSource) {
                  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api/v1"}/interview/select-jd`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                      jd_filename: job.jdSource
                    })
                  });

                  if (!response.ok) {
                    console.warn('Failed to set JD file, but continuing with interview');
                  } else {
                    console.log('Successfully set JD file for interview');
                  }
                }

                // Save selected job to localStorage for the interview page
                localStorage.setItem("selectedJob", JSON.stringify(job));
                // Navigate to interview page
                router.push("/interview");
              } catch (error) {
                console.error('Error setting JD file:', error);
                // Continue with interview even if JD setting fails
                localStorage.setItem("selectedJob", JSON.stringify(job));
                router.push("/interview");
              }
            }}
          />
        ) : (
          <div className="text-center py-12">
            <Building className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">
              No job recommendations found
            </h3>
            <p className="text-muted-foreground mb-6">
              Upload your resume to get personalized job recommendations.
            </p>
            <Button onClick={() => router.push("/resume")}>
              Upload Resume
            </Button>
          </div>
        )}
      </main>
    </div>
  );
}
