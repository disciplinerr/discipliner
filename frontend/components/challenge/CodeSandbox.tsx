"use client";

import { useState } from "react";
import { useI18n } from "@/lib/i18n";

const PYODIDE_VERSION = "v0.26.4";
const PYODIDE_URL = `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/`;

interface PyodideInterface {
  runPythonAsync(code: string): Promise<unknown>;
  setStdout(options: { batched: (text: string) => void }): void;
  setStderr(options: { batched: (text: string) => void }): void;
}

declare global {
  interface Window {
    loadPyodide?: (options: { indexURL: string }) => Promise<PyodideInterface>;
  }
}

let pyodidePromise: Promise<PyodideInterface> | null = null;

function loadPyodideOnce(): Promise<PyodideInterface> {
  if (pyodidePromise) return pyodidePromise;
  pyodidePromise = new Promise<PyodideInterface>((resolve, reject) => {
    const script = document.createElement("script");
    script.src = `${PYODIDE_URL}pyodide.js`;
    script.onload = () => {
      window
        .loadPyodide!({ indexURL: PYODIDE_URL })
        .then(resolve)
        .catch(reject);
    };
    script.onerror = () => reject(new Error("Failed to load Pyodide"));
    document.head.appendChild(script);
  });
  pyodidePromise.catch(() => {
    pyodidePromise = null; // allow retry after a network failure
  });
  return pyodidePromise;
}

async function runPython(code: string): Promise<string> {
  const pyodide = await loadPyodideOnce();
  const lines: string[] = [];
  pyodide.setStdout({ batched: (text) => lines.push(text) });
  pyodide.setStderr({ batched: (text) => lines.push(text) });
  try {
    const result = await pyodide.runPythonAsync(code);
    if (result !== undefined && result !== null) lines.push(String(result));
  } catch (err) {
    lines.push(String(err));
  }
  return lines.join("\n");
}

function runJavaScript(code: string): string {
  const lines: string[] = [];
  const fakeConsole = {
    log: (...args: unknown[]) => lines.push(args.map(String).join(" ")),
    error: (...args: unknown[]) => lines.push(args.map(String).join(" ")),
    warn: (...args: unknown[]) => lines.push(args.map(String).join(" ")),
  };
  try {
    const fn = new Function("console", code);
    const result = fn(fakeConsole);
    if (result !== undefined) lines.push(String(result));
  } catch (err) {
    lines.push(String(err));
  }
  return lines.join("\n");
}

type Language = "python" | "javascript";

export default function CodeSandbox({ code }: { code: string }) {
  const { t } = useI18n();
  const [language, setLanguage] = useState<Language>("python");
  const [output, setOutput] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "running">("idle");

  async function run() {
    if (!code.trim() || status !== "idle") return;
    setOutput(null);
    try {
      if (language === "python") {
        if (!pyodidePromise) setStatus("loading");
        else setStatus("running");
        const result = await runPython(code);
        setOutput(result);
      } else {
        setStatus("running");
        setOutput(runJavaScript(code));
      }
    } catch (err) {
      setOutput(String(err));
    } finally {
      setStatus("idle");
    }
  }

  return (
    <div className="rounded-xl border border-line bg-elevated p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">
          {t("sandbox.title")}
        </p>
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-line p-0.5">
            {(["python", "javascript"] as Language[]).map((lang) => (
              <button
                key={lang}
                type="button"
                onClick={() => setLanguage(lang)}
                className={`rounded-md px-2.5 py-1 text-xs font-bold transition-colors ${
                  language === lang
                    ? "bg-foreground text-background"
                    : "text-muted hover:text-secondary"
                }`}
              >
                {lang === "python" ? "Python" : "JS"}
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={run}
            disabled={status !== "idle" || !code.trim()}
            className="rounded-lg bg-foreground px-4 py-1.5 text-xs font-bold text-background transition-all hover:bg-neutral-300 active:scale-95 disabled:opacity-40"
          >
            {status === "loading"
              ? t("sandbox.loading_runtime")
              : status === "running"
                ? t("sandbox.running")
                : `▶ ${t("sandbox.run")}`}
          </button>
        </div>
      </div>

      {output !== null && (
        <div className="mt-3">
          <p className="mb-1 text-[10px] font-bold uppercase tracking-widest text-muted">
            {t("sandbox.output")}
          </p>
          <pre className="max-h-64 overflow-auto whitespace-pre-wrap rounded-lg bg-background p-3 font-mono text-xs leading-relaxed text-secondary">
            {output.trim() === "" ? t("sandbox.empty_output") : output}
          </pre>
        </div>
      )}

      <p className="mt-3 text-[11px] text-muted">
        {t("sandbox.note")} {t("sandbox.loop_warning")}
      </p>
    </div>
  );
}
