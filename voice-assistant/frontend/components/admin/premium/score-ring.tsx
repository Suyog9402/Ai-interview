"use client";

import { cn } from "@/lib/utils";

interface ScoreRingProps {
  score: number;
  maxScore?: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export function ScoreRing({ 
  score, 
  maxScore = 100, 
  size = 'md',
  showLabel = true,
  className 
}: ScoreRingProps) {
  const percentage = (score / maxScore) * 100;
  const circumference = 2 * Math.PI * 45; // radius = 45
  const offset = circumference - (percentage / 100) * circumference;

  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32',
  };

  const strokeWidth = size === 'sm' ? 4 : size === 'md' ? 6 : 8;

  const getColor = () => {
    if (percentage >= 80) return 'text-green-500 stroke-green-500';
    if (percentage >= 60) return 'text-yellow-500 stroke-yellow-500';
    return 'text-red-500 stroke-red-500';
  };

  return (
    <div className={cn("relative inline-flex items-center justify-center", sizeClasses[size], className)}>
      <svg className="transform -rotate-90" width="100%" height="100%">
        <circle
          cx="50%"
          cy="50%"
          r="45%"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="none"
          className="text-muted opacity-20"
        />
        <circle
          cx="50%"
          cy="50%"
          r="45%"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={cn("transition-all duration-500", getColor())}
        />
      </svg>
      {showLabel && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className={cn("font-bold", getColor(), size === 'sm' ? 'text-lg' : size === 'md' ? 'text-2xl' : 'text-3xl')}>
              {score.toFixed(0)}
            </div>
            {maxScore !== 100 && (
              <div className="text-xs text-muted-foreground">/ {maxScore}</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

