import {
  Challenge,
  ChallengeHistoryItem,
  ReviewCard,
  ReviewStats,
  RoutineDay,
  RoutineItem,
  RoutineWeek,
  Submission,
  TokenPair,
  TrailProgress,
  User,
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

export function register(email: string, password: string): Promise<User> {
  return request("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
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

export function getTodayChallenge(): Promise<Challenge> {
  return request("/api/v1/challenges/today");
}

export function submitChallenge(
  id: number,
  mathDerivation: string,
  code: string
): Promise<Submission> {
  return request(`/api/v1/challenges/${id}/submit`, {
    method: "POST",
    body: JSON.stringify({ math_derivation: mathDerivation, code_submission: code }),
  });
}

export function getChallengeHistory(): Promise<ChallengeHistoryItem[]> {
  return request("/api/v1/challenges/history");
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
