# Frontend — i18n, Settings, Code Sandbox

## Internationalization (i18n)

Lightweight, dependency-free i18n built on React context. Two locales: **pt-BR** (default) and **en**.

| Piece | Location |
|---|---|
| Dictionaries | `frontend/locales/pt-BR.ts` (source of truth), `frontend/locales/en.ts` |
| Provider + hook | `frontend/lib/i18n.tsx` — `I18nProvider` (wraps the app in `layout.tsx`), `useI18n()` |
| Persistence | `localStorage` key `discipliner_locale` |

Usage in components:

```tsx
const { t, locale, setLocale } = useI18n();
t("routine.title");                       // translated string, typed key
new Date(d).toLocaleDateString(locale);   // locale-aware dates everywhere
```

Rules:
- `pt-BR.ts` defines the key set (`as const`); `en.ts` is typed as `Record<keyof typeof ptBR, string>` — a missing English key is a **compile error**.
- Backend strings (routine item labels) are translated client-side via `routineLabel(t, item_key, fallback)`, keyed by the stable `item_key`. Unknown keys fall back to the backend label, so adding items never breaks the UI.
- Adding a language = new file in `locales/` + one entry in `DICTS` and the settings page list.

## Settings (`/settings`)

| Section | What it does | Storage |
|---|---|---|
| Language | pt-BR / English toggle, applies immediately | `localStorage` |
| Pomodoro | Focus minutes (10–60) and break minutes (3–20), consumed by the routine-page timer | `localStorage` (`lib/pomodoro.ts`) |
| Account | Email, member-since, current trail phase (from `GET /auth/me`) + logout | — |

Settings are device-local by design — no backend persistence, nothing to sync, nothing to leak.

## Code Sandbox

`frontend/components/challenge/CodeSandbox.tsx`, embedded under the code textarea in the submission form. Lets you **run the code you are about to submit** without leaving the page.

| Language | Runtime | Notes |
|---|---|---|
| Python | [Pyodide](https://pyodide.org) (CPython compiled to WebAssembly) | Lazy-loaded from CDN on first run (~10 MB, then cached by the browser). stdout/stderr captured; last expression value printed. |
| JavaScript | `new Function` with a captured `console` | Instant; `console.log/error/warn` and the return value go to the output panel. |

Design constraints (deliberate):
- **Everything runs in the browser.** No code is sent to any server or AI. The strict rules stay intact: the sandbox is an interpreter, not an assistant.
- The editor remains a plain textarea — no autocomplete, no highlighting, no AI (non-negotiable rule 6).
- Code runs on the main thread: an infinite loop freezes the tab. This is documented in the UI.
- C/Java submissions can't run client-side; use Python or JS to verify logic, submit in whatever language the challenge asks.

## File map

```
frontend/
├── locales/pt-BR.ts        # dictionary (source of truth for keys)
├── locales/en.ts           # English translations (type-checked against pt-BR)
├── lib/i18n.tsx            # I18nProvider, useI18n, routineLabel
├── lib/pomodoro.ts         # pomodoro config (localStorage)
├── app/settings/page.tsx   # settings page
└── components/challenge/CodeSandbox.tsx
```
