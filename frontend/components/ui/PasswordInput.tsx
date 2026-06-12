"use client";

import { InputHTMLAttributes, useState } from "react";

type Props = Omit<InputHTMLAttributes<HTMLInputElement>, "type">;

export default function PasswordInput({ className = "", ...rest }: Props) {
  const [show, setShow] = useState(false);

  return (
    <div className="relative">
      <input
        {...rest}
        type={show ? "text" : "password"}
        className={`w-full rounded-xl border border-line bg-elevated px-4 py-2.5 pr-11 text-foreground placeholder:text-muted transition-colors focus:border-secondary ${className}`}
      />
      <button
        type="button"
        onClick={() => setShow((v) => !v)}
        tabIndex={-1}
        aria-label={show ? "Hide password" : "Show password"}
        className="absolute inset-y-0 right-0 flex items-center px-3.5 text-muted transition-colors hover:text-foreground"
      >
        {show ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
            <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
            <line x1="1" y1="1" x2="23" y2="23" />
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
            <circle cx="12" cy="12" r="3" />
          </svg>
        )}
      </button>
    </div>
  );
}
