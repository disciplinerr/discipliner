"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Logo from "@/components/ui/Logo";
import PasswordInput from "@/components/ui/PasswordInput";
import { ApiError, login } from "@/lib/api";
import { useI18n } from "@/lib/i18n";

export default function LoginPage() {
  const { t } = useI18n();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("auth.login_failed"));
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
          <p className="text-sm text-muted">{t("auth.tagline_login")}</p>
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
          <PasswordInput
            placeholder={t("auth.password")}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <p className="text-sm text-red-400">{error}</p>}
          <Button type="submit" disabled={busy} className="w-full">
            {busy ? t("auth.login_busy") : t("auth.login")}
          </Button>
        </form>

        <div className="mt-4 flex flex-col items-center gap-3">
          <Link
            href="/forgot-password"
            className="text-sm text-muted underline-offset-4 hover:text-foreground hover:underline"
          >
            {t("auth.forgot_password")}
          </Link>
          <p className="text-sm text-muted">
            {t("auth.no_account")}{" "}
            <Link
              href="/register"
              className="font-semibold text-foreground underline-offset-4 hover:underline"
            >
              {t("auth.create_account")}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
