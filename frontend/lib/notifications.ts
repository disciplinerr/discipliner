const STORAGE_KEY = "discipliner_reminder";
const FIRED_KEY = "discipliner_reminder_fired";

export interface ReminderConfig {
  enabled: boolean;
  hour: number;
  minute: number;
}

const DEFAULT_CONFIG: ReminderConfig = { enabled: false, hour: 20, minute: 0 };

export function getReminder(): ReminderConfig {
  if (typeof window === "undefined") return DEFAULT_CONFIG;
  try {
    return { ...DEFAULT_CONFIG, ...JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "{}") };
  } catch {
    return DEFAULT_CONFIG;
  }
}

export function saveReminder(config: ReminderConfig): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
}

export async function requestPermission(): Promise<NotificationPermission> {
  if (!("Notification" in window)) return "denied";
  if (Notification.permission === "granted") return "granted";
  return Notification.requestPermission();
}

export function getPermission(): NotificationPermission | "unsupported" {
  if (typeof window === "undefined" || !("Notification" in window)) return "unsupported";
  return Notification.permission;
}

export function checkAndFire(pendingCount: number, locale: string): void {
  const config = getReminder();
  if (!config.enabled) return;
  if (typeof window === "undefined" || !("Notification" in window)) return;
  if (Notification.permission !== "granted") return;

  const now = new Date();
  if (now.getHours() !== config.hour || now.getMinutes() !== config.minute) return;

  const today = now.toDateString();
  if (localStorage.getItem(FIRED_KEY) === today) return;
  localStorage.setItem(FIRED_KEY, today);

  const isPt = locale.startsWith("pt");
  const title = isPt ? "Discipliner — Rotina" : "Discipliner — Routine";
  const body =
    pendingCount > 0
      ? isPt
        ? `${pendingCount} ${pendingCount === 1 ? "item pendente" : "itens pendentes"} hoje.`
        : `${pendingCount} pending ${pendingCount === 1 ? "item" : "items"} today.`
      : isPt
        ? "Todos os itens concluídos hoje. 🔥"
        : "All items done today. 🔥";

  new Notification(title, { body, icon: "/icon.svg" });
}
