import {
  Bill,
  BillStatus,
  Category,
  Challenge,
  ChallengeHistoryItem,
  DashboardStats,
  EnglishAnswerResult,
  EnglishSession,
  EnglishStats,
  ExecuteResult,
  FinanceOverview,
  Installment,
  InstallmentStatus,
  PreviewChallenge,
  ReviewCard,
  ReviewStats,
  RoutineDay,
  RoutineItem,
  RoutineMonth,
  RoutineWeek,
  SavingsGoal,
  Submission,
  TokenPair,
  Transaction,
  TrailProgress,
  TrendPoint,
  User,
  UserRoutineItem,
} from "@/types";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function refreshTokens(): Promise<boolean> {
  const refresh = getRefreshToken();
  if (!refresh) return false;
  const res = await fetch(`${API_URL}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refresh }),
  });
  if (!res.ok) {
    clearTokens();
    return false;
  }
  const tokens: TokenPair = await res.json();
  setTokens(tokens.access_token, tokens.refresh_token);
  return true;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  retry = true
): Promise<T> {
  const token = getAccessToken();
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (res.status === 401 && retry && (await refreshTokens())) {
    return request<T>(path, options, false);
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // non-JSON error body
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// --- Auth ---

export function register(
  email: string,
  password: string,
  passwordConfirm: string,
): Promise<{ message: string }> {
  return request("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({
      email,
      password,
      password_confirm: passwordConfirm,
    }),
  });
}

export function verifyEmail(token: string): Promise<{ message: string }> {
  return request("/api/v1/auth/verify-email", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

export async function login(email: string, password: string): Promise<void> {
  const tokens = await request<TokenPair>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setTokens(tokens.access_token, tokens.refresh_token);
}

export function getMe(): Promise<User> {
  return request("/api/v1/auth/me");
}

// --- Challenges ---

export function getTodayChallenge(locale = "pt-BR"): Promise<Challenge> {
  return request(`/api/v1/challenges/today?locale=${encodeURIComponent(locale)}`);
}

export function submitChallenge(id: number, code: string): Promise<Submission> {
  return request(`/api/v1/challenges/${id}/submit`, {
    method: "POST",
    body: JSON.stringify({ code_submission: code }),
  });
}

export function getChallengeHistory(): Promise<ChallengeHistoryItem[]> {
  return request("/api/v1/challenges/history");
}

export function executeCode(code: string, language: string): Promise<ExecuteResult> {
  return request("/api/v1/challenges/execute", {
    method: "POST",
    body: JSON.stringify({ code, language }),
  });
}

export function generateCustomChallenge(
  description: string,
  locale: string
): Promise<PreviewChallenge> {
  return request("/api/v1/challenges/generate-custom", {
    method: "POST",
    body: JSON.stringify({ description, locale }),
  });
}

// --- Routine ---

export function getTodayRoutine(): Promise<RoutineDay> {
  return request("/api/v1/routine/today");
}

export function checkRoutineItem(
  itemKey: string,
  status: "DONE" | "SKIPPED"
): Promise<RoutineItem> {
  return request(`/api/v1/routine/today/${itemKey}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function getWeekRoutine(): Promise<RoutineWeek> {
  return request("/api/v1/routine/week");
}

export function getMonthRoutine(year: number, month: number): Promise<RoutineMonth> {
  return request(`/api/v1/routine/month?year=${year}&month=${month}`);
}

export function getRoutineItems(): Promise<UserRoutineItem[]> {
  return request("/api/v1/routine/items");
}

export function addRoutineItem(label: string): Promise<UserRoutineItem> {
  return request("/api/v1/routine/items", {
    method: "POST",
    body: JSON.stringify({ label }),
  });
}

export function toggleRoutineItem(itemKey: string, isActive: boolean): Promise<UserRoutineItem> {
  return request(`/api/v1/routine/items/${itemKey}`, {
    method: "PATCH",
    body: JSON.stringify({ is_active: isActive }),
  });
}

export function deleteRoutineItem(itemKey: string): Promise<void> {
  return request(`/api/v1/routine/items/${itemKey}`, { method: "DELETE" });
}

// --- Reviews (spaced repetition) ---

export function getDueReviews(): Promise<ReviewCard[]> {
  return request("/api/v1/reviews/due");
}

export function getReviewStats(): Promise<ReviewStats> {
  return request("/api/v1/reviews/stats");
}

export function gradeReview(cardId: number, grade: 0 | 1 | 2 | 3): Promise<ReviewCard> {
  return request(`/api/v1/reviews/${cardId}/grade`, {
    method: "POST",
    body: JSON.stringify({ grade }),
  });
}

// --- Trail ---

export function getTrailProgress(): Promise<TrailProgress> {
  return request("/api/v1/trail/progress");
}

export function completePhase(phaseId: number, summary: string): Promise<void> {
  return request(`/api/v1/trail/phase/${phaseId}/complete`, {
    method: "POST",
    body: JSON.stringify({ summary }),
  });
}

// --- Password reset ---

export function forgotPassword(email: string): Promise<{ message: string }> {
  return request("/api/v1/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export function resetPassword(
  token: string,
  new_password: string,
): Promise<{ message: string }> {
  return request("/api/v1/auth/reset-password", {
    method: "POST",
    body: JSON.stringify({ token, new_password }),
  });
}

// --- English training ---

export function getEnglishSession(): Promise<EnglishSession | null> {
  return request<EnglishSession | null>("/api/v1/english/session").catch((err) => {
    if (err instanceof ApiError && err.status === 204) return null;
    throw err;
  });
}

export function submitEnglishAnswer(
  item_id: number,
  exercise_type: string,
  answer: string,
): Promise<EnglishAnswerResult> {
  return request("/api/v1/english/answer", {
    method: "POST",
    body: JSON.stringify({ item_id, exercise_type, answer }),
  });
}

export function getEnglishStats(): Promise<EnglishStats> {
  return request("/api/v1/english/stats");
}

export function getDashboardStats(): Promise<DashboardStats> {
  return request("/api/v1/dashboard/stats");
}

// --- Finance ---

export function getFinanceOverview(year: number, month: number): Promise<FinanceOverview> {
  return request(`/api/v1/finance/overview?year=${year}&month=${month}`);
}

export function getCategories(): Promise<Category[]> {
  return request("/api/v1/finance/categories");
}

export function createCategory(data: {
  name: string;
  emoji?: string;
  color?: string;
  group?: string;
  monthly_budget?: number;
}): Promise<Category> {
  return request("/api/v1/finance/categories", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateCategory(
  id: number,
  data: Partial<{
    name: string;
    emoji: string;
    color: string;
    group: string;
    monthly_budget: number;
    is_active: boolean;
  }>,
): Promise<Category> {
  return request(`/api/v1/finance/categories/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteCategory(id: number): Promise<void> {
  return request(`/api/v1/finance/categories/${id}`, { method: "DELETE" });
}

export function getTransactions(year: number, month: number): Promise<Transaction[]> {
  return request(`/api/v1/finance/transactions?year=${year}&month=${month}`);
}

export function createTransaction(data: {
  category_id?: number | null;
  description: string;
  amount: number;
  kind: string;
  date: string;
}): Promise<Transaction> {
  return request("/api/v1/finance/transactions", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function deleteTransaction(id: number): Promise<void> {
  return request(`/api/v1/finance/transactions/${id}`, { method: "DELETE" });
}

export function getBills(): Promise<Bill[]> {
  return request("/api/v1/finance/bills");
}

export function getBillsForMonth(year: number, month: number): Promise<BillStatus[]> {
  return request(`/api/v1/finance/bills/month?year=${year}&month=${month}`);
}

export function createBill(data: {
  category_id?: number | null;
  name: string;
  amount: number;
  due_day: number;
}): Promise<Bill> {
  return request("/api/v1/finance/bills", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateBill(
  id: number,
  data: Partial<{
    category_id: number | null;
    name: string;
    amount: number;
    due_day: number;
    is_active: boolean;
  }>,
): Promise<Bill> {
  return request(`/api/v1/finance/bills/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteBill(id: number): Promise<void> {
  return request(`/api/v1/finance/bills/${id}`, { method: "DELETE" });
}

export function payBill(id: number, year: number, month: number): Promise<BillStatus> {
  return request(`/api/v1/finance/bills/${id}/pay?year=${year}&month=${month}`, {
    method: "POST",
  });
}

export function unpayBill(id: number, year: number, month: number): Promise<BillStatus> {
  return request(`/api/v1/finance/bills/${id}/pay?year=${year}&month=${month}`, {
    method: "DELETE",
  });
}

// Installments (parcelas)

export function getInstallments(): Promise<Installment[]> {
  return request("/api/v1/finance/installments");
}

export function getInstallmentsForMonth(
  year: number,
  month: number,
): Promise<InstallmentStatus[]> {
  return request(`/api/v1/finance/installments/month?year=${year}&month=${month}`);
}

export function createInstallment(data: {
  description: string;
  installment_amount: number;
  total_installments: number;
  start_year: number;
  start_month: number;
  due_day: number;
  category_id: number | null;
}): Promise<Installment> {
  return request("/api/v1/finance/installments", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function deleteInstallment(id: number): Promise<void> {
  return request(`/api/v1/finance/installments/${id}`, { method: "DELETE" });
}

// Savings goals (metas)

export function getGoals(): Promise<SavingsGoal[]> {
  return request("/api/v1/finance/goals");
}

export function createGoal(data: {
  name: string;
  target_amount: number;
  current_amount: number;
  emoji: string;
  color: string;
  deadline: string | null;
}): Promise<SavingsGoal> {
  return request("/api/v1/finance/goals", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function contributeGoal(id: number, amount: number): Promise<SavingsGoal> {
  return request(`/api/v1/finance/goals/${id}/contribute`, {
    method: "POST",
    body: JSON.stringify({ amount }),
  });
}

export function deleteGoal(id: number): Promise<void> {
  return request(`/api/v1/finance/goals/${id}`, { method: "DELETE" });
}

// Trend (month-by-month)

export function getTrend(
  year: number,
  month: number,
  months = 6,
): Promise<TrendPoint[]> {
  return request(
    `/api/v1/finance/trend?year=${year}&month=${month}&months=${months}`,
  );
}
