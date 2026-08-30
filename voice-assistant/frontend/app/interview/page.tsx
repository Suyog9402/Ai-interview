"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { APP_CONFIG_DEFAULTS } from "../../app-config";
import { App } from "@/components/app";

export default function InterviewPage() {
  const router = useRouter();
  const [selectedJob, setSelectedJob] = useState<any>(null);

  useEffect(() => {
    // Get the selected job from localStorage
    const jobJson = localStorage.getItem("selectedJob");
    if (jobJson) {
      try {
        const job = JSON.parse(jobJson);
        setSelectedJob(job);
      } catch (error) {
        console.error("Error parsing selected job:", error);
        // Redirect back to jobs if there's an error
        router.push("/jobs");
      }
    } else {
      // Redirect to jobs page if no job is selected
      router.push("/jobs");
    }
  }, [router]);

  if (!selectedJob) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading interview setup...</p>
        </div>
      </div>
    );
  }

  // Update the app config with the selected job details
  const appConfig = {
    ...APP_CONFIG_DEFAULTS,
    jobTitle: selectedJob.title,
    companyName: selectedJob.company || "AI Interview Assistant",
    jobDescription: selectedJob.description,
  };

  return <App appConfig={appConfig} />;
}
