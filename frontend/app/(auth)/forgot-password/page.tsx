"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Logo from "@/components/ui/Logo";
import { ApiError, forgotPassword } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { ArrowLeft } from "lucide-react";

export default function ForgotPasswordPage() {
  const { t } = useI18n();
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await forgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("auth.forgot_failed"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-[70vh] items-center justify-center">
      <div className="w-full max-w-sm animate-fade-up">
        <div className="mb-8 flex flex-col items-center gap-3">
          <Logo size={56} />
          <h1 className="text-2xl font-extrabold tracking-tight">discipliner</h1>
          <p className="text-sm text-muted">{t("auth.forgot_subtitle")}</p>
        </div>

        {sent ? (
          <div className="rounded-2xl border border-line bg-surface p-6 shadow-soft text-center space-y-3">
            <p className="font-extrabold">{t("auth.forgot_sent_title")}</p>
            <p className="text-sm text-secondary">{t("auth.forgot_sent_text")}</p>
            <Link
              href="/login"
              className="mt-2 inline-flex items-center gap-1 text-sm font-semibold text-foreground underline-offset-4 hover:underline"
            >
              <ArrowLeft size={14} /> {t("auth.back_to_login")}
            </Link>
          </div>
        ) : (
          <>
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
              {error && <p className="text-sm text-red-400">{error}</p>}
              <Button type="submit" disabled={busy} className="w-full">
                {busy ? t("auth.forgot_sending") : t("auth.forgot_submit")}
              </Button>
            </form>

            <p className="mt-5 text-center text-sm text-muted">
              <Link
                href="/login"
                className="inline-flex items-center gap-1 font-semibold text-foreground underline-offset-4 hover:underline"
              >
                <ArrowLeft size={14} /> {t("auth.back_to_login")}
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
