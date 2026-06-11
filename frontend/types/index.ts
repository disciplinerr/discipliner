export interface User {
  id: number;
  email: string;
  created_at: string;
  current_phase: number;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Challenge {
  id: number;
  date: string;
  title: string;
  math_problem: string;
  programming_task: string;
  difficulty: string;
  category: string;
  expected_output_example: string;
  constraints: string;
}

export interface Submission {
  id: number;
  challenge_id: number;
  result: "PASS" | "FAIL" | "PARTIAL" | "PENDING";
  reason: string;
  submitted_at: string;
}

export interface ChallengeHistoryItem {
  challenge: Challenge;
  submissions: Submission[];
}

export type RoutineStatus = "DONE" | "LATE" | "SKIPPED" | null;

export interface RoutineItem {
  item_key: string;
  label: string;
  status: RoutineStatus;
  logged_at: string | null;
}

export interface RoutineDay {
  date: string;
  items: RoutineItem[];
}

export interface RoutineWeek {
  days: RoutineDay[];
}

export interface ReviewCard {
  id: number;
  topic: string;
  phase_id: number;
  repetitions: number;
  interval_days: number;
  due_date: string;
}

export interface ReviewStats {
  total: number;
  due: number;
  reviewed_today: number;
  mature: number;
}

export interface Phase {
  id: number;
  number: number;
  name: string;
  weeks: string;
  topics: string[];
  exercises: string[];
}

export interface PhaseProgress {
  phase: Phase;
  started_at: string | null;
  completed_at: string | null;
  summary: string;
  is_current: boolean;
}

export interface TrailProgress {
  current_phase: number;
  phases: PhaseProgress[];
}

export interface PreviewChallenge {
  title: string;
  math_problem: string;
  programming_task: string;
  difficulty: string;
  category: string;
  expected_output_example: string;
  constraints: string;
}

export interface ExecuteResult {
  output: string;
  error: boolean;
}

export interface RoutineDaySummary {
  date: string;
  done: number;
  total: number;
  skipped: number;
}

export interface RoutineMonth {
  year: number;
  month: number;
  days: RoutineDaySummary[];
}

export interface UserRoutineItem {
  id: number;
  item_key: string;
  label: string;
  is_system: boolean;
  is_active: boolean;
  position: number;
}
