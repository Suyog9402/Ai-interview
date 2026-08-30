"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Camera, CameraSlash, Eye } from "@phosphor-icons/react";
import { motion } from "motion/react";

interface FaceDetectionToggleProps {
  isActive: boolean;
  onToggle: () => void;
  disabled?: boolean;
  className?: string;
  isCameraRunning?: boolean; // New prop to show camera status
}

export const FaceDetectionToggle: React.FC<FaceDetectionToggleProps> = ({
  isActive,
  onToggle,
  disabled = false,
  className = "",
  isCameraRunning = false,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      className={className}
    >
      <Button
        variant={isActive ? "default" : "outline"}
        size="sm"
        onClick={onToggle}
        disabled={disabled}
        className={`flex items-center gap-2 transition-all duration-200 ${
          isActive && isCameraRunning
            ? "bg-green-600 hover:bg-green-700 text-white"
            : isActive
              ? "bg-blue-600 hover:bg-blue-700 text-white"
              : "hover:bg-blue-50 hover:border-blue-300"
        }`}
      >
        {isActive && isCameraRunning ? (
          <>
            <Eye size={16} className="animate-pulse" />
            <span className="hidden sm:inline">Analyzing...</span>
          </>
        ) : isActive ? (
          <>
            <Camera size={16} />
            <span className="hidden sm:inline">Face Analysis</span>
          </>
        ) : (
          <>
            <CameraSlash size={16} />
            <span className="hidden sm:inline">Enable Face Analysis</span>
          </>
        )}
      </Button>
    </motion.div>
  );
};
