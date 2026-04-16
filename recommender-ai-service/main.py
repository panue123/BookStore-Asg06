"""AI Assistant Service - FastAPI entrypoint."""
import logging
import os

import django
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import setup_logging
from app.api.routes import router


setup_logging()
logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recommender_ai_service.settings")
try:
    django.setup()
    logger.info("Django ORM initialized")
except Exception as exc:
    logger.warning("Django setup failed (non-fatal): %s", exc)


app = FastAPI(
    title="AI Recommender & Chatbot Service",
    description=(
        "AI-powered assistant for e-commerce platform. "
        "Includes recommendation list + chatbot using LSTM/RAG hybrid stack. "
        "No external LLM — all inference is local."
    ),
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
async def startup() -> None:
    from app.services.kb_ingestion import kb_service
    from app.services.rag_retrieval import rag_service

    count = kb_service.load_from_disk()
    try:
        indexed = rag_service.load_index()
        if not indexed and count > 0:
            rag_service.build_index()
    except Exception as exc:
        logger.warning("FAISS load/build warning: %s", exc)

    logger.info("AI Service ready. KB entries=%d", count)
