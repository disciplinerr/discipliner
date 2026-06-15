"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef, useState } from "react";
import Logo from "@/components/ui/Logo";
import { ApiError, verifyEmail } from "@/lib/api";
import { useI18n } from "@/lib/i18n";

type Status = "verifying" | "ok" | "error";

function VerifyEmailInner() {
  const { t } = useI18n();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const [status, setStatus] = useState<Status>(token ? "verifying" : "error");
  const [error, setError] = useState(token ? "" : t("auth.verify_invalid"));
  const ran = useRef(false);

  useEffect(() => {
    if (!token || ran.current) return;
    ran.current = true; // StrictMode double-invoke guard — token is single-use
    verifyEmail(token)
      .then(() => setStatus("ok"))
      .catch((err) => {
        setStatus("error");
        if (err instanceof ApiError) {
          if (err.status === 410) setError(t("auth.verify_expired"));
          else if (err.status === 404) setError(t("auth.verify_invalid"));
          else setError(err.message);
        } else {
          setError(t("auth.verify_failed"));
        }
      });
  }, [token, t]);

  if (status === "verifying") {
    return (
      <div className="rounded-2xl border border-line bg-surface p-6 shadow-soft text-center space-y-3">
        <p className="text-sm text-muted">{t("auth.verify_checking")}</p>
      </div>
    );
  }

  if (status === "ok") {
    return (
      <div className="rounded-2xl border border-line bg-surface p-6 shadow-soft text-center space-y-3">
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-foreground text-xl text-background mx-auto">
          ✓
        </span>
        <p className="font-extrabold">{t("auth.verify_done_title")}</p>
        <p className="text-sm text-secondary">{t("auth.verify_done_text")}</p>
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
    <div className="rounded-2xl border border-line bg-surface p-6 shadow-soft text-center space-y-3">
      <p className="font-extrabold text-red-400">{error}</p>
      <Link
        href="/register"
        className="inline-block text-sm font-semibold text-foreground underline-offset-4 hover:underline"
      >
        {t("auth.register")}
      </Link>
    </div>
  );
}

export default function VerifyEmailPage() {
  const { t } = useI18n();

  return (
    <div className="flex min-h-[70vh] items-center justify-center">
      <div className="w-full max-w-sm animate-fade-up">
        <div className="mb-8 flex flex-col items-center gap-3">
          <Logo size={56} />
          <h1 className="text-2xl font-extrabold tracking-tight">discipliner</h1>
          <p className="text-sm text-muted">{t("auth.verify_subtitle")}</p>
        </div>

        <Suspense fallback={<p className="text-sm text-muted text-center">carregando...</p>}>
          <VerifyEmailInner />
        </Suspense>

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
