"""Idempotent seeding of trail phases and the fallback challenge pool.

Run: python -m app.db.seed
"""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Difficulty, FallbackChallenge, TrailPhase

PHASES = [
    {
        "number": 1,
        "name": "Foundations",
        "weeks": "Weeks 1-3",
        "topics": "HTTP\nTCP/IP\nDNS\nHow servers work\nProcesses\nFile descriptors",
        "exercises": "Build a raw TCP echo server in C\nImplement an HTTP/1.1 GET parser in Python",
    },
    {
        "number": 2,
        "name": "Backend Fundamentals",
        "weeks": "Weeks 4-7",
        "topics": "REST design\nSQL\nIndexes\nTransactions\nAuth (JWT, sessions)\nHashing",
        "exercises": "Build a REST API from scratch in FastAPI\nWrite raw SQL migrations",
    },
    {
        "number": 3,
        "name": "Systems & Concurrency",
        "weeks": "Weeks 8-11",
        "topics": "Threads\nAsync I/O\nConnection pooling\nCaching (Redis)\nMessage queues",
        "exercises": "Implement a job queue\nBenchmark a slow query and fix it",
    },
    {
        "number": 4,
        "name": "DevOps Foundations",
        "weeks": "Weeks 12-16",
        "topics": "Docker\nDocker Compose\nLinux basics\nEnvironment variables\nCI/CD concepts",
        "exercises": "Containerize an app\nWrite a Dockerfile from scratch\nSet up a GitHub Actions pipeline",
    },
    {
        "number": 5,
        "name": "Infrastructure",
        "weeks": "Weeks 17-22",
        "topics": "VPS\nSSH\nNginx\nReverse proxy\nSSL/TLS\nMonitoring (Prometheus basics)",
        "exercises": "Deploy an app to a VPS manually\nConfigure Nginx\nSet up basic monitoring",
    },
    {
        "number": 6,
        "name": "Advanced Backend",
        "weeks": "Weeks 23-28",
        "topics": "Microservices tradeoffs\nEvent-driven architecture\nSystem design basics",
        "exercises": "Design and document a system\nImplement one service with a message queue",
    },
]

FALLBACK_CHALLENGES = [
    {
        "title": "Projectile Range Optimizer",
        "math_problem": (
            "Given initial velocity v and angle θ, derive the formula for maximum "
            "horizontal range R. Show that R is maximized when θ = 45°."
        ),
        "programming_task": (
            "Implement a function `max_range(v: float) -> float` in Python that returns "
            "the maximum horizontal range for a given initial velocity. Use g = 9.8 m/s²."
        ),
        "difficulty": Difficulty.beginner,
        "category": "physics",
        "expected_output_example": "max_range(10) → 10.2",
        "constraints": "Do not use any libraries. Only math operations.",
    },
    {
        "title": "Sum of Arithmetic Series",
        "math_problem": (
            "Derive the closed-form formula for the sum 1 + 2 + ... + n. "
            "Prove it by induction."
        ),
        "programming_task": (
            "Implement `series_sum(n: int) -> int` in Python using the closed-form "
            "formula, and `series_sum_loop(n: int) -> int` using a loop. Verify they "
            "agree for n in [1, 1000]."
        ),
        "difficulty": Difficulty.beginner,
        "category": "math",
        "expected_output_example": "series_sum(100) → 5050",
        "constraints": "No external libraries.",
    },
    {
        "title": "Free Fall Time",
        "math_problem": (
            "From the kinematics equation s = ½gt², derive the time t for an object "
            "dropped from height h to reach the ground."
        ),
        "programming_task": (
            "Implement `fall_time(h: float) -> float` in Python returning the fall time "
            "in seconds for height h meters. Use g = 9.8 m/s²."
        ),
        "difficulty": Difficulty.beginner,
        "category": "physics",
        "expected_output_example": "fall_time(20) → 2.02",
        "constraints": "Only the math module is allowed.",
    },
    {
        "title": "Newton's Square Root",
        "math_problem": (
            "Derive the Newton-Raphson iteration formula for computing √a, starting "
            "from f(x) = x² − a. Show the update rule x_{n+1} = (x_n + a/x_n) / 2."
        ),
        "programming_task": (
            "Implement `newton_sqrt(a: float, eps: float = 1e-9) -> float` in Python "
            "using the derived iteration. Do not use math.sqrt or **0.5."
        ),
        "difficulty": Difficulty.intermediate,
        "category": "math",
        "expected_output_example": "newton_sqrt(2) → 1.41421356...",
        "constraints": "No math.sqrt, no exponent operator for roots.",
    },
    {
        "title": "Orbital Velocity",
        "math_problem": (
            "Equate gravitational force and centripetal force to derive the circular "
            "orbital velocity v = sqrt(GM/r) for a satellite at radius r."
        ),
        "programming_task": (
            "Implement `orbital_velocity(r: float) -> float` in Python for Earth "
            "(GM = 3.986e14 m³/s²), returning velocity in m/s for orbital radius r meters."
        ),
        "difficulty": Difficulty.intermediate,
        "category": "physics",
        "expected_output_example": "orbital_velocity(6.771e6) → 7672.6",
        "constraints": "Only the math module is allowed.",
    },
    {
        "title": "Damped Oscillator Energy",
        "math_problem": (
            "For a damped harmonic oscillator x(t) = A·e^(−γt)·cos(ωt), derive the "
            "envelope of the mechanical energy over time and show E(t) ≈ E₀·e^(−2γt)."
        ),
        "programming_task": (
            "Implement `energy(t: float, e0: float, gamma: float) -> float` in Python "
            "and a function `half_life(gamma: float) -> float` returning the time for "
            "the energy to halve."
        ),
        "difficulty": Difficulty.advanced,
        "category": "physics",
        "expected_output_example": "half_life(0.5) → 0.693",
        "constraints": "Only the math module is allowed.",
    },
    {
        "title": "Matrix Exponentiation Fibonacci",
        "math_problem": (
            "Show that [[1,1],[1,0]]^n = [[F(n+1),F(n)],[F(n),F(n-1)]] by induction, "
            "where F is the Fibonacci sequence."
        ),
        "programming_task": (
            "Implement `fib(n: int) -> int` in Python using matrix exponentiation by "
            "squaring, achieving O(log n) multiplications."
        ),
        "difficulty": Difficulty.advanced,
        "category": "math",
        "expected_output_example": "fib(50) → 12586269025",
        "constraints": "No external libraries. No memoized recursion — matrix method only.",
    },
]


def seed() -> None:
    db = SessionLocal()
    try:
        for phase in PHASES:
            existing = db.scalar(select(TrailPhase).where(TrailPhase.number == phase["number"]))
            if existing is None:
                db.add(TrailPhase(**phase))
        if db.scalar(select(FallbackChallenge)) is None:
            for challenge in FALLBACK_CHALLENGES:
                db.add(FallbackChallenge(**challenge))
        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
