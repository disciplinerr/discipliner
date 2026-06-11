import logging
import os
import re
import subprocess
import tempfile
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.core.limiter import limiter
from app.models import ChallengeSubmission, DailyChallenge, SubmissionResult, User
from app.schemas import (
    ChallengeHistoryItem,
    ChallengeOut,
    CodeExecuteRequest,
    CodeExecuteResult,
    CustomChallengeOut,
    CustomChallengeRequest,
    SubmissionCreate,
    SubmissionOut,
)
from app.services.challenge_generator import (
    evaluate_submission,
    generate_custom_challenge,
    get_or_create_today_challenge,
)
from app.services.routine_service import log_item_if_absent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/challenges", tags=["challenges"])

_EXEC_TIMEOUT = 5
_COMPILE_TIMEOUT = 10

# Allowlist for locale parameter to prevent prompt injection
_ALLOWED_LOCALES = frozenset({"pt-BR", "pt", "en", "en-US"})

# Minimal safe environment for subprocess execution — no secrets inherited
_SANDBOX_ENV = {
    "PATH": "/usr/bin:/bin",
    "JAVA_HOME": os.environ.get("JAVA_HOME", ""),
}


@router.get("/today", response_model=ChallengeOut)
def today_challenge(
    locale: str = Query(default="pt-BR", max_length=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if locale not in _ALLOWED_LOCALES:
        locale = "pt-BR"
    return get_or_create_today_challenge(db, current_user, locale)


@router.post("/{challenge_id}/submit", response_model=SubmissionOut)
def submit(
    challenge_id: int,
    payload: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    challenge = db.get(DailyChallenge, challenge_id)
    if challenge is None or challenge.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Challenge not found")

    result, reason = evaluate_submission(challenge, payload.code_submission)
    submission = ChallengeSubmission(
        challenge_id=challenge.id,
        user_id=current_user.id,
        math_derivation=payload.math_derivation or None,
        code_submission=payload.code_submission,
        result=SubmissionResult(result),
        reason=reason,
    )
    db.add(submission)
    log_item_if_absent(db, current_user.id, "daily_challenge")
    db.commit()
    db.refresh(submission)
    return submission


@router.get("/history", response_model=list[ChallengeHistoryItem])
def history(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    challenges = db.scalars(
        select(DailyChallenge)
        .where(DailyChallenge.user_id == current_user.id)
        .order_by(DailyChallenge.date.desc())
    ).all()
    return [
        ChallengeHistoryItem(
            challenge=ChallengeOut.model_validate(c),
            submissions=[
                SubmissionOut.model_validate(s)
                for s in sorted(c.submissions, key=lambda s: s.submitted_at, reverse=True)
            ],
        )
        for c in challenges
    ]


@router.post("/execute", response_model=CodeExecuteResult)
@limiter.limit("20/minute")
def execute_code(
    request: Request,
    payload: CodeExecuteRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        if payload.language == "java":
            output = _run_java(payload.code)
        else:
            output = _run_c(payload.code)
        error = any(
            marker in output
            for marker in ("error:", "error\n", "Exception", "cannot find symbol")
        )
        return CodeExecuteResult(output=output[:8000], error=error)
    except subprocess.TimeoutExpired:
        return CodeExecuteResult(output="Timeout: execução excedeu 5 segundos.", error=True)
    except Exception as exc:
        logger.exception("Code execution failed")
        return CodeExecuteResult(output="Execution failed.", error=True)


@router.post("/generate-custom", response_model=CustomChallengeOut)
@limiter.limit("5/minute")
def generate_custom(
    request: Request,
    payload: CustomChallengeRequest,
    current_user: User = Depends(get_current_user),
):
    locale = payload.locale if payload.locale in _ALLOWED_LOCALES else "pt-BR"
    try:
        data = generate_custom_challenge(payload.description, locale)
        return CustomChallengeOut(**{k: str(v) for k, v in data.items()})
    except Exception:
        logger.exception("Custom challenge generation failed")
        raise HTTPException(status_code=502, detail="Challenge generation failed. Try again later.")


def _run_java(code: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        match = re.search(r"public\s+class\s+(\w+)", code)
        classname = match.group(1) if match else "Main"
        srcfile = os.path.join(tmpdir, f"{classname}.java")
        with open(srcfile, "w") as f:
            f.write(code)
        compile_result = subprocess.run(
            ["javac", srcfile],
            capture_output=True,
            text=True,
            timeout=_COMPILE_TIMEOUT,
            cwd=tmpdir,
            env=_SANDBOX_ENV,
        )
        if compile_result.returncode != 0:
            return compile_result.stderr or compile_result.stdout
        run_result = subprocess.run(
            ["java", "-cp", tmpdir, "-Xmx128m", "-Xss2m", classname],
            capture_output=True,
            text=True,
            timeout=_EXEC_TIMEOUT,
            cwd=tmpdir,
            env=_SANDBOX_ENV,
        )
        return (run_result.stdout + run_result.stderr).strip()


def _run_c(code: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        srcfile = os.path.join(tmpdir, "main.c")
        outfile = os.path.join(tmpdir, "main")
        with open(srcfile, "w") as f:
            f.write(code)
        compile_result = subprocess.run(
            ["gcc", "-o", outfile, srcfile, "-lm", "-Wall"],
            capture_output=True,
            text=True,
            timeout=_COMPILE_TIMEOUT,
            env=_SANDBOX_ENV,
        )
        if compile_result.returncode != 0:
            return compile_result.stderr or compile_result.stdout
        run_result = subprocess.run(
            [outfile],
            capture_output=True,
            text=True,
            timeout=_EXEC_TIMEOUT,
            cwd=tmpdir,
            env=_SANDBOX_ENV,
        )
        return (run_result.stdout + run_result.stderr).strip()
