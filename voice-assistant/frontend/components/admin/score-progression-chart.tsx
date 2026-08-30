"use client";

import * as React from "react";

interface ProgressionData {
  date: string;
  score: number;
}

interface ScoreProgressionChartProps {
  data: ProgressionData[];
}

export function ScoreProgressionChart({ data }: ScoreProgressionChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <p>No progression data available</p>
      </div>
    );
  }

  const maxScore = Math.max(...data.map((d) => d.score), 100);
  const minScore = Math.min(...data.map((d) => d.score), 0);
  const range = maxScore - minScore || 1;
  const width = 600;
  const height = 200;
  const padding = 40;
  const chartWidth = width - padding * 2;
  const chartHeight = height - padding * 2;

  const points = data.map((d, i) => {
    const x = padding + (i / Math.max(data.length - 1, 1)) * chartWidth;
    const y =
      padding +
      chartHeight -
      ((d.score - minScore) / range) * chartHeight;
    return { x, y, score: d.score, date: d.date };
  });

  const pathData = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
    .join(" ");

  return (
    <div className="w-full overflow-x-auto">
      <svg width={width} height={height} className="border rounded">
        {/* Grid lines */}
        {[0, 25, 50, 75, 100].map((score) => {
          const y =
            padding +
            chartHeight -
            ((score - minScore) / range) * chartHeight;
          return (
            <g key={score}>
              <line
                x1={padding}
                y1={y}
                x2={width - padding}
                y2={y}
                stroke="currentColor"
                strokeWidth="0.5"
                className="text-muted-foreground opacity-30"
              />
              <text
                x={padding - 10}
                y={y + 4}
                textAnchor="end"
                className="text-xs fill-muted-foreground"
              >
                {score}%
              </text>
            </g>
          );
        })}

        {/* Line */}
        <path
          d={pathData}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-primary"
        />

        {/* Points */}
        {points.map((point, i) => (
          <g key={i}>
            <circle
              cx={point.x}
              cy={point.y}
              r="4"
              fill="currentColor"
              className="text-primary"
            />
            <title>
              {new Date(point.date).toLocaleDateString()}: {point.score.toFixed(1)}%
            </title>
          </g>
        ))}

        {/* X-axis labels */}
        {data.map((d, i) => {
          if (data.length > 10 && i % Math.ceil(data.length / 5) !== 0) return null;
          const x = padding + (i / (data.length - 1 || 1)) * chartWidth;
          return (
            <text
              key={i}
              x={x}
              y={height - padding + 20}
              textAnchor="middle"
              className="text-xs fill-muted-foreground"
            >
              {new Date(d.date).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
              })}
            </text>
          );
        })}
      </svg>
    </div>
  );
}

