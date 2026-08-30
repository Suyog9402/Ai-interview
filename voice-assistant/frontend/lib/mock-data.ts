// lib/mock-data.ts
// Mock data for development - replace with API calls in production

import {
  User,
  Interview,
  Job,
  Automation,
  DashboardStats,
  PipelineMetrics,
  SystemHealth,
  ActivityEvent,
} from "@/types/admin";

export const mockUsers: User[] = [
  {
    id: 1,
    email: "john.doe@example.com",
    username: "johndoe",
    full_name: "John Doe",
    is_active: true,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(),
    total_interviews: 5,
    average_score: 78.5,
    best_score: 92,
    latest_score: 85,
  },
  {
    id: 2,
    email: "jane.smith@example.com",
    username: "janesmith",
    full_name: "Jane Smith",
    is_active: true,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 15).toISOString(),
    total_interviews: 3,
    average_score: 65.2,
    best_score: 72,
    latest_score: 68,
  },
  // Add more mock users as needed
];

export const mockInterviews: Interview[] = [
  {
    id: "1",
    session_id: "session_123",
    user_id: 1,
    candidate_name: "John Doe",
    job_title: "Senior Frontend Developer",
    status: "completed",
    total_score: 85,
    max_score: 100,
    percentage: 85,
    duration_minutes: 45,
    created_at: new Date().toISOString(),
    risk_flags: [],
    transcript: [
      {
        speaker: "interviewer",
        text: "Could you please introduce yourself and tell me a bit about your background?",
        timestamp: "00:00:05",
      },
      {
        speaker: "candidate",
        text: "Hi, I'm John Doe. I've been working as a frontend developer for the past 5 years...",
        timestamp: "00:00:15",
      },
    ],
    evaluation: {
      overall_score: 85,
      rubric_breakdown: [
        {
          criterion: "Technical Knowledge",
          score: 90,
          max_score: 100,
          feedback: "Strong understanding of React and modern frontend practices",
        },
        {
          criterion: "Problem Solving",
          score: 80,
          max_score: 100,
          feedback: "Good analytical skills, could improve on edge cases",
        },
      ],
      pass: true,
      recommendation: "hire",
      strengths: ["Strong technical foundation", "Good communication"],
      weaknesses: ["Could improve on system design"],
    },
  },
];

export const mockJobs: Job[] = [
  {
    id: 1,
    title: "Senior Frontend Developer",
    description: "Looking for an experienced frontend developer with React expertise",
    required_skills: ["React", "TypeScript", "Next.js", "Tailwind CSS"],
    nice_to_have_skills: ["GraphQL", "Redux", "Jest"],
    experience_range: { min: 5, max: 10 },
    status: "open",
    total_candidates_matched: 45,
    match_distribution: [
      { range: "80-100%", count: 12 },
      { range: "60-79%", count: 20 },
      { range: "40-59%", count: 10 },
      { range: "0-39%", count: 3 },
    ],
  },
];

export const mockAutomations: Automation[] = [
  {
    id: "1",
    name: "Resume Upload → Parse → Match → Schedule",
    description: "Automatically processes uploaded resumes and schedules interviews",
    trigger: "resume_uploaded",
    actions: ["parse_resume", "match_to_jobs", "schedule_interview", "notify_candidate"],
    status: "enabled",
    last_run: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    success_rate: 98.5,
    recent_errors: [],
  },
];

export const mockDashboardStats: DashboardStats = {
  total_users: 1250,
  active_users: 890,
  interviews_today: 45,
  interviews_this_week: 320,
  total_interviews: 5680,
  avg_score: 72.5,
  pass_rate: 68.3,
  avg_interview_duration: 42,
};

export const mockPipelineMetrics: PipelineMetrics = {
  resume_uploaded: 1250,
  parsed: 1180,
  matched: 950,
  interview_started: 720,
  completed: 680,
  hired_recommended: 145,
};

export const mockSystemHealth: SystemHealth = {
  queue_size: 42,
  failure_rate: 1.2,
  avg_latency_ms: 1200,
  token_usage_today: 125000,
  cost_today: 12.50,
  uptime_status: "healthy",
};

export const mockActivities: ActivityEvent[] = [
  {
    id: "1",
    type: "interview_completed",
    timestamp: new Date().toISOString(),
    description: "Interview completed for John Doe",
    interview_id: "session_123",
  },
  {
    id: "2",
    type: "resume_parsed",
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    description: "Resume parsed successfully",
    user_id: 456,
  },
  {
    id: "3",
    type: "automation_ran",
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    description: "Automation workflow executed",
  },
  {
    id: "4",
    type: "flagged_event",
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    description: "Flagged interview detected",
    interview_id: "session_456",
  },
];

