"use client";

import { useI18n } from "@/lib/i18n";
import { Challenge } from "@/types";



function Section({ label, children, mono = false }: {
  label: string;
  children: React.ReactNode;
  mono?: boolean;
}) {
  return (
    <section>
      <h2 className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-muted">
        {label}
      </h2>
      <div
        className={`whitespace-pre-wrap rounded-xl bg-elevated p-4 text-sm leading-relaxed text-secondary ${
          mono ? "font-mono" : ""
        }`}
      >
        {children}
      </div>
    </section>
  );
}

export default function ChallengeView({ challenge }: { challenge: Challenge }) {
  const { t } = useI18n();
  const difficultyLabel: Record<string, string> = {
    beginner: t("challenge.difficulty_beginner"),
    intermediate: t("challenge.difficulty_intermediate"),
    advanced: t("challenge.difficulty_advanced"),
  };
  return (
    <div className="space-y-5">
      <div>
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <span className="rounded-full border border-line px-2.5 py-0.5 text-xs font-bold text-secondary">
            {challenge.category}
          </span>
          <span className="rounded-full border border-line px-2.5 py-0.5 text-xs font-bold text-secondary">
            {difficultyLabel[challenge.difficulty] ?? challenge.difficulty}
          </span>
          <span className="text-xs font-semibold text-muted">{challenge.date}</span>
        </div>
        <h1 className="text-2xl font-extrabold tracking-tight">{challenge.title}</h1>
      </div>

      <Section label={t("challenge.math_section")}>
        {challenge.math_problem}
      </Section>
      <Section label={t("challenge.task_section")}>{challenge.programming_task}</Section>
      {challenge.expected_output_example && (
        <Section label={t("challenge.output_section")} mono>
          {challenge.expected_output_example}
        </Section>
      )}
      {challenge.constraints && (
        <Section label={t("challenge.constraints_section")}>{challenge.constraints}</Section>
      )}
    </div>
  );
}
