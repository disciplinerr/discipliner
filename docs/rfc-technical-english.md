# RFC: Technical English Training Module

**Status:** Draft  
**Author:** FernandoHaeser  
**Date:** 2026-06-11  
**Target model:** `claude-fable-5`

---

## 1. Motivation

Reading technical English fluently is a hard prerequisite for backend development: documentation, RFCs, Stack Overflow answers, error messages, commit conventions, API references — all in English. Poor reading speed creates a compounding tax on every learning session.

This module adds **retrieval-based technical English training** to the daily routine. The format borrows the exercise variety of Duolingo (fill-the-blank, multiple choice, translation, matching) but strips gamification and follows the same evidence-based rules already applied in Discipliner:

- Active recall only — no passive reading.
- Spaced repetition for vocabulary retention.
- Deliberate difficulty — sentences are drawn from real technical writing (commit messages, error logs, RFC excerpts, API descriptions).
- PASS/FAIL only — no partial scores for vocabulary.

---

## 2. Scope

### In scope

- Vocabulary and phrase bank of ~400 technical English items (seeded, idempotent).
- Five exercise types (defined in §4).
- Spaced repetition scheduler per user+item (reuse SM-2-lite from review module).
- Daily cap: 10–15 exercises, ~5 minutes.
- Auto-log routine item `english_training` on session completion.
- Integration with existing `/routine` page.
- Claude generation of contextual sentences on demand (fallback to static examples).
- New page: `/english`.

### Out of scope (this RFC)

- Listening/speaking exercises.
- Grammar correction.
- AI tutoring or hint system (contradicts deliberate-practice rule).
- Pronunciation.
- Level detection beyond difficulty enum.

---

## 3. Core Design Decisions

### 3.1 No gamification

Consistent with [learning-method.md](learning-method.md) — no streaks, no XP, no badges. The feedback is the score. A session shows: items done / items due, pass rate for the day.

### 3.2 Difficulty tiers mirror trail phases

| Trail phase | English difficulty |
|---|---|
| 1–2 (Foundations, Backend) | beginner |
| 3–4 (Systems, DevOps) | intermediate |
| 5–6 (Infrastructure, Advanced) | advanced |

The backend picks exercises at or one level above the user's current trail phase difficulty — same interleaving logic as daily challenges.

### 3.3 Retrieval enforced by exercise type

No exercise shows the answer first. Multiple choice distractors must be plausible (same word class, similar context). Fill-in-the-blank never highlights the missing word's category. This prevents pattern-matching without understanding.

### 3.4 Static bank + Claude augmentation

400 seeded items cover the core. When a user reaches a new trail phase, Claude generates 5–10 contextual sentences using vocabulary from that phase's topics (e.g. Phase 3 → "thread", "deadlock", "race condition") and stores them as `EnglishItem` rows. Generation is one-shot per user+phase — cached, never regenerated.

### 3.5 Spaced repetition per item

Reuses the SM-2-lite algorithm already in `review_service.py`. Each `EnglishProgress` row tracks `ease`, `interval_days`, `repetitions` per user+item. Grade mapping:

| Answer | Grade |
|---|---|
| Correct | 2 (good) |
| Wrong | 0 (forgot) |

No "hard/easy" nuance — vocabulary is binary.

---

## 4. Exercise Types

| Type | Description | Example |
|---|---|---|
| **multiple_choice_vocab** | Word shown in isolation, pick correct definition | "deadlock" → A: mutual wait cycle / B: memory leak / C: race condition / D: stack overflow |
| **fill_in_the_blank** | Technical sentence with one word blanked, type or pick | "A ___ proxy sits between client and backend." → reverse |
| **translate_pt_en** | Portuguese technical phrase, user types English equivalent | "fila de mensagens" → message queue |
| **translate_en_pt** | English term, user types Portuguese | "load balancing" → balanceamento de carga |
| **sentence_match** | Match 4 terms to 4 short definitions (drag or tap) | deadlock ↔ "two threads wait forever", livelock ↔ "threads keep changing state but make no progress", ... |

Exercise type rotation is deterministic per session (same interleaving principle): no two of the same type back-to-back.

---

## 5. Data Model

```sql
-- Static + Claude-generated vocabulary bank
english_items (
  id              SERIAL PRIMARY KEY,
  term            VARCHAR(120) NOT NULL,          -- "reverse proxy"
  definition_en   TEXT NOT NULL,                   -- "sits in front of backend servers..."
  definition_pt   TEXT NOT NULL,                   -- "fica na frente dos servidores..."
  example_sentence TEXT,                           -- "nginx acts as a reverse proxy..."
  category        VARCHAR(60),                     -- "networking", "concurrency", "databases", ...
  difficulty      difficulty_enum NOT NULL,        -- beginner / intermediate / advanced
  source          VARCHAR(30) DEFAULT 'seed',      -- 'seed' | 'claude'
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Per-user SM-2-lite state (one row per user+item)
english_progress (
  id              SERIAL PRIMARY KEY,
  user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE,
  item_id         INTEGER REFERENCES english_items(id) ON DELETE CASCADE,
  ease            FLOAT DEFAULT 2.5,
  interval_days   INTEGER DEFAULT 1,
  repetitions     INTEGER DEFAULT 0,
  due_date        DATE DEFAULT CURRENT_DATE,
  last_reviewed   DATE,
  UNIQUE (user_id, item_id)
);

-- Log of individual answers (for stats)
english_attempts (
  id              SERIAL PRIMARY KEY,
  user_id         INTEGER REFERENCES users(id) ON DELETE CASCADE,
  item_id         INTEGER REFERENCES english_items(id) ON DELETE CASCADE,
  exercise_type   VARCHAR(30) NOT NULL,
  correct         BOOLEAN NOT NULL,
  attempted_at    TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 6. API Endpoints

```
GET  /api/v1/english/session
     → Returns today's due items (up to 15), shaped into exercises.
     → Seeds progress rows for new items if user has none.
     → 204 if nothing due today.

POST /api/v1/english/answer
     Body: { item_id, exercise_type, answer }
     → Validates answer against item.term / definition / translation.
     → Runs SM-2-lite update on english_progress.
     → Returns { correct: bool, correct_answer: str }.
     → On 15th correct answer of session: auto-logs routine item english_training.

GET  /api/v1/english/stats
     → { due_today, done_today, pass_rate_7d, mature_items }

POST /api/v1/english/generate  (internal, triggered by trail phase advance)
     → Calls Claude to generate 5 contextual sentences for current phase vocabulary.
     → Stores as english_items with source='claude'.
     → Idempotent: skips if user+phase already generated.
```

Rate limits: `session` 30/min, `answer` 60/min, `generate` 2/min.

---

## 7. Claude Integration

### Trigger

`POST /api/v1/english/generate` is called automatically when a trail phase completes (hook in `trail_service.py`). User never triggers it manually.

### Prompt (system)

```
You are generating technical English vocabulary exercises for a developer learning platform.
Output ONLY a JSON array. No prose, no markdown, no code fences.

Each object must have exactly these keys:
  term          (string, max 3 words, technical English)
  definition_en (string, 1 sentence)
  definition_pt (string, 1 sentence in Brazilian Portuguese)
  example_sentence (string, 1 sentence using the term in a technical context)
  category      (one of: networking, concurrency, databases, systems, devops, api-design, security)

Generate 8 items for vocabulary relevant to: {phase_topics}.
Difficulty: {difficulty}.
Do not use: {existing_terms}.
```

### Model config

```python
client.messages.create(
    model=settings.CLAUDE_MODEL,   # "claude-fable-5"
    max_tokens=1200,
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": user_prompt}],
    # No temperature/top_p/top_k — Fable 5 rejects them
)
```

---

## 8. Frontend

### New page: `/english`

```
┌────────────────────────────────────────────────┐
│  Technical English          5 / 15 today        │
├────────────────────────────────────────────────┤
│                                                  │
│  Fill in the blank:                              │
│                                                  │
│  "A ___ proxy sits between the client and        │
│   the origin server, hiding the server's         │
│   identity."                                     │
│                                                  │
│  [ reverse        ]   ← plain text input         │
│                                                  │
│  [  Submit  ]                                    │
│                                                  │
│  ─────────────────────────────────────────────  │
│  Progress: ████████░░░░░░░░  5 done, 10 left    │
└────────────────────────────────────────────────┘
```

After submit:
- **Correct** → green border, next item immediately.
- **Wrong** → red border, correct answer shown for 2 seconds, then next item.
- No explanations. No hints. No "try again".

### Session complete screen

```
Session done.
Correct: 12 / 15
Items due tomorrow: 8
```

No celebration. No streak counter.

### Routine page integration

`english_training` appears as a new routine item (auto-logged on session complete). No manual check-off allowed — same rule as `daily_challenge`.

---

## 9. Vocabulary Bank Categories (seed)

400 items across 8 categories and 3 difficulties:

| Category | Beginner (50) | Intermediate (80) | Advanced (70) |
|---|---|---|---|
| networking | HTTP, TCP, DNS, IP, port, socket, header, request, response, protocol | reverse proxy, load balancer, TLS handshake, CDN, WebSocket, CORS, SSL certificate | mTLS, BGP, anycast, QUIC, TCP BBR, zero-RTT |
| databases | table, row, column, query, index, join, transaction, migration | ACID, N+1 problem, connection pool, deadlock, WAL, vacuum | MVCC, LSM tree, consistent hashing, write amplification |
| concurrency | thread, process, lock, mutex, race condition | deadlock, livelock, semaphore, async I/O, event loop, goroutine | memory model, happens-before, CAS, ABA problem |
| devops | container, image, volume, environment variable, pipeline | orchestration, health check, rolling deploy, secret management | blue-green deploy, canary release, chaos engineering |
| api-design | endpoint, route, status code, payload, authentication | idempotent, pagination, rate limiting, versioning, contract | hypermedia, HATEOAS, backward compatibility, schema evolution |
| systems | memory, CPU, process, file descriptor, signal | page fault, context switch, system call, mmap, buffer | huge pages, NUMA, kernel bypass, eBPF |
| security | password, hash, token, HTTPS, firewall | JWT, SQL injection, XSS, CSRF, privilege escalation | side-channel attack, key derivation, supply chain attack |
| git-workflow | commit, branch, merge, pull request, conflict | rebase, cherry-pick, bisect, stash, reflog | octopus merge, rerere, partial clone |

---

## 10. Enforcement Rules

1. Session cap: 15 items max per day. No override.
2. `english_training` routine item: auto-logged only on 15 correct answers in one session. Partial sessions do not log.
3. Answer validation is server-side only. Frontend shows result, never validates locally.
4. No hints. No "close enough" matching. String comparison is case-insensitive, trim-only. No fuzzy.
5. Claude-generated items stored permanently — not regenerated per session. Quality is reviewed at next trail phase.

---

## 11. Open Questions

| # | Question | Impact |
|---|---|---|
| 1 | Should `translate_pt_en` accept synonyms? (e.g. "fila" → "queue" or "message queue") | High — determines if we need a synonyms list per item or strict single answer |
| 2 | Should `sentence_match` be implemented in v1 or deferred? Requires drag interaction on mobile. | Medium — can launch with 4 types, add match in v2 |
| 3 | Routine cap: complete session = 15 correct or 15 attempted? | Low — proposed: 15 correct (harder, consistent with deliberate-practice principle) |
| 4 | Should `english_progress` be pre-seeded for all 400 items at registration, or lazy (due today = subset)? | Medium — lazy seeding on first `GET /session` avoids 400 inserts at signup |

---

## 12. Implementation Plan (suggested order)

1. **Migration** — `english_items`, `english_progress`, `english_attempts` tables + `difficulty_enum` reuse.
2. **Seed script** — 400 items in `backend/app/db/seed_english.py` (idempotent, title-based dedup).
3. **Models + schemas** — `EnglishItem`, `EnglishProgress`, `EnglishAttempt` SQLAlchemy models.
4. **Service layer** — `english_service.py`: session builder, answer validator, SM-2-lite adapter, Claude generation hook.
5. **Endpoints** — `backend/app/api/v1/endpoints/english.py`.
6. **Trail hook** — call `generate_english_for_phase()` inside `trail_service.complete_phase()`.
7. **Frontend** — `/english` page, exercise components, routine item.
8. **Tests** — answer validation, SM-2 schedule update, idempotent session log.
