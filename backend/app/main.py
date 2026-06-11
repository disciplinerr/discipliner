from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.v1.router import api_router

_docs_url = os.getenv("DOCS_URL")
docs_url = f"/{_docs_url.strip('/')}" if _docs_url else None

app = FastAPI(title="Discipliner API", version="1.0.0", docs_url=docs_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}
