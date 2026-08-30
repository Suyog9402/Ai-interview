"use client";

import * as React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface SkillData {
  problemSolving: number;
  systemDesign: number;
  codingLogic: number;
  communication: number;
  depthOfKnowledge: number;
  realWorldThinking: number;
}

interface SkillRadarChartProps {
  userSkills: SkillData;
  benchmarkSkills?: SkillData;
  comparisonSkills?: SkillData;
  showComparison?: boolean;
  className?: string;
}

const SKILL_LABELS = [
  "Problem Solving",
  "System Design",
  "Coding/Logic",
  "Communication",
  "Depth of Knowledge",
  "Real-world Thinking",
];

const SKILL_KEYS: (keyof SkillData)[] = [
  "problemSolving",
  "systemDesign",
  "codingLogic",
  "communication",
  "depthOfKnowledge",
  "realWorldThinking",
];

export function SkillRadarChart({
  userSkills,
  benchmarkSkills,
  comparisonSkills,
  showComparison = false,
  className,
}: SkillRadarChartProps) {
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  const [dimensions, setDimensions] = React.useState({ width: 400, height: 400 });

  React.useEffect(() => {
    const updateDimensions = () => {
      if (canvasRef.current?.parentElement) {
        const parent = canvasRef.current.parentElement;
        const size = Math.min(parent.clientWidth - 40, 500);
        setDimensions({ width: size, height: size });
      }
    };

    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const { width, height } = dimensions;
    canvas.width = width;
    canvas.height = height;

    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 40;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw grid circles
    ctx.strokeStyle = "#e5e7eb";
    ctx.lineWidth = 1;
    for (let i = 1; i <= 5; i++) {
      ctx.beginPath();
      ctx.arc(centerX, centerY, (radius * i) / 5, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Draw grid lines (spokes)
    const numSkills = SKILL_LABELS.length;
    ctx.strokeStyle = "#e5e7eb";
    ctx.lineWidth = 1;
    for (let i = 0; i < numSkills; i++) {
      const angle = (Math.PI * 2 * i) / numSkills - Math.PI / 2;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(x, y);
      ctx.stroke();
    }

    // Draw benchmark (if provided)
    if (benchmarkSkills) {
      drawSkillPolygon(ctx, centerX, centerY, radius, benchmarkSkills, "#94a3b8", 0.3, true);
    }

    // Draw comparison (if provided)
    if (comparisonSkills && showComparison) {
      drawSkillPolygon(ctx, centerX, centerY, radius, comparisonSkills, "#f59e0b", 0.4, true);
    }

    // Draw user skills
    drawSkillPolygon(ctx, centerX, centerY, radius, userSkills, "#3b82f6", 0.6, false);

    // Draw labels
    ctx.fillStyle = "#374151";
    ctx.font = "12px system-ui";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    for (let i = 0; i < numSkills; i++) {
      const angle = (Math.PI * 2 * i) / numSkills - Math.PI / 2;
      const labelRadius = radius + 25;
      const x = centerX + labelRadius * Math.cos(angle);
      const y = centerY + labelRadius * Math.sin(angle);

      ctx.fillText(SKILL_LABELS[i], x, y);
    }

    // Draw value labels on axes
    ctx.fillStyle = "#6b7280";
    ctx.font = "10px system-ui";
    for (let i = 1; i <= 5; i++) {
      const value = i * 20;
      const labelRadius = (radius * i) / 5;
      ctx.fillText(value.toString(), centerX + labelRadius + 15, centerY);
    }
  }, [dimensions, userSkills, benchmarkSkills, comparisonSkills, showComparison]);

  const drawSkillPolygon = (
    ctx: CanvasRenderingContext2D,
    centerX: number,
    centerY: number,
    radius: number,
    skills: SkillData,
    color: string,
    alpha: number,
    isDashed: boolean
  ) => {
    const numSkills = SKILL_KEYS.length;
    const points: { x: number; y: number }[] = [];

    for (let i = 0; i < numSkills; i++) {
      const skillKey = SKILL_KEYS[i];
      const skillValue = skills[skillKey];
      const normalizedValue = skillValue / 100; // Normalize to 0-1
      const angle = (Math.PI * 2 * i) / numSkills - Math.PI / 2;
      const r = radius * normalizedValue;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      points.push({ x, y });
    }

    // Draw filled polygon
    ctx.fillStyle = color;
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.closePath();
    ctx.fill();

    // Draw outline
    ctx.globalAlpha = 1;
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    if (isDashed) {
      ctx.setLineDash([5, 5]);
    } else {
      ctx.setLineDash([]);
    }
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.closePath();
    ctx.stroke();
    ctx.setLineDash([]);
  };

  const handleDownload = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const link = document.createElement("a");
    link.download = "skill-radar-chart.png";
    link.href = canvas.toDataURL("image/png");
    link.click();
  };

  // Calculate skill values from user data (mock calculation - adjust based on actual data)
  const calculateSkills = (): SkillData => {
    // This is a placeholder - in real implementation, you'd extract this from interview data
    // For now, we'll use average_score as a base and distribute it
    const baseScore = 70; // Default if no data
    
    return {
      problemSolving: baseScore + Math.random() * 20 - 10,
      systemDesign: baseScore + Math.random() * 20 - 10,
      codingLogic: baseScore + Math.random() * 20 - 10,
      communication: baseScore + Math.random() * 20 - 10,
      depthOfKnowledge: baseScore + Math.random() * 20 - 10,
      realWorldThinking: baseScore + Math.random() * 20 - 10,
    };
  };

  const actualSkills = userSkills || calculateSkills();

  return (
    <div className={className}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Skill Breakdown</h3>
        <Button variant="outline" size="sm" onClick={handleDownload}>
          <Download className="h-4 w-4 mr-2" />
          Download
        </Button>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Radar Chart */}
        <div className="flex-1 flex justify-center">
          <canvas
            ref={canvasRef}
            className="border rounded-lg bg-white"
            style={{ maxWidth: "100%", height: "auto" }}
          />
        </div>

        {/* Legend and Stats */}
        <div className="md:w-64 space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-2">Legend</h4>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-blue-500 rounded"></div>
                <span className="text-sm">User Skills</span>
              </div>
              {benchmarkSkills && (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-slate-400 rounded"></div>
                  <span className="text-sm">Role Benchmark</span>
                </div>
              )}
              {comparisonSkills && showComparison && (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-amber-500 rounded"></div>
                  <span className="text-sm">Top Performers Avg</span>
                </div>
              )}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium mb-2">Skill Scores</h4>
            <div className="space-y-2">
              {SKILL_KEYS.map((key, index) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    {SKILL_LABELS[index]}
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary transition-all"
                        style={{
                          width: `${actualSkills[key]}%`,
                        }}
                      />
                    </div>
                    <Badge variant="secondary" className="text-xs w-12 text-center">
                      {actualSkills[key].toFixed(0)}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Strengths & Weaknesses */}
          <div>
            <h4 className="text-sm font-medium mb-2">Analysis</h4>
            <div className="space-y-2">
              <div>
                <span className="text-xs text-green-600 font-medium">Strengths:</span>
                <div className="text-xs text-muted-foreground mt-1">
                  {Object.entries(actualSkills)
                    .filter(([_, value]) => value >= 75)
                    .map(([key]) => SKILL_LABELS[SKILL_KEYS.indexOf(key as keyof SkillData)])
                    .join(", ") || "None identified"}
                </div>
              </div>
              <div>
                <span className="text-xs text-red-600 font-medium">Weaknesses:</span>
                <div className="text-xs text-muted-foreground mt-1">
                  {Object.entries(actualSkills)
                    .filter(([_, value]) => value < 60)
                    .map(([key]) => SKILL_LABELS[SKILL_KEYS.indexOf(key as keyof SkillData)])
                    .join(", ") || "None identified"}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

