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

export interface EnglishExercise {
  item_id: number;
  exercise_type: "multiple_choice_vocab" | "fill_in_the_blank" | "translate_pt_en" | "translate_en_pt";
  prompt: string;
  choices: string[] | null;
}

export interface EnglishSession {
  items: EnglishExercise[];
  done_today: number;
  due_today: number;
}

export interface EnglishAnswerResult {
  correct: boolean;
  correct_answer: string;
  session_complete: boolean;
}

export interface EnglishStats {
  due_today: number;
  done_today: number;
  pass_rate_7d: number;
  mature_items: number;
  total_items: number;
}

export interface RoutineDayBar {
  date: string;
  done: number;
  total: number;
  pct: number;
}

export interface DashboardStats {
  routine_streak: number;
  routine_7d: RoutineDayBar[];
  english_accuracy_7d: number;
}

// --- Finance ---

export type BudgetGroup = "NEEDS" | "WANTS" | "SAVINGS";
export type TransactionKind = "EXPENSE" | "INCOME";
export type IncomeKind = "SALARY" | "BENEFIT" | "OTHER";

export interface RecurringIncome {
  id: number;
  name: string;
  amount: number;
  kind: IncomeKind;
  is_active: boolean;
}

export interface Category {
  id: number;
  category_key: string;
  name: string;
  emoji: string;
  color: string;
  group: BudgetGroup;
  monthly_budget: number;
  is_system: boolean;
  is_active: boolean;
  position: number;
}

export interface Transaction {
  id: number;
  category_id: number | null;
  description: string;
  amount: number;
  kind: TransactionKind;
  date: string;
}

export interface Bill {
  id: number;
  category_id: number | null;
  name: string;
  amount: number;
  due_day: number;
  is_active: boolean;
}

export interface BillStatus {
  id: number;
  name: string;
  amount: number;
  due_day: number;
  due_date: string;
  category_id: number | null;
  paid: boolean;
  paid_at: string | null;
  overdue: boolean;
}

export interface GroupSpend {
  group: BudgetGroup;
  budget: number;
  spent: number;
  target_pct: number;
  over_budget: boolean;
}

export interface CategorySpend {
  category_id: number;
  name: string;
  emoji: string;
  color: string;
  group: BudgetGroup;
  budget: number;
  spent: number;
  over_budget: boolean;
}

export type SpendingStatus = "healthy" | "tight" | "over" | "unknown";

export interface RecommendationGroup {
  group: BudgetGroup;
  pct: number;
  amount: number;
}

export interface RecommendationItem {
  key: string;
  group: BudgetGroup;
  pct: number;
  amount: number;
}

export interface Recommendation {
  income: number;
  actual_spending: number;
  leftover: number;
  savings_rate: number;
  status: SpendingStatus;
  groups: RecommendationGroup[];
  items: RecommendationItem[];
}

export interface FinanceOverview {
  year: number;
  month: number;
  income: number;
  expense: number;
  balance: number;
  savings_rate: number;
  recurring_income: number;
  total_income: number;
  total_spending: number;
  net: number;
  recommendation: Recommendation;
  total_budget: number;
  bills_total: number;
  bills_paid: number;
  bills_pending: number;
  bills_overdue: number;
  installments_month: number;
  installments_count: number;
  installments_outstanding: number;
  groups: GroupSpend[];
  categories: CategorySpend[];
}

export interface Installment {
  id: number;
  category_id: number | null;
  description: string;
  installment_amount: number;
  total_installments: number;
  start_year: number;
  start_month: number;
  due_day: number;
  is_active: boolean;
}

export interface InstallmentStatus {
  id: number;
  description: string;
  category_id: number | null;
  installment_amount: number;
  number: number;
  total_installments: number;
  remaining_count: number;
  remaining_amount: number;
  due_date: string;
  end_year: number;
  end_month: number;
}

export interface SavingsGoal {
  id: number;
  name: string;
  target_amount: number;
  current_amount: number;
  emoji: string;
  color: string;
  deadline: string | null;
  is_active: boolean;
}

export interface TrendPoint {
  year: number;
  month: number;
  income: number;
  expense: number;
  balance: number;
}
