"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ArrowLeft, AlertCircle } from "lucide-react";
import { UserIntelligenceHeader } from "@/components/admin/user-intelligence-header";
import { NeuralSummaryCards } from "@/components/admin/neural-summary-cards";
import { AITimelineView } from "@/components/admin/ai-timeline-view";
import { AIInsightPanel } from "@/components/admin/ai-insight-panel";

export default function UserDetailPage() {
  const params = useParams();
  const router = useRouter();
  const userId = parseInt(params.id as string);
  
  const [userDetails, setUserDetails] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (userId) {
      loadUserDetails();
    }
  }, [userId]);

  const loadUserDetails = async () => {
    try {
      setIsLoading(true);
      const details = await apiClient.getUserDetails(userId);
      setUserDetails(details);
      setError("");
    } catch (err) {
      console.error("Error loading user details:", err);
      setError(err instanceof Error ? err.message : "Failed to load user details");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading user details...</p>
        </div>
      </div>
    );
  }

  if (error || !userDetails) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <p className="text-foreground">{error || "User not found"}</p>
          <Button
            onClick={() => router.push("/admin/users")}
            className="mt-4"
            variant="outline"
          >
            Back to Users
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Button
        onClick={() => router.push("/admin/users")}
        variant="ghost"
        className="mb-2"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Users
      </Button>

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">User Details</h1>
        <p className="text-muted-foreground mt-2">
          Complete information and interview history for {userDetails.email || userDetails.username}
        </p>
      </div>

      {/* Hero Intelligence Header */}
      <UserIntelligenceHeader userDetails={userDetails} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Neural Summary Cards */}
          <NeuralSummaryCards userDetails={userDetails} />

          {/* AI Timeline View */}
          <AITimelineView 
            interviewHistory={userDetails.interview_history || []}
            userId={userId}
          />
        </div>

        {/* Right Column - AI Insights */}
        <div className="lg:col-span-1">
          <AIInsightPanel userDetails={userDetails} />
        </div>
      </div>
    </div>
  );
}

