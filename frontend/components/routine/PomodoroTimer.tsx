"use client";

import { useEffect, useRef, useState } from "react";
import { useI18n } from "@/lib/i18n";
import { getPomodoroConfig } from "@/lib/pomodoro";

type Mode = "focus" | "break";

function storageKey() {
  return `discipliner_pomodoros_${new Date().toISOString().slice(0, 10)}`;
}

export default function PomodoroTimer() {
  const { t } = useI18n();
  const [focusSeconds, setFocusSeconds] = useState(25 * 60);
  const [breakSeconds, setBreakSeconds] = useState(5 * 60);
  const [focusMinutes, setFocusMinutes] = useState(25);
  const [mode, setMode] = useState<Mode>("focus");
  const [secondsLeft, setSecondsLeft] = useState(25 * 60);
  const [running, setRunning] = useState(false);
  const [cycles, setCycles] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const config = getPomodoroConfig();
    setFocusMinutes(config.focusMinutes);
    setFocusSeconds(config.focusMinutes * 60);
    setBreakSeconds(config.breakMinutes * 60);
    setSecondsLeft(config.focusMinutes * 60);
    setCycles(Number(localStorage.getItem(storageKey()) ?? 0));
  }, []);

  useEffect(() => {
    if (!running) return;
    intervalRef.current = setInterval(() => {
      setSecondsLeft((s) => s - 1);
    }, 1000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [running]);

  useEffect(() => {
    if (secondsLeft > 0) return;
    setRunning(false);
    if (mode === "focus") {
      const next = cycles + 1;
      setCycles(next);
      localStorage.setItem(storageKey(), String(next));
      setMode("break");
      setSecondsLeft(breakSeconds);
    } else {
      setMode("focus");
      setSecondsLeft(focusSeconds);
    }
  }, [secondsLeft, mode, cycles, breakSeconds, focusSeconds]);

  const total = mode === "focus" ? focusSeconds : breakSeconds;
  const progress = 1 - secondsLeft / total;
  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;
  const focusedMinutes = cycles * focusMinutes;

  const R = 54;
  const CIRC = 2 * Math.PI * R;

  function reset() {
    setRunning(false);
    setMode("focus");
    setSecondsLeft(focusSeconds);
  }

  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row sm:gap-8">
      <div className="relative h-36 w-36 shrink-0">
        <svg viewBox="0 0 128 128" className="h-full w-full -rotate-90">
          <circle cx="64" cy="64" r={R} fill="none" stroke="#1d1d1d" strokeWidth="8" />
          <circle
            cx="64"
            cy="64"
            r={R}
            fill="none"
            stroke="#fafafa"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={CIRC}
            strokeDashoffset={CIRC * (1 - progress)}
            className="transition-[stroke-dashoffset] duration-1000 ease-linear"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-extrabold tabular-nums">
            {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}
          </span>
          <span className="text-[10px] font-bold uppercase tracking-widest text-muted">
            {mode === "focus" ? t("pomodoro.focus") : t("pomodoro.break")}
          </span>
        </div>
      </div>

      <div className="flex flex-col items-center gap-3 sm:items-start">
        <div className="flex gap-2">
          <button
            onClick={() => setRunning(!running)}
            className="rounded-xl bg-foreground px-5 py-2 text-sm font-bold text-background transition-all hover:bg-neutral-300 active:scale-[0.98]"
          >
            {running ? t("pomodoro.pause") : t("pomodoro.start")}
          </button>
          <button
            onClick={reset}
            className="rounded-xl border border-line px-5 py-2 text-sm font-bold text-muted transition-colors hover:border-muted hover:text-secondary"
          >
            {t("pomodoro.reset")}
          </button>
        </div>

        <div className="flex items-center gap-1.5">
          {Array.from({ length: Math.max(4, cycles) }).map((_, i) => (
            <span
              key={i}
              className={`h-2.5 w-2.5 rounded-full ${
                i < cycles ? "bg-foreground" : "bg-elevated"
              }`}
            />
          ))}
          <span className="ml-2 text-xs font-semibold text-muted">
            {cycles} {cycles === 1 ? t("pomodoro.one") : t("pomodoro.many")} ·{" "}
            {focusedMinutes} {t("pomodoro.focus_minutes")}
          </span>
        </div>

        <p className="max-w-xs text-center text-xs text-secondary sm:text-left">
          {focusedMinutes >= 60 ? t("pomodoro.hint_done") : t("pomodoro.hint_progress")}
        </p>
      </div>
    </div>
  );
}
