# Learning Method

Discipliner's learning dynamic is built on techniques with the strongest experimental evidence in cognitive science. This document explains what the app implements, why, and where each technique lives in the code.

## The evidence

Dunlosky et al. (2013), the most comprehensive review of learning techniques to date, evaluated ten popular study techniques and rated only **two** as "high utility":

1. **Practice testing (retrieval practice / active recall)** — recalling information from memory instead of re-reading it. Roediger & Karpicke (2006) showed students who practiced retrieval retained ~80% of material after a week vs ~34% for those who re-read.
2. **Distributed practice (spaced repetition)** — spreading study over expanding intervals instead of cramming. A meta-analysis across 242 studies and ~169k participants confirmed both as the most effective techniques.

Complementary techniques applied here:

- **Feynman technique** — explaining a concept in simple words as if teaching a beginner; gaps in the explanation reveal gaps in understanding.
- **Pomodoro technique** — 25-minute focused blocks with 5-minute breaks; trains sustained attention and makes the 1-hour study requirement concrete.
- **Interleaving** — mixing problem categories (math / physics / algorithms) instead of blocking one topic.
- **Deliberate practice** — daily challenges slightly above current level, typed by hand, with immediate pass/fail feedback and no solutions given.

References:
- [Evidence-Based Study Techniques — ASRJ](https://theasrj.com/articles/studytechniques)
- [Retrieval and Spaced Practice — Evidence Based Education](https://evidencebased.education/resource/retrieval-and-spaced-practice-study-strategies-that-must-be-combined/)
- [The Evidence for Active Recall and Spaced Repetition](https://recallify.ai/evidence-for-active-recall-and-spaced-repetition/)
- [Spaced Repetition Promotes Efficient and Effective Learning (Kang, 2016)](https://www.researchgate.net/publication/290511665_Spaced_Repetition_Promotes_Efficient_and_Effective_Learning_Policy_Implications_for_Instruction)
- [Systematic review: spaced learning, interleaving, retrieval practice — JACR](https://www.jacr.org/article/S1546-1440(23)00646-4/fulltext)

## How each technique maps to the app

| Technique | Feature | Where |
|---|---|---|
| Retrieval practice | Review cards: "Explain from memory: {topic}" — user recalls aloud/on paper, then self-grades | `/review` page, `backend/app/services/review_service.py` |
| Spaced repetition | SM-2-lite scheduler with expanding intervals (1 → 3 → interval×ease days) | `review_service.grade_card` |
| Feynman technique | Phase completion requires a "Feynman explanation" — teach the phase to a beginner, min 100 chars | Trail page, `POST /trail/phase/{id}/complete` |
| Pomodoro | Built-in 25/5 timer with cycle tracking per day; ~3 cycles ≈ the 1-hour study requirement | Routine page, `PomodoroTimer.tsx` |
| Interleaving | Daily challenge rotates category (physics / math / algorithms) and difficulty follows the trail phase | `challenge_generator.py` |
| Deliberate practice | One challenge/day, no hints, no solutions, PASS/FAIL/PARTIAL + one sentence only | Challenge flow |

## The review system (spaced repetition + active recall)

### Card creation

Cards are generated automatically from trail topics: every topic of every phase the user has **reached** becomes one card (e.g. reaching Phase 1 seeds HTTP, TCP/IP, DNS, ...). Seeding is idempotent and runs on `GET /api/v1/reviews/due` — advancing a phase automatically feeds new topics into the deck. No manual card management: the trail defines what you must remember.

### Review flow (active recall, enforced by UI)

1. Card shows only the topic: **"Explique de memória: HTTP"**.
2. User explains aloud or on paper — *before* anything is revealed. This is the retrieval event that builds memory.
3. User self-grades: **Esqueci (0) · Difícil (1) · Bom (2) · Fácil (3)**.
4. The scheduler sets the next due date.

### Scheduling algorithm (SM-2-lite)

Simplified from SuperMemo's SM-2, the same family used by Anki:

```
state per card: ease (start 2.5, clamp 1.3–3.0), interval_days, repetitions

grade 0 (forgot):   repetitions = 0; interval = 1 day; ease -= 0.2
grade ≥ 1:          repetitions += 1
                    rep 1 → interval = 1 day
                    rep 2 → interval = 3 days
                    rep ≥ 3 → interval = interval × ease × m
                              (m = 0.8 hard, 1.0 good, 1.3 easy)
grade 1 (hard):     ease -= 0.15        grade 3 (easy): ease += 0.15

due_date = today + interval
```

Typical "good" progression: 1 → 3 → 8 → 20 → 50 days. Cards with ≥3 repetitions count as "mature" in stats.

### Integration with the routine

- Grading any review card auto-logs the routine item **"Review one concept from the learning trail"** as DONE for the day.
- Submitting the daily challenge auto-logs **"Daily challenge attempted"**.
- Wake-up and spending items remain manual — they happen outside the app.

## A recommended day

1. **Check in** wake-up before 7:00 (the server decides DONE vs LATE).
2. **Review** — clear the due cards (5–15 min of pure retrieval).
3. **Pomodoro study** — 2–3 focus cycles on the current trail phase topics (≥ 1h).
4. **Daily challenge** — derivation on paper, then code in the plain textarea.
5. **Phase work** — type the exercises; when the whole phase is solid, write the Feynman explanation to unlock the next one.

## What is deliberately absent

- No re-reading/highlighting features — rated low-utility by the evidence.
- No streaks, badges or gamification — the data is the feedback.
- No AI explanations — retrieval only works if *you* generate the answer.
