"use client";

import { KeyboardEvent, useEffect, useRef, useState } from "react";
import { executeCode } from "@/lib/api";
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
    script.onload = () => window.loadPyodide!({ indexURL: PYODIDE_URL }).then(resolve).catch(reject);
    script.onerror = () => reject(new Error("Failed to load Pyodide"));
    document.head.appendChild(script);
  });
  pyodidePromise.catch(() => { pyodidePromise = null; });
  return pyodidePromise;
}

async function runPython(code: string): Promise<string> {
  const pyodide = await loadPyodideOnce();
  const lines: string[] = [];
  pyodide.setStdout({ batched: (t) => lines.push(t) });
  pyodide.setStderr({ batched: (t) => lines.push(t) });
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
    log: (...a: unknown[]) => lines.push(a.map(String).join(" ")),
    error: (...a: unknown[]) => lines.push(a.map(String).join(" ")),
    warn: (...a: unknown[]) => lines.push(a.map(String).join(" ")),
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

// ── Syntax highlighter ────────────────────────────────────────────────────────

const C = {
  keyword:  "#60a5fa",
  string:   "#4ade80",
  comment:  "#6b7280",
  number:   "#fbbf24",
  preproc:  "#a78bfa",
  builtin:  "#f472b6",
} as const;

const PYTHON_BUILTINS = new Set([
  "print","len","range","input","int","str","float","list","dict","set","tuple",
  "bool","type","isinstance","hasattr","getattr","setattr","delattr","callable",
  "enumerate","zip","map","filter","sorted","reversed","sum","min","max","abs",
  "round","open","super","object","repr","format","hex","bin","oct","ord","chr",
  "all","any","next","iter","id","hash","vars","dir","help",
  "Exception","ValueError","TypeError","KeyError","IndexError","AttributeError",
  "RuntimeError","StopIteration","NotImplementedError","FileNotFoundError",
]);

const KEYWORDS: Record<Language, Set<string>> = {
  python: new Set([
    "False","None","True","and","as","assert","async","await","break","class",
    "continue","def","del","elif","else","except","finally","for","from","global",
    "if","import","in","is","lambda","nonlocal","not","or","pass","raise","return",
    "try","while","with","yield",
  ]),
  javascript: new Set([
    "break","case","catch","class","const","continue","debugger","default","delete",
    "do","else","export","extends","false","finally","for","function","if","import",
    "in","instanceof","let","new","null","of","return","static","super","switch",
    "this","throw","true","try","typeof","undefined","var","void","while","with",
    "yield","async","await",
  ]),
  java: new Set([
    "abstract","assert","boolean","break","byte","case","catch","char","class",
    "const","continue","default","do","double","else","enum","extends","final",
    "finally","float","for","goto","if","implements","import","instanceof","int",
    "interface","long","native","new","package","private","protected","public",
    "return","short","static","strictfp","super","switch","synchronized","this",
    "throw","throws","transient","true","false","null","try","var","void",
    "volatile","while",
  ]),
  c: new Set([
    "auto","break","case","char","const","continue","default","do","double","else",
    "enum","extern","float","for","goto","if","inline","int","long","register",
    "restrict","return","short","signed","sizeof","static","struct","switch",
    "typedef","union","unsigned","void","volatile","while",
  ]),
};

function esc(s: string) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function sp(color: string, text: string) {
  return `<span style="color:${color}">${text}</span>`;
}

function highlight(code: string, lang: Language): string {
  const kw = KEYWORDS[lang];
  let out = "";
  let i = 0;

  while (i < code.length) {
    const ch = code[i];

    // Python triple-quote strings (with optional prefix: f""", r""", b""", etc.)
    if (lang === "python") {
      const prefix = /^[fFbBrRuU]{0,2}/.exec(code.slice(i))?.[0] ?? "";
      const after = i + prefix.length;
      if (code.startsWith('"""', after) || code.startsWith("'''", after)) {
        const q = code.slice(after, after + 3);
        const end = code.indexOf(q, after + 3);
        const to = end === -1 ? code.length : end + 3;
        out += sp(C.string, esc(code.slice(i, to)));
        i = to;
        continue;
      }
    }

    // C preprocessor directives
    if (lang === "c" && ch === "#") {
      const end = code.indexOf("\n", i);
      const to = end === -1 ? code.length : end;
      out += sp(C.preproc, esc(code.slice(i, to)));
      i = to;
      continue;
    }

    // Python comment
    if (lang === "python" && ch === "#") {
      const end = code.indexOf("\n", i);
      const to = end === -1 ? code.length : end;
      out += sp(C.comment, esc(code.slice(i, to)));
      i = to;
      continue;
    }

    // Multi-line comment /* */
    if ((lang === "java" || lang === "c" || lang === "javascript") && ch === "/" && code[i + 1] === "*") {
      const end = code.indexOf("*/", i + 2);
      const to = end === -1 ? code.length : end + 2;
      out += sp(C.comment, esc(code.slice(i, to)));
      i = to;
      continue;
    }

    // Single-line comment //
    if ((lang === "java" || lang === "c" || lang === "javascript") && ch === "/" && code[i + 1] === "/") {
      const end = code.indexOf("\n", i);
      const to = end === -1 ? code.length : end;
      out += sp(C.comment, esc(code.slice(i, to)));
      i = to;
      continue;
    }

    // Strings with optional prefix (f"", b"", r"", f'', etc.) — single-line
    {
      const prefix = lang === "python" ? (/^[fFbBrRuU]{0,2}/.exec(code.slice(i))?.[0] ?? "") : "";
      const after = i + prefix.length;
      const q = code[after];
      if (q === '"' || q === "'") {
        let j = after + 1;
        while (j < code.length && code[j] !== q && code[j] !== "\n") {
          if (code[j] === "\\") j++;
          j++;
        }
        if (code[j] === q) j++;
        out += sp(C.string, esc(code.slice(i, j)));
        i = j;
        continue;
      }
    }

    // Numbers
    if (/\d/.test(ch) && (i === 0 || !/\w/.test(code[i - 1]))) {
      let j = i;
      while (j < code.length && /[\d._xXoObBfFdDlLuU]/.test(code[j])) j++;
      out += sp(C.number, esc(code.slice(i, j)));
      i = j;
      continue;
    }

    // Identifiers, keywords and Python builtins
    if (/[a-zA-Z_]/.test(ch)) {
      let j = i;
      while (j < code.length && /\w/.test(code[j])) j++;
      const word = code.slice(i, j);
      if (kw.has(word)) {
        out += sp(C.keyword, word);
      } else if (lang === "python" && PYTHON_BUILTINS.has(word)) {
        out += sp(C.builtin, word);
      } else {
        out += esc(word);
      }
      i = j;
      continue;
    }

    out += esc(ch);
    i++;
  }

  return out;
}

// ── Component ─────────────────────────────────────────────────────────────────

export type Language = "python" | "javascript" | "java" | "c";

const LANG_LABELS: Record<Language, string> = {
  python: "Python",
  javascript: "JS",
  java: "Java",
  c: "C",
};

const LANG_PLACEHOLDERS: Record<Language, string> = {
  python: "# Python",
  javascript: "// JavaScript",
  java: "public class Main {\n  public static void main(String[] args) {\n    \n  }\n}",
  c: "#include <stdio.h>\n\nint main() {\n    \n    return 0;\n}",
};

const PLACEHOLDER_SET = new Set(Object.values(LANG_PLACEHOLDERS));

interface CodeSandboxProps {
  code: string;
  onChange: (code: string) => void;
  language: Language;
  onLanguageChange: (lang: Language) => void;
}

export default function CodeSandbox({ code, onChange, language, onLanguageChange }: CodeSandboxProps) {
  const { t } = useI18n();
  const [output, setOutput] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "running">("idle");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const preRef = useRef<HTMLPreElement>(null);

  // Sync scroll between textarea and highlighted pre
  function syncScroll() {
    if (preRef.current && textareaRef.current) {
      preRef.current.scrollTop = textareaRef.current.scrollTop;
      preRef.current.scrollLeft = textareaRef.current.scrollLeft;
    }
  }

  // Tab → 2 spaces; Enter → auto-indent
  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    const ta = e.currentTarget;

    if (e.key === "Tab") {
      e.preventDefault();
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const next = code.slice(0, start) + "  " + code.slice(end);
      onChange(next);
      requestAnimationFrame(() => {
        ta.selectionStart = ta.selectionEnd = start + 2;
      });
    }

    if (e.key === "Enter") {
      e.preventDefault();
      const start = ta.selectionStart;
      const lineStart = code.lastIndexOf("\n", start - 1) + 1;
      const currentLine = code.slice(lineStart, start);
      const indent = currentLine.match(/^(\s*)/)?.[1] ?? "";
      const extra = /[:{]\s*$/.test(currentLine) ? "  " : "";
      const next = code.slice(0, start) + "\n" + indent + extra + code.slice(ta.selectionEnd);
      onChange(next);
      requestAnimationFrame(() => {
        const pos = start + 1 + indent.length + extra.length;
        ta.selectionStart = ta.selectionEnd = pos;
      });
    }
  }

  async function run() {
    if (!code.trim() || status !== "idle") return;
    setOutput(null);
    try {
      if (language === "python") {
        if (!pyodidePromise) setStatus("loading");
        else setStatus("running");
        setOutput(await runPython(code));
      } else if (language === "javascript") {
        setStatus("running");
        setOutput(runJavaScript(code));
      } else {
        setStatus("running");
        const res = await executeCode(code, language);
        setOutput(res.output || "(sem saída)");
      }
    } catch (err) {
      setOutput(String(err));
    } finally {
      setStatus("idle");
    }
  }

  const highlighted = highlight(code || " ", language);

  const editorStyle = {
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    fontSize: "0.8125rem",
    lineHeight: "1.6",
    padding: "1rem",
    tabSize: 2,
    whiteSpace: "pre" as const,
    overflowWrap: "normal" as const,
  };

  return (
    <div className="rounded-xl border border-line bg-elevated overflow-hidden">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-2.5">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-muted">
          {t("sandbox.title")}
        </p>
        <div className="flex items-center gap-2">
          {/* Language switcher */}
          <div className="flex rounded-lg border border-line p-0.5">
            {(["python", "javascript", "java", "c"] as Language[]).map((lang) => (
              <button
                key={lang}
                type="button"
                onClick={() => {
                  onLanguageChange(lang);
                  // Replace if empty or still showing any language's default template
                  if (!code.trim() || PLACEHOLDER_SET.has(code)) {
                    onChange(LANG_PLACEHOLDERS[lang]);
                  }
                  setOutput(null);
                }}
                className={`rounded-md px-2.5 py-1 text-xs font-bold transition-colors ${
                  language === lang
                    ? "bg-foreground text-background"
                    : "text-muted hover:text-secondary"
                }`}
              >
                {LANG_LABELS[lang]}
              </button>
            ))}
          </div>
          {/* Run */}
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

      {/* Editor (overlay: pre + textarea) */}
      <div className="relative" style={{ minHeight: "260px", height: "320px" }}>
        {/* Highlighted layer */}
        <pre
          ref={preRef}
          aria-hidden
          style={{
            ...editorStyle,
            position: "absolute",
            inset: 0,
            margin: 0,
            overflow: "hidden",
            pointerEvents: "none",
            color: "#e5e5e5",
            background: "transparent",
            wordBreak: "normal",
          }}
          dangerouslySetInnerHTML={{ __html: highlighted + "\n" }}
        />
        {/* Input layer */}
        <textarea
          ref={textareaRef}
          value={code}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onScroll={syncScroll}
          spellCheck={false}
          autoCapitalize="none"
          autoCorrect="off"
          style={{
            ...editorStyle,
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            background: "transparent",
            color: "transparent",
            caretColor: "#fafafa",
            resize: "none",
            outline: "none",
            border: "none",
            overflowY: "auto",
            overflowX: "auto",
          }}
        />
      </div>

      {/* Output */}
      {output !== null && (
        <div className="border-t border-line p-4">
          <p className="mb-1.5 text-[10px] font-bold uppercase tracking-widest text-muted">
            {t("sandbox.output")}
          </p>
          <pre
            className="max-h-48 overflow-auto whitespace-pre-wrap rounded-lg bg-background p-3 text-xs leading-relaxed text-secondary"
            style={{ fontFamily: editorStyle.fontFamily }}
          >
            {output.trim() === "" ? t("sandbox.empty_output") : output}
          </pre>
        </div>
      )}

      <p className="px-4 pb-3 pt-1 text-[11px] text-muted">
        {t("sandbox.note")}
      </p>
    </div>
  );
}
