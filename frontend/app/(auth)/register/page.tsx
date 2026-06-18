"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Logo from "@/components/ui/Logo";
import PasswordInput from "@/components/ui/PasswordInput";
import PasswordRules, { passwordValid } from "@/components/ui/PasswordRules";
import { ApiError, register } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { MailCheck } from "lucide-react";

export default function RegisterPage() {
  const { t } = useI18n();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);

  const passwordsMatch = password === passwordConfirm;
  const canSubmit = passwordValid(password) && passwordsMatch;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!passwordValid(password)) return;
    if (!passwordsMatch) {
      setError(t("auth.password_mismatch"));
      return;
    }
    setError("");
    setBusy(true);
    try {
      await register(email, password, passwordConfirm);
      setSent(true);
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError(t("auth.email_taken"));
      } else {
        setError(err instanceof ApiError ? err.message : t("auth.register_failed"));
      }
    } finally {
      setBusy(false);
    }
  }

  if (sent) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <div className="w-full max-w-sm animate-fade-up text-center">
          <div className="mb-8 flex flex-col items-center gap-3">
            <Logo size={56} />
            <h1 className="text-2xl font-extrabold tracking-tight">discipliner</h1>
          </div>
          <div className="space-y-4 rounded-2xl border border-line bg-surface p-6 shadow-soft">
            <MailCheck size={44} className="mx-auto text-emerald-400" />
            <h2 className="text-lg font-bold">{t("auth.verify_sent_title")}</h2>
            <p className="text-sm text-muted">{t("auth.verify_sent_text")}</p>
          </div>
          <p className="mt-5 text-center text-sm text-muted">
            <Link
              href="/login"
              className="font-semibold text-foreground underline-offset-4 hover:underline"
            >
              {t("auth.login")}
            </Link>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-[70vh] items-center justify-center">
      <div className="w-full max-w-sm animate-fade-up">
        <div className="mb-8 flex flex-col items-center gap-3">
          <Logo size={56} />
          <h1 className="text-2xl font-extrabold tracking-tight">discipliner</h1>
          <p className="text-sm text-muted">{t("auth.tagline_register")}</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-4 rounded-2xl border border-line bg-surface p-6 shadow-soft"
        >
          <Input
            type="email"
            placeholder={t("auth.email")}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <div className="space-y-2">
            <PasswordInput
              placeholder={t("auth.password_hint")}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <PasswordRules password={password} />
          </div>
          <div className="space-y-2">
            <PasswordInput
              placeholder={t("auth.password_confirm")}
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              required
            />
            {passwordConfirm.length > 0 && !passwordsMatch && (
              <p className="text-sm text-red-400">{t("auth.password_mismatch")}</p>
            )}
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <Button
            type="submit"
            disabled={busy || !canSubmit}
            className="w-full"
          >
            {busy ? t("auth.register_busy") : t("auth.register")}
          </Button>
        </form>

        <p className="mt-5 text-center text-sm text-muted">
          {t("auth.has_account")}{" "}
          <Link
            href="/login"
            className="font-semibold text-foreground underline-offset-4 hover:underline"
          >
            {t("auth.login")}
          </Link>
        </p>
      </div>
    </div>
  );
}
