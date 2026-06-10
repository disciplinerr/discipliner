"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Logo from "@/components/ui/Logo";
import { clearTokens, isLoggedIn } from "@/lib/auth";
import { TKey, useI18n } from "@/lib/i18n";

const LINKS: { href: string; label: TKey }[] = [
  { href: "/dashboard", label: "nav.dashboard" },
  { href: "/routine", label: "nav.routine" },
  { href: "/challenges", label: "nav.challenge" },
  { href: "/review", label: "nav.review" },
  { href: "/trail", label: "nav.trail" },
];

export default function Nav() {
  const pathname = usePathname();
  const router = useRouter();
  const { t } = useI18n();
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    setLoggedIn(isLoggedIn());
  }, [pathname]);

  if (!loggedIn) return null;

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3 sm:px-6">
        <Link
          href="/dashboard"
          className="flex items-center gap-2 font-extrabold tracking-tight"
        >
          <Logo size={28} />
          <span className="hidden sm:inline">discipliner</span>
        </Link>

        <nav className="flex items-center gap-1 rounded-full border border-line bg-surface p-1">
          {LINKS.map((link) => {
            const active = pathname.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`rounded-full px-2.5 py-1.5 text-sm font-semibold transition-colors sm:px-4 ${
                  active
                    ? "bg-foreground text-background"
                    : "text-secondary hover:bg-elevated hover:text-foreground"
                }`}
              >
                {t(link.label)}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-3">
          <Link
            href="/settings"
            aria-label={t("nav.settings")}
            className={`transition-colors ${
              pathname.startsWith("/settings")
                ? "text-foreground"
                : "text-muted hover:text-foreground"
            }`}
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
          </Link>
          <button
            onClick={() => {
              clearTokens();
              router.push("/login");
            }}
            className="text-sm font-semibold text-muted transition-colors hover:text-foreground"
          >
            {t("nav.logout")}
          </button>
        </div>
      </div>
    </header>
  );
}
