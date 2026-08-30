// types/admin.ts
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  total_interviews?: number;
  average_score?: number;
  best_score?: number;
  latest_score?: number;
  interview_history?: Interview[];
  matched_jobs?: MatchedJob[];
  flags?: string[];
  notes?: string;
}

export interface Interview {
  id: string;
  session_id: string;
  user_id: number;
  candidate_name?: string;
  job_title?: string;
  status: 'scheduled' | 'running' | 'completed' | 'failed';
  total_score?: number;
  max_score?: number;
  percentage?: number;
  duration_minutes?: number;
  created_at: string;
  risk_flags?: string[];
  transcript?: TranscriptSegment[];
  evaluation?: Evaluation;
  events?: SystemEvent[];
}

export interface TranscriptSegment {
  speaker: 'interviewer' | 'candidate';
  text: string;
  timestamp: string;
}

export interface Evaluation {
  overall_score: number;
  rubric_breakdown: RubricScore[];
  pass: boolean;
  recommendation: 'hire' | 'maybe' | 'reject';
  strengths: string[];
  weaknesses: string[];
  suspicious_patterns?: string[];
}

export interface RubricScore {
  criterion: string;
  score: number;
  max_score: number;
  feedback: string;
}

export interface Job {
  id: number;
  title: string;
  description: string;
  required_skills: string[];
  nice_to_have_skills: string[];
  experience_range: { min: number; max: number };
  status: 'open' | 'closed';
  total_candidates_matched: number;
  match_distribution?: MatchDistribution[];
  top_candidates?: TopCandidate[];
}

export interface MatchedJob {
  job_id: number;
  job_title: string;
  match_percentage: number;
  key_skills: string[];
}

export interface TopCandidate {
  user_id: number;
  name: string;
  match_percentage: number;
  key_skills: string[];
}

export interface MatchDistribution {
  range: string;
  count: number;
}

export interface Automation {
  id: string;
  name: string;
  description: string;
  trigger: string;
  actions: string[];
  status: 'enabled' | 'disabled';
  last_run?: string;
  success_rate: number;
  recent_errors?: string[];
  logs?: AutomationLog[];
}

export interface AutomationLog {
  id: string;
  timestamp: string;
  status: 'success' | 'error';
  message: string;
  details?: any;
}

export interface SystemEvent {
  id: string;
  type: 'resume_parsed' | 'interview_completed' | 'flagged_event' | 'webhook_triggered' | 'automation_ran';
  timestamp: string;
  description: string;
  metadata?: any;
}

export interface ActivityEvent {
  id: string;
  type: SystemEvent['type'];
  timestamp: string;
  description: string;
  user_id?: number;
  interview_id?: string;
  metadata?: any;
}

export interface DashboardStats {
  total_users: number;
  active_users: number;
  interviews_today: number;
  interviews_this_week: number;
  total_interviews: number;
  avg_score: number;
  pass_rate: number;
  avg_interview_duration: number;
}

export interface PipelineMetrics {
  resume_uploaded: number;
  parsed: number;
  matched: number;
  interview_started: number;
  completed: number;
  hired_recommended: number;
}

export interface SystemHealth {
  queue_size: number;
  failure_rate: number;
  avg_latency_ms: number;
  token_usage_today: number;
  cost_today: number;
  uptime_status: 'healthy' | 'degraded' | 'down';
}

