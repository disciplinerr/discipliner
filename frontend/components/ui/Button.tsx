import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "ghost";

export default function Button({
  variant = "primary",
  className = "",
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl px-5 py-2.5 text-sm font-bold transition-all active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40";
  const variants: Record<Variant, string> = {
    primary: "bg-foreground text-background hover:bg-neutral-300",
    ghost:
      "border border-line bg-transparent text-secondary hover:border-muted hover:text-foreground",
  };
  return <button {...rest} className={`${base} ${variants[variant]} ${className}`} />;
}
