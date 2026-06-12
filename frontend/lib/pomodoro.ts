export const DEFAULT_FOCUS_MINUTES = 25;
export const DEFAULT_BREAK_MINUTES = 5;

const FOCUS_KEY = "discipliner_pomodoro_focus_min";
const BREAK_KEY = "discipliner_pomodoro_break_min";

export interface PomodoroConfig {
  focusMinutes: number;
  breakMinutes: number;
}

export function getPomodoroConfig(): PomodoroConfig {
  if (typeof window === "undefined") {
    return { focusMinutes: DEFAULT_FOCUS_MINUTES, breakMinutes: DEFAULT_BREAK_MINUTES };
  }
  return {
    focusMinutes: Number(localStorage.getItem(FOCUS_KEY)) || DEFAULT_FOCUS_MINUTES,
    breakMinutes: Number(localStorage.getItem(BREAK_KEY)) || DEFAULT_BREAK_MINUTES,
  };
}

export function setPomodoroConfig(config: PomodoroConfig): void {
  localStorage.setItem(FOCUS_KEY, String(config.focusMinutes));
  localStorage.setItem(BREAK_KEY, String(config.breakMinutes));
}
