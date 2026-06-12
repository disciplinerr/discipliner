import { InputHTMLAttributes } from "react";

export default function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  const { className = "", ...rest } = props;
  return (
    <input
      {...rest}
      className={`w-full rounded-xl border border-line bg-elevated px-4 py-2.5 text-foreground placeholder:text-muted transition-colors focus:border-secondary ${className}`}
    />
  );
}
