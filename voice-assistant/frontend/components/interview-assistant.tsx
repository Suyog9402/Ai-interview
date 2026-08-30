"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { useRouter } from "next/navigation";
import { ResumeUpload } from "@/components/resume/resume-upload";
import { JobRecommendations } from "@/components/jobs/job-recommendations";
import { InterviewPreparation } from "@/components/interview/interview-preparation";
import { App } from "@/components/app";
import { Button } from "@/components/ui/button";
import {
  SignOut,
  User,
  FileText,
  Building,
  Microphone,
} from "@phosphor-icons/react";

import { useUser } from "@/lib/user-context";

type View = "resume" | "preparation";

// Remove this interface as we'll use the User type from the API

interface ResumeData {
  name: string;
  email: string;
  skills: string[];
  experience: string;
  education: string;
}

interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  salary: string;
  match: number;
  description: string;
}

export const InterviewAssistant = () => {
  const router = useRouter();
  const { user, logout } = useUser();
  const [currentView, setCurrentView] = useState<View>("resume");
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [jobRecommendations, setJobRecommendations] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleResumeUploaded = (data: ResumeData) => {
    setResumeData(data);
    // Don't change view here, the resume upload will handle redirect to /jobs
  };

  const handleJobRecommendations = (jobs: Job[]) => {
    setJobRecommendations(jobs);
  };

  const handleStartInterview = (job: Job) => {
    setSelectedJob(job);
    setCurrentView("preparation");
  };

  const handleBeginInterview = () => {
    // Navigate to the dedicated interview page
    router.push("/interview");
  };

  const handleLogout = () => {
    logout();
    setResumeData(null);
    setJobRecommendations([]);
    setSelectedJob(null);
    setCurrentView("resume");
    router.push("/");
  };

  const renderProgressBar = () => {
    const steps = [
      { key: "resume", label: "Resume", icon: FileText },
      { key: "jobs", label: "Jobs", icon: Building },
      { key: "preparation", label: "Setup", icon: Microphone },
    ];

    const currentIndex = steps.findIndex((step) => step.key === currentView);

    return (
      <div className="w-full max-w-2xl mx-auto mb-4 sm:mb-8 px-2 sm:px-0">
        <div className="flex items-center justify-center">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isActive = index <= currentIndex;
            const isCompleted = index < currentIndex;

            return (
              <div key={step.key} className="flex items-center">
                <div
                  className={`flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-full border-2 ${
                    isCompleted
                      ? "bg-green-500 border-green-500 text-white"
                      : isActive
                        ? "bg-blue-500 border-blue-500 text-white"
                        : "bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-400 dark:text-gray-500"
                  }`}
                >
                  <Icon className="h-4 w-4 sm:h-5 sm:w-5" />
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`w-8 sm:w-12 h-0.5 sm:h-1 mx-1 sm:mx-2 ${isCompleted ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"}`}
                  />
                )}
              </div>
            );
          })}
        </div>
        <div className="flex justify-center mt-1.5 sm:mt-2 text-xs sm:text-sm text-muted-foreground space-x-4 sm:space-x-8">
          {steps.map((step, index) => (
            <span key={`label-${step.key}`} className="text-center">
              {step.label}
            </span>
          ))}
        </div>
      </div>
    );
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case "resume":
        return <ResumeUpload onResumeUploaded={handleResumeUploaded} />;

      case "preparation":
        return selectedJob ? (
          <InterviewPreparation
            selectedJob={selectedJob}
            onStartInterview={handleBeginInterview}
            onBackToJobs={() => setCurrentView("resume")}
          />
        ) : null;

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      {user && (
        <header className="border-b bg-card">
          <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-12 sm:h-16 py-2 sm:py-0">
              <div className="flex items-center space-x-2 sm:space-x-4">
                <h1 className="text-base sm:text-xl font-semibold">
                  AI Interview Assistant
                </h1>
                {user && (
                  <div className="hidden sm:flex items-center space-x-2 text-xs sm:text-sm text-muted-foreground">
                    <User className="h-3 w-3 sm:h-4 sm:w-4" />
                    <span>Welcome, {user.full_name || user.username}</span>
                  </div>
                )}
              </div>
              <div className="flex items-center space-x-2 sm:space-x-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogout}
                  className="flex items-center space-x-1 sm:space-x-2 h-7 sm:h-9 text-xs sm:text-sm px-2 sm:px-4"
                >
                  <SignOut className="h-3 w-3 sm:h-4 sm:w-4" />
                  <span>Logout</span>
                </Button>
              </div>
            </div>
          </div>
        </header>
      )}

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-3 sm:px-6 lg:px-8 py-4 sm:py-8">
        <div className="w-full max-w-4xl">
          <AnimatePresence mode="wait">
            <div key="progress-bar">{renderProgressBar()}</div>
            <div key="current-view">{renderCurrentView()}</div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
};
