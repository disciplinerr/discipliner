import json
import logging
import random
from datetime import date

import anthropic
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import DailyChallenge, Difficulty, FallbackChallenge, User

logger = logging.getLogger(__name__)

_LANG_INSTRUCTION = {
    "pt": "Escreva todo o conteúdo do desafio em português do Brasil.",
    "en": "Write all challenge content in English.",
}

CHALLENGE_SYSTEM_PROMPT = """
You are a challenge generator for a self-discipline training application.
Your job is to generate one daily challenge that tests programming skills.
Focus on algorithms, data structures, math, or systems programming.

STRICT RULES:
- Return ONLY a valid JSON object. No markdown, no explanation, no preamble.
- Do not include hints, partial solutions, or answers.
- The problem must be solvable without AI assistance using pen, paper, and code.
- Difficulty must match the requested level.
- Use only standard libraries. No external packages.
- The "math_problem" field: describe the theoretical/conceptual aspect or any math behind it.
- The "programming_task" field: the concrete coding challenge (function signature, behavior).

The JSON object must have exactly these keys:
"title", "math_problem", "programming_task", "difficulty", "category",
"expected_output_example", "constraints"

Categories: algorithms, data-structures, math, systems, strings
"""

EVALUATION_SYSTEM_PROMPT = """
You are a strict code evaluator. Given a problem statement and a code submission,
return ONLY a JSON object with this exact structure:
{"result": "PASS" | "FAIL" | "PARTIAL", "reason": "<one sentence, max 20 words>"}
Do not provide the correct solution. Do not explain further. No markdown.
"""

CUSTOM_CHALLENGE_SYSTEM_PROMPT = """
You are a challenge generator for a programming practice application.
Generate one coding challenge based on the user's description.

STRICT RULES:
- Return ONLY a valid JSON object. No markdown, no explanation, no preamble.
- Do not include hints, partial solutions, or answers.
- Make it concrete and implementable.
- Use only standard libraries.

The JSON object must have exactly these keys:
"title", "math_problem", "programming_task", "difficulty", "category",
"expected_output_example", "constraints"

"difficulty" must be one of: beginner, intermediate, advanced
Categories: algorithms, data-structures, math, systems, strings
"""

PHASE_DIFFICULTY = {
    1: Difficulty.beginner,
    2: Difficulty.beginner,
    3: Difficulty.intermediate,
    4: Difficulty.intermediate,
    5: Difficulty.advanced,
    6: Difficulty.advanced,
}

REQUIRED_KEYS = {
    "title",
    "math_problem",
    "programming_task",
    "difficulty",
    "category",
    "expected_output_example",
    "constraints",
}


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in response")
    return json.loads(text[start : end + 1])


def _lang_instruction(locale: str) -> str:
    key = "pt" if locale.lower().startswith("pt") else "en"
    return _LANG_INSTRUCTION[key]


def _generate_via_claude(difficulty: Difficulty, today: date, locale: str = "pt-BR") -> dict:
    # Note: claude-fable-5 rejects sampling params (temperature/top_p/top_k).
    client = _client()
    response = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=settings.CHALLENGE_MAX_TOKENS,
        system=CHALLENGE_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{_lang_instruction(locale)} "
                    f"Generate one challenge for {today.isoformat()} "
                    f"with difficulty '{difficulty.value}'. "
                    "Pick a category from: algorithms, data-structures, math, systems, strings."
                ),
            }
        ],
    )
    text = next(b.text for b in response.content if b.type == "text")
    data = _extract_json(text)
    missing = REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(f"challenge JSON missing keys: {missing}")
    return data


def generate_custom_challenge(description: str, locale: str = "pt-BR") -> dict:
    """Generate a one-off practice challenge from user description. Not persisted."""
    client = _client()
    response = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=settings.CHALLENGE_MAX_TOKENS,
        system=CUSTOM_CHALLENGE_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{_lang_instruction(locale)} "
                    f"Generate a coding challenge based on this description: {description}"
                ),
            }
        ],
    )
    text = next(b.text for b in response.content if b.type == "text")
    data = _extract_json(text)
    missing = REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(f"challenge JSON missing keys: {missing}")
    return data


def _fallback_challenge(db: Session, difficulty: Difficulty) -> dict:
    pool = db.scalars(
        select(FallbackChallenge).where(FallbackChallenge.difficulty == difficulty)
    ).all()
    if not pool:
        pool = db.scalars(select(FallbackChallenge)).all()
    if not pool:
        raise RuntimeError("fallback challenge pool is empty — run the seed script")
    pick = random.choice(pool)
    return {
        "title": pick.title,
        "math_problem": pick.math_problem,
        "programming_task": pick.programming_task,
        "difficulty": pick.difficulty.value,
        "category": pick.category,
        "expected_output_example": pick.expected_output_example,
        "constraints": pick.constraints,
    }


def get_or_create_today_challenge(
    db: Session, user: User, locale: str = "pt-BR"
) -> DailyChallenge:
    """One challenge per user per day. Cached in DB; never regenerated."""
    today = date.today()
    existing = db.scalar(
        select(DailyChallenge).where(
            DailyChallenge.user_id == user.id, DailyChallenge.date == today
        )
    )
    if existing:
        return existing

    difficulty = PHASE_DIFFICULTY.get(user.current_phase, Difficulty.advanced)
    try:
        data = _generate_via_claude(difficulty, today, locale)
    except Exception:
        logger.exception("Claude generation failed; serving fallback challenge")
        data = _fallback_challenge(db, difficulty)

    challenge = DailyChallenge(
        user_id=user.id,
        date=today,
        title=str(data["title"])[:255],
        math_problem=str(data["math_problem"]),
        programming_task=str(data["programming_task"]),
        difficulty=difficulty,
        category=str(data.get("category", "algorithms"))[:64],
        expected_output_example=str(data.get("expected_output_example", "")),
        constraints=str(data.get("constraints", "")),
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge


def evaluate_submission(challenge: DailyChallenge, code: str) -> tuple[str, str]:
    """Return (result, reason). Result is PASS/FAIL/PARTIAL, or PENDING on API failure."""
    client = _client()
    try:
        response = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=settings.EVALUATION_MAX_TOKENS,
            system=EVALUATION_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Problem:\n{challenge.math_problem}\n\n"
                        f"Programming task:\n{challenge.programming_task}\n\n"
                        f"Constraints:\n{challenge.constraints}\n\n"
                        f"Code submission:\n{code}"
                    ),
                }
            ],
        )
        text = next(b.text for b in response.content if b.type == "text")
        data = _extract_json(text)
        result = str(data.get("result", "")).upper()
        if result not in ("PASS", "FAIL", "PARTIAL"):
            raise ValueError(f"unexpected result: {result!r}")
        return result, str(data.get("reason", ""))[:500]
    except Exception:
        logger.exception("Claude evaluation failed")
        return "PENDING", "Evaluation unavailable — try resubmitting later."
