"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useState } from "react";
import Button from "@/components/ui/Button";
import Logo from "@/components/ui/Logo";
import PasswordInput from "@/components/ui/PasswordInput";
import PasswordRules, { passwordValid } from "@/components/ui/PasswordRules";
import { ApiError, resetPassword } from "@/lib/api";
import { useI18n } from "@/lib/i18n";

function ResetPasswordForm() {
  const { t } = useI18n();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const [password, setPassword] = useState("");
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!passwordValid(password)) return;
    setError("");
    setBusy(true);
    try {
      await resetPassword(token, password);
      setDone(true);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 410) setError(t("auth.reset_expired"));
        else if (err.status === 404) setError(t("auth.reset_invalid"));
        else setError(err.message);
      } else {
        setError(t("auth.reset_failed"));
      }
    } finally {
      setBusy(false);
    }
  }

  if (!token) {
    return (
      <div className="rounded-2xl border border-line bg-surface p-6 shadow-soft text-center space-y-3">
        <p className="font-extrabold text-red-400">{t("auth.reset_invalid")}</p>
        <Link
          href="/forgot-password"
          className="inline-block text-sm font-semibold text-foreground underline-offset-4 hover:underline"
        >
          {t("auth.request_new_link")}
        </Link>
      </div>
    );
  }

  if (done) {
    return (
      <div className="rounded-2xl border border-line bg-surface p-6 shadow-soft text-center space-y-3">
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-foreground text-xl text-background mx-auto">
          ✓
        </span>
        <p className="font-extrabold">{t("auth.reset_done_title")}</p>
        <p className="text-sm text-secondary">{t("auth.reset_done_text")}</p>
        <Link
          href="/login"
          className="inline-block mt-2 rounded-xl bg-foreground px-6 py-2.5 text-sm font-bold text-background transition-all hover:bg-neutral-300 active:scale-[0.98]"
        >
          {t("auth.back_to_login")}
        </Link>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-2xl border border-line bg-surface p-6 shadow-soft"
    >
      <div className="space-y-2">
        <PasswordInput
          placeholder={t("auth.new_password")}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <PasswordRules password={password} />
      </div>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <Button
        type="submit"
        disabled={busy || !passwordValid(password)}
        className="w-full"
      >
        {busy ? t("auth.reset_saving") : t("auth.reset_submit")}
      </Button>
    </form>
  );
}

export default function ResetPasswordPage() {
  const { t } = useI18n();

  return (
    <div className="flex min-h-[70vh] items-center justify-center">
      <div className="w-full max-w-sm animate-fade-up">
        <div className="mb-8 flex flex-col items-center gap-3">
          <Logo size={56} />
          <h1 className="text-2xl font-extrabold tracking-tight">discipliner</h1>
          <p className="text-sm text-muted">{t("auth.reset_subtitle")}</p>
        </div>

        <Suspense fallback={<p className="text-sm text-muted text-center">carregando...</p>}>
          <ResetPasswordForm />
        </Suspense>

        <p className="mt-5 text-center text-sm text-muted">
          <Link
            href="/login"
            className="font-semibold text-foreground underline-offset-4 hover:underline"
          >
            ← {t("auth.back_to_login")}
          </Link>
        </p>
      </div>
    </div>
  );
}
