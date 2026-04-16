"""FastAPI routers for AI Assistant Service."""
from __future__ import annotations
import logging
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from .schemas import (
    ChatRequest, ChatResponse,
    RecommendationResponse, RecommendationItem,
    SimilarProductResponse,
    BehaviorProfile,
    KBStatusResponse, KBReindexResponse,
    TrackRequest,
)
from ..orchestrator import orchestrator
from ..services.recommendation   import recommendation_service as rec_svc
from ..services.behavior_analysis import behavior_service
from ..services.kb_ingestion     import kb_service
from ..services.rag_retrieval    import rag_service
from ..clients.order_client      import order_client
from ..clients.comment_client    import comment_client

logger = logging.getLogger(__name__)
router = APIRouter()


def _load_customer_signals(customer_id: int) -> tuple[dict, list]:
    interactions: dict = {}
    event_sequence: list = []

    # 1) Explicit tracked interactions from recommender DB
    try:
        from django.apps import apps
        Interaction = apps.get_model("app", "CustomerProductInteraction")
        qs = Interaction.objects.filter(customer_id=customer_id)
        for row in qs:
            itype = row.interaction_type
            interactions[itype] = interactions.get(itype, 0) + row.count
            event_sequence.append({
                "product_id":       row.product_id,
                "interaction_type": itype,
                "timestamp":        int(row.timestamp.timestamp()),
                "price_range":      row.price_range,
                "category_idx":     0,
            })
    except Exception as exc:
        logger.debug("Could not load DB interactions: %s", exc)

    # 2) Purchase signals from order-service
    try:
        now_ts = int(time.time())
        orders = order_client.get_orders_by_customer(customer_id)
        for order in orders:
            for item in order.get("items", []):
                pid = item.get("product_id") or item.get("book_id")
                if not pid:
                    continue
                interactions["purchase"] = interactions.get("purchase", 0) + 1
                event_sequence.append({
                    "product_id":       int(pid),
                    "interaction_type": "purchase",
                    "timestamp":        now_ts,
                    "price_range":      2,
                    "category_idx":     0,
                })
    except Exception as exc:
        logger.debug("Could not load order signals: %s", exc)

    # 3) Rating signals from comment-rate-service
    try:
        now_ts = int(time.time())
        comments = comment_client.get_all_comments()
        for c in comments:
            if c.get("customer_id") != customer_id:
                continue
            pid = c.get("product_id") or c.get("book_id")
            if not pid:
                continue
            interactions["rate"] = interactions.get("rate", 0) + 1
            event_sequence.append({
                "product_id":       int(pid),
                "interaction_type": "rate",
                "timestamp":        now_ts,
                "price_range":      2,
                "category_idx":     0,
            })
    except Exception as exc:
        logger.debug("Could not load comment signals: %s", exc)

    return interactions, event_sequence


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health", tags=["system"])
def health():
    stats = kb_service.get_stats()
    from ..infrastructure.ml.lstm_model import LSTM_MODEL_PATH
    from ..infrastructure.graph.neo4j_adapter import neo4j_adapter
    return {
        "service": "recommender-ai-service",
        "status":  "healthy",
        "modules": ["intent_detector", "entity_extractor", "behavior_analysis",
                    "recommendation", "kb_ingestion", "rag_retrieval",
                    "order_support", "response_composer", "orchestrator"],
        "kb_stats":      stats,
        "lstm_loaded":   LSTM_MODEL_PATH.exists(),
        "graph_enabled": neo4j_adapter.is_available(),
        "hybrid_weights": {"lstm": 0.40, "graph": 0.25, "content": 0.25, "rating": 0.10},
    }


# ── Chat ──────────────────────────────────────────────────────────────────────

@router.post("/api/v1/chat", response_model=ChatResponse, tags=["chat"])
def chat(req: ChatRequest):
    """
    Main chatbot endpoint.
    Pipeline: IntentDetector → EntityExtractor → Orchestrator → ResponseComposer
    Supports: faq, product_advice, order_support, payment_support,
              shipping_support, return_policy, general_search, fallback.
    """
    try:
        result = orchestrator.process(
            message=req.message,
            customer_id=req.customer_id,
            session_id=req.session_id,
            quick_action=req.quick_action,
        )
        return ChatResponse(**result)
    except Exception as exc:
        logger.exception("Chat error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Recommendations ───────────────────────────────────────────────────────────

@router.get("/api/v1/recommend/{customer_id}", response_model=RecommendationResponse, tags=["recommend"])
def recommend(
    customer_id: int,
    limit:        int            = Query(8, ge=1, le=20),
    category:     Optional[str]  = None,
    budget_max:   Optional[float] = None,
):
    """Personalized recommendations — LSTM behavior sequence + interaction history."""
    try:
        interactions, event_sequence = _load_customer_signals(customer_id)

        recs = rec_svc.get_personalized(
            customer_id=customer_id,
            interactions={itype: {0: cnt} for itype, cnt in interactions.items()},
            limit=limit,
            budget_max=budget_max,
            category=category,
            event_sequence=event_sequence,
        )
        items = [
            RecommendationItem(
                product_id=r.get("product_id") or r.get("id") or 0,
                title=r.get("title", ""),
                author=r.get("author"),
                category=r.get("category"),
                price=float(r.get("price", 0)),
                score=float(r.get("score", 0)),
                reason=r.get("reason", ""),
                avg_rating=float(r.get("avg_rating", 0)),
            )
            for r in recs
        ]
        return RecommendationResponse(
            customer_id=customer_id,
            recommendations=items,
            source="lstm_hybrid",
        )
    except Exception as exc:
        logger.exception("Recommend error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/v1/recommend/similar/{product_id}", response_model=SimilarProductResponse, tags=["recommend"])
def similar(product_id: int, limit: int = Query(6, ge=1, le=12)):
    """Similar product recommendations based on category and attributes."""
    try:
        similar_products = rec_svc.get_similar(product_id=product_id, limit=limit)
        items = [
            RecommendationItem(
                product_id=r.get("product_id") or r.get("id") or 0,
                title=r.get("title", ""),
                author=r.get("author"),
                category=r.get("category"),
                price=float(r.get("price", 0)),
                score=float(r.get("score", 0)),
                reason=r.get("reason", "Sản phẩm tương tự"),
                avg_rating=float(r.get("avg_rating", 0)),
            )
            for r in similar_products
        ]
        return SimilarProductResponse(product_id=product_id, similar=items)
    except Exception as exc:
        logger.exception("Similar error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Behavior Analysis ─────────────────────────────────────────────────────────

@router.get("/api/v1/analyze-customer/{customer_id}", response_model=BehaviorProfile, tags=["behavior"])
def analyze_customer(customer_id: int):
    """Analyze customer behavior profile using LSTM/MLP/rule-based pipeline."""
    try:
        interactions, event_sequence = _load_customer_signals(customer_id)

        profile = behavior_service.analyze(
            customer_id=customer_id,
            interactions=interactions,
            event_sequence=event_sequence if event_sequence else None,
        )
        return BehaviorProfile(**{k: v for k, v in profile.items() if k != "customer_id"},
                               customer_id=customer_id)
    except Exception as exc:
        logger.exception("Analyze error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Interaction Tracking ──────────────────────────────────────────────────────

@router.post("/api/v1/track", tags=["behavior"])
def track(req: TrackRequest):
    """Track a customer interaction event — persists to DB and Neo4j graph."""
    try:
        from django.apps import apps
        try:
            Interaction = apps.get_model("app", "CustomerProductInteraction")
        except LookupError:
            Interaction = apps.get_model("app", "CustomerBookInteraction")

        interaction_type = "view" if req.interaction_type == "click" else req.interaction_type

        obj, created = Interaction.objects.get_or_create(
            customer_id=req.customer_id,
            product_id=req.product_id or 0,
            interaction_type=interaction_type,
            defaults={"count": 1, "rating": req.rating},
        )
        if not created:
            obj.count += 1
            if req.rating is not None:
                obj.rating = req.rating
            obj.save(update_fields=["count", "rating", "timestamp"])

        # Write to Neo4j graph for hybrid scoring
        if req.product_id:
            from ..infrastructure.graph.neo4j_adapter import neo4j_adapter
            rel_map = {"view": "VIEWED", "click": "VIEWED", "cart": "CART", "purchase": "PURCHASED", "rate": "RATED"}
            rel_type = rel_map.get(interaction_type, "VIEWED")
            # Fetch product meta for graph node
            product_meta: dict = {}
            try:
                from ..clients.catalog_client import catalog_client
                p = catalog_client.get_product_by_id(req.product_id)
                if p:
                    product_meta = {"name": p.get("title", ""), "category": p.get("category", ""),
                                    "brand": p.get("brand", ""), "price": p.get("price", 0)}
            except Exception:
                pass
            neo4j_adapter.write_interaction(
                customer_id=req.customer_id,
                product_id=req.product_id,
                rel_type=rel_type,
                props={"rating": req.rating or 0},
                product_meta=product_meta,
            )

        return {"tracked": True, "customer_id": req.customer_id,
            "product_id": req.product_id, "type": interaction_type}
    except Exception as exc:
        logger.warning("Track failed: %s", exc)
        return {"tracked": False, "error": str(exc)}


# ── KB Management ─────────────────────────────────────────────────────────────

@router.post("/api/v1/kb/reindex", response_model=KBReindexResponse, tags=["kb"])
def kb_reindex():
    """Reindex Knowledge Base from product-service + reviews + seed data."""
    try:
        count = kb_service.reindex()
        rag_service.build_index()
        return KBReindexResponse(indexed=count, message=f"KB reindexed: {count} entries")
    except Exception as exc:
        logger.exception("KB reindex error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/v1/kb/status", response_model=KBStatusResponse, tags=["kb"])
def kb_status():
    """Get Knowledge Base status."""
    stats = kb_service.get_stats()
    from ..core.config import FAISS_INDEX_PATH
    return KBStatusResponse(
        total_entries=stats["total_entries"],
        by_category=stats["by_category"],
        faiss_indexed=FAISS_INDEX_PATH.exists(),
        index_size=stats["total_entries"],
    )
