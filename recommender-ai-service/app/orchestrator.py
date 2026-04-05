"""
ChatOrchestrator
─────────────────
Central coordinator for the chatbot pipeline:

  message → IntentDetector → EntityExtractor
         → [module dispatch] → ResponseComposer → ChatResponse

Each intent routes to the appropriate service(s).
"""
from __future__ import annotations
import logging
import uuid
from typing import Any

from .services.intent_detector  import detect as detect_intent
from .services.entity_extractor import extract as extract_entities
from .services.rag_retrieval    import retrieve as rag_retrieve, build_context_string
from .services.recommendation   import recommendation_service as rec_svc
from .services.behavior_analysis import behavior_service
from .services.order_support    import order_support_service
from .services.response_composer import compose

logger = logging.getLogger(__name__)

# In-memory session store (replace with Redis for production)
_sessions: dict[str, list[dict]] = {}
MAX_HISTORY = 6


def _get_history(session_id: str) -> list[dict]:
    return _sessions.get(session_id, [])[-MAX_HISTORY:]


def _save_message(session_id: str, role: str, content: str) -> None:
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append({"role": role, "content": content})
    # Trim
    if len(_sessions[session_id]) > MAX_HISTORY * 2:
        _sessions[session_id] = _sessions[session_id][-MAX_HISTORY * 2:]


def _get_interactions(customer_id: int) -> dict[str, dict[int, int]]:
    """Load interaction counts from DB via Django ORM."""
    try:
        from app.models import CustomerBookInteraction  # type: ignore
        qs = CustomerBookInteraction.objects.filter(customer_id=customer_id)
        result: dict[str, dict[int, int]] = {}
        for ix in qs:
            result.setdefault(ix.interaction_type, {})[ix.book_id] = ix.count
        return result
    except Exception as exc:
        logger.debug("Could not load interactions: %s", exc)
        return {}


class ChatOrchestrator:
    def process(
        self,
        message:      str,
        customer_id:  int | None = None,
        session_id:   str | None = None,
        quick_action: str | None = None,
    ) -> dict[str, Any]:
        """
        Full pipeline: detect → extract → dispatch → compose.
        Returns ChatResponse-compatible dict.
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        _save_message(session_id, "user", message)

        # 1. Intent detection
        intent, confidence = detect_intent(message, quick_action)
        logger.info("Intent=%s (%.2f) | C%s | msg=%s", intent, confidence, customer_id, message[:60])

        # 2. Entity extraction
        entities = extract_entities(message, intent)

        # 3. Dispatch to services
        data: dict[str, Any] = {}
        recommendations: list[dict] = []
        sources: list[dict] = []

        if intent in ("faq", "return_policy", "payment_support", "shipping_support"):
            # RAG retrieval from KB
            category_map = {
                "return_policy":    "policy",
                "payment_support":  "policy",
                "shipping_support": "policy",
                "faq":              None,
            }
            kb_cat = category_map.get(intent)
            entries = rag_retrieve(message, top_k=3, category=kb_cat)
            sources = entries
            data["sources"] = entries

        elif intent == "product_advice":
            # Behavior + Recommendation + RAG context
            interactions = _get_interactions(customer_id) if customer_id else {}
            flat_interactions = {
                itype: {bid: cnt for bid, cnt in book_counts.items()}
                for itype, book_counts in interactions.items()
            }
            recs = rec_svc.get_personalized(
                customer_id=customer_id or 0,
                interactions=flat_interactions,
                budget_min=entities.get("budget_min"),
                budget_max=entities.get("budget_max"),
                category=entities.get("category"),
            )
            # If no personalized recs, fall back to popular
            if not recs:
                recs = rec_svc.get_popular(limit=5)
            recommendations = recs
            data["recommendations"] = recs

            # RAG context for additional context
            rag_entries = rag_retrieve(message, top_k=2, category="book")
            data["rag_context"] = build_context_string(rag_entries)
            sources = rag_entries

        elif intent == "order_support":
            if not customer_id:
                data["order_data"] = {
                    "found":   False,
                    "message": "Vui lòng đăng nhập để tra cứu đơn hàng của bạn. 🔒",
                }
            else:
                order_id = entities.get("order_id")
                data["order_data"] = order_support_service.get_order_info(customer_id, order_id)

        elif intent == "general_search":
            keywords = entities.get("product_keywords", [])
            query    = " ".join(keywords) if keywords else message
            category = entities.get("category")

            # Search products
            from .clients.catalog_client import catalog_client
            books = catalog_client.search_products(
                query=query,
                category=category,
                min_price=entities.get("budget_min"),
                max_price=entities.get("budget_max"),
            )
            # Format as recommendations
            from .clients.comment_client import comment_client as cc
            product_ids = [b["id"] for b in books if b.get("id")]
            ratings = cc.get_reviews_for_products(product_ids) if product_ids else {}
            recs = []
            for b in books[:8]:
                bid = b.get("id")
                rm  = ratings.get(bid, {})
                recs.append({
                    "product_id": bid,
                    "title":      b.get("title", ""),
                    "author":     b.get("author", ""),
                    "category":   b.get("category", ""),
                    "price":      float(b.get("price", 0)),
                    "score":      rm.get("avg", 0),
                    "reason":     "kết quả tìm kiếm",
                    "avg_rating": round(rm.get("avg", 0), 2),
                })
            recommendations = recs
            data["recommendations"] = recs

            # Also RAG
            rag_entries = rag_retrieve(message, top_k=2)
            sources = rag_entries
            data["sources"] = rag_entries

        else:  # fallback
            entries = rag_retrieve(message, top_k=2)
            sources = entries
            data["sources"] = entries

        # 4. Compose response
        answer = compose(intent, entities, data, customer_id)
        _save_message(session_id, "assistant", answer)

        return {
            "session_id":      session_id,
            "intent":          intent,
            "confidence":      round(confidence, 3),
            "answer":          answer,
            "recommendations": recommendations,
            "sources":         [{"title": s["title"], "snippet": s["content"][:150]} for s in sources],
            "meta": {
                "entities":    entities,
                "customer_id": customer_id,
            },
        }


orchestrator = ChatOrchestrator()
