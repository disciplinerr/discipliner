import { Check, Circle } from "lucide-react";

type Rule = { label: string; met: boolean };

function check(password: string): Rule[] {
  return [
    { label: "8+ caracteres", met: password.length >= 8 },
    { label: "Maiúscula", met: /[A-Z]/.test(password) },
    { label: "Minúscula", met: /[a-z]/.test(password) },
    { label: "Número", met: /[0-9]/.test(password) },
  ];
}

export function passwordValid(password: string): boolean {
  return check(password).every((r) => r.met);
}

export default function PasswordRules({ password }: { password: string }) {
  if (!password) return null;
  const rules = check(password);
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1 pt-1">
      {rules.map((r) => (
        <span
          key={r.label}
          className={`flex items-center gap-1 text-xs font-medium transition-colors ${
            r.met ? "text-green-500" : "text-muted"
          }`}
        >
          {r.met ? <Check size={12} /> : <Circle size={8} />}
          {r.label}
        </span>
      ))}
    </div>
  );
}
