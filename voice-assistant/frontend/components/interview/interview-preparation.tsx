"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Building,
  MapPin,
  CurrencyDollar,
  Star,
  Microphone,
  Headphones,
  VideoCamera,
  CheckCircle,
} from "@phosphor-icons/react";

interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  salary: string;
  match: number;
  description: string;
}

interface InterviewPreparationProps {
  selectedJob: Job;
  onStartInterview: () => void;
  onBackToJobs: () => void;
}

export const InterviewPreparation = ({
  selectedJob,
  onStartInterview,
  onBackToJobs,
}: InterviewPreparationProps) => {
  const [isReady, setIsReady] = useState(false);
  const [micPermission, setMicPermission] = useState(false);
  const [speakerPermission, setSpeakerPermission] = useState(false);
  const [cameraPermission, setCameraPermission] = useState(false);

  const checkPermissions = async () => {
    try {
      // Check microphone permission
      const micStream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      setMicPermission(true);
      micStream.getTracks().forEach((track) => track.stop());

      // Check speaker permission (this is usually always available)
      setSpeakerPermission(true);

      // Check camera permission (optional)
      try {
        const cameraStream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        setCameraPermission(true);
        cameraStream.getTracks().forEach((track) => track.stop());
      } catch (cameraError) {
        console.log("Camera permission not granted, but this is optional");
        setCameraPermission(false);
      }

      setIsReady(true);
    } catch (error) {
      console.error("Permission check failed:", error);
      alert(
        "Please allow microphone permissions to continue with the interview. Camera is optional.",
      );
    }
  };

  const handleStartInterview = async () => {
    if (!isReady) {
      await checkPermissions();
      return;
    }

    if (isReady) {
      // Clear any previous interview results from localStorage
      Object.keys(localStorage).forEach((key) => {
        if (key.startsWith("interview_result_")) {
          localStorage.removeItem(key);
        }
      });

      onStartInterview();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-4xl mx-auto space-y-6"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold mb-2">Interview Preparation</h2>
        <p className="text-muted-foreground">
          Get ready for your AI interview for the selected position
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Job Details Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Selected Position</span>
              <div className="flex items-center space-x-1 bg-green-100 text-green-700 px-2 py-1 rounded-full">
                <Star className="h-4 w-4 fill-current" />
                <span className="text-sm font-medium">
                  {selectedJob.match}% Match
                </span>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="text-xl font-semibold mb-2">
                {selectedJob.title}
              </h3>
              <div className="space-y-2 text-sm text-muted-foreground">
                <div className="flex items-center space-x-2">
                  <Building className="h-4 w-4" />
                  <span>{selectedJob.company}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4" />
                  <span>{selectedJob.location}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CurrencyDollar className="h-4 w-4" />
                  <span>{selectedJob.salary}</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">Job Description</h4>
              <p className="text-sm text-muted-foreground">
                {selectedJob.description}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Interview Setup Card */}
        <Card>
          <CardHeader>
            <CardTitle>Interview Setup</CardTitle>
            <CardDescription>
              Ensure your equipment is ready for the voice interview
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div
                className={`flex items-center space-x-3 p-3 rounded-lg border ${
                  micPermission
                    ? "border-green-200 bg-green-50"
                    : "border-gray-200"
                }`}
              >
                <Microphone
                  className={`h-5 w-5 ${micPermission ? "text-green-600" : "text-gray-400"}`}
                />
                <div className="flex-1">
                  <p className="font-medium">Microphone</p>
                  <p className="text-sm text-muted-foreground">
                    {micPermission
                      ? "Permission granted"
                      : 'Click "Check Permissions" to enable'}
                  </p>
                </div>
                {micPermission && (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                )}
              </div>

              <div
                className={`flex items-center space-x-3 p-3 rounded-lg border ${
                  speakerPermission
                    ? "border-green-200 bg-green-50"
                    : "border-gray-200"
                }`}
              >
                <Headphones
                  className={`h-5 w-5 ${speakerPermission ? "text-green-600" : "text-gray-400"}`}
                />
                <div className="flex-1">
                  <p className="font-medium">Speakers/Headphones</p>
                  <p className="text-sm text-muted-foreground">
                    {speakerPermission ? "Ready" : "Will be checked"}
                  </p>
                </div>
                {speakerPermission && (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                )}
              </div>

              <div
                className={`flex items-center space-x-3 p-3 rounded-lg border ${
                  cameraPermission
                    ? "border-green-200 bg-green-50"
                    : "border-gray-200"
                }`}
              >
                <VideoCamera
                  className={`h-5 w-5 ${cameraPermission ? "text-green-600" : "text-gray-400"}`}
                />
                <div className="flex-1">
                  <p className="font-medium">Camera (Optional)</p>
                  <p className="text-sm text-muted-foreground">
                    {cameraPermission
                      ? "Permission granted"
                      : "Optional for video feedback"}
                  </p>
                </div>
                {cameraPermission && (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                )}
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-2">Interview Tips</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Find a quiet environment for the best experience</li>
                <li>• Speak clearly and at a normal pace</li>
                <li>• Take your time to think before answering</li>
                <li>• The AI will ask relevant questions based on the job</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex items-center justify-center space-x-4 pt-6">
        <Button variant="outline" onClick={onBackToJobs} size="lg">
          Back to Jobs
        </Button>
        <Button onClick={handleStartInterview} size="lg" disabled={false}>
          {isReady ? "Start Interview" : "Check Permissions & Continue"}
        </Button>
      </div>

      {!isReady && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center text-sm text-muted-foreground"
        >
          <p>
            Click "Check Permissions & Start" to enable your microphone and
            begin the interview
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};
