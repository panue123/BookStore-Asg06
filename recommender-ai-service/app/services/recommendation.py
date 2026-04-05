"""
RecommendationService
──────────────────────
Personalized recommendations combining:
  1. Behavior scores (interaction history)
  2. Content-based filtering (category/author affinity)
  3. Collaborative signals (rating popularity)
  4. Budget filtering

Each recommendation includes a human-readable reason (explainability).
"""
from __future__ import annotations
import logging
import math
from collections import defaultdict
from typing import Any

from ..clients.catalog_client import catalog_client
from ..clients.order_client import order_client
from ..clients.comment_client import comment_client
from ..core.config import PURCHASE_THRESHOLD, RECOMMENDATION_LIMIT

logger = logging.getLogger(__name__)

WEIGHTS = {"view": 1, "search": 2, "cart": 4, "purchase": 8, "rate": 3}


def _get_purchased_ids(customer_id: int) -> set[int]:
    orders = order_client.get_orders_by_customer(customer_id)
    ids: set[int] = set()
    for order in orders:
        for item in order.get("items", []):
            if item.get("book_id"):
                ids.add(item["book_id"])
    return ids


def _rating_map(product_ids: list[int]) -> dict[int, dict]:
    return comment_client.get_reviews_for_products(product_ids)


def _popularity_score(book_id: int, ratings: dict[int, dict]) -> float:
    rm = ratings.get(book_id, {})
    if not rm.get("count", 0):
        return 0.0
    return (rm["avg"] / 5.0) * math.log1p(rm["count"]) * 0.3


def get_personalized(
    customer_id: int,
    interactions: dict[str, dict[int, int]],   # {type: {book_id: count}}
    limit: int = RECOMMENDATION_LIMIT,
    budget_min: float | None = None,
    budget_max: float | None = None,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """
    Generate personalized recommendations.
    interactions: {interaction_type: {book_id: count}}
    """
    # Flatten to {book_id: weighted_score}
    book_scores: dict[int, float] = defaultdict(float)
    for itype, book_counts in interactions.items():
        w = WEIGHTS.get(itype, 1)
        for bid, cnt in book_counts.items():
            book_scores[bid] += w * cnt

    purchased = _get_purchased_ids(customer_id)

    # Category/author affinity from high-score books
    cat_affinity:    dict[str, float] = defaultdict(float)
    author_affinity: dict[str, float] = defaultdict(float)
    for bid, score in book_scores.items():
        book = catalog_client.get_product_by_id(bid)
        if not book:
            continue
        if book.get("category"):
            cat_affinity[book["category"]] += score
        if book.get("author"):
            author_affinity[book["author"]] += score

    top_cats    = {c for c, _ in sorted(cat_affinity.items(), key=lambda x: x[1], reverse=True)[:3]}
    top_authors = {a for a, _ in sorted(author_affinity.items(), key=lambda x: x[1], reverse=True)[:3]}

    # Fetch all books
    all_books = catalog_client.get_all_products(limit=500)
    if not all_books:
        return []

    product_ids = [b["id"] for b in all_books if b.get("id")]
    ratings     = _rating_map(product_ids)

    candidates: list[dict] = []
    for book in all_books:
        bid = book.get("id")
        if not bid or bid in purchased or book.get("stock", 0) <= 0:
            continue

        price = float(book.get("price", 0))
        if budget_min is not None and price < budget_min:
            continue
        if budget_max is not None and price > budget_max:
            continue
        if category and book.get("category") != category:
            continue

        score   = 0.0
        reasons = []

        # Direct behavior signal
        bscore = book_scores.get(bid, 0)
        if bscore >= PURCHASE_THRESHOLD:
            score += bscore * 0.4
            reasons.append(f"bạn đã tương tác {int(bscore)} lần")

        # Category match
        if book.get("category") in top_cats:
            score += 2.0
            reasons.append(f"thể loại {book['category']} bạn yêu thích")

        # Author match
        if book.get("author") in top_authors:
            score += 1.5
            reasons.append(f"tác giả {book['author']} bạn quan tâm")

        # Popularity
        pop = _popularity_score(bid, ratings)
        score += pop
        rm = ratings.get(bid, {})
        if rm.get("avg", 0) >= 4.0:
            reasons.append(f"đánh giá cao ({rm['avg']:.1f}★/{rm['count']} lượt)")

        if score > 0 or not reasons:
            candidates.append({
                "product_id": bid,
                "title":      book.get("title", ""),
                "author":     book.get("author", ""),
                "category":   book.get("category", ""),
                "price":      price,
                "score":      round(score, 3),
                "reason":     ", ".join(reasons) if reasons else "phổ biến trong cộng đồng",
                "avg_rating": round(rm.get("avg", 0), 2),
            })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    logger.info("Generated %d recommendations for C%s", min(len(candidates), limit), customer_id)
    return candidates[:limit]


def get_similar(product_id: int, limit: int = 6) -> list[dict[str, Any]]:
    """
    Content-based similar products.
    Similarity = same category + author + price range proximity.
    """
    target = catalog_client.get_product_by_id(product_id)
    if not target:
        return []

    all_books = catalog_client.get_all_products(limit=500)
    product_ids = [b["id"] for b in all_books if b.get("id")]
    ratings = _rating_map(product_ids)

    target_cat    = target.get("category", "")
    target_author = target.get("author", "")
    target_price  = float(target.get("price", 0))

    candidates = []
    for book in all_books:
        bid = book.get("id")
        if not bid or bid == product_id or book.get("stock", 0) <= 0:
            continue

        score   = 0.0
        reasons = []

        if book.get("category") == target_cat:
            score += 3.0
            reasons.append(f"cùng thể loại {target_cat}")
        if book.get("author") == target_author and target_author:
            score += 2.5
            reasons.append(f"cùng tác giả {target_author}")

        price = float(book.get("price", 0))
        if target_price > 0:
            price_diff = abs(price - target_price) / target_price
            if price_diff < 0.3:
                score += 1.0
                reasons.append("tầm giá tương đương")

        pop = _popularity_score(bid, ratings)
        score += pop

        if score > 0:
            rm = ratings.get(bid, {})
            candidates.append({
                "product_id": bid,
                "title":      book.get("title", ""),
                "author":     book.get("author", ""),
                "category":   book.get("category", ""),
                "price":      price,
                "score":      round(score, 3),
                "reason":     ", ".join(reasons) if reasons else "sản phẩm tương tự",
                "avg_rating": round(rm.get("avg", 0), 2),
            })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:limit]


def get_popular(limit: int = 10) -> list[dict[str, Any]]:
    """Global popularity based on ratings."""
    all_books = catalog_client.get_all_products(limit=500)
    product_ids = [b["id"] for b in all_books if b.get("id")]
    ratings = _rating_map(product_ids)

    result = []
    for book in all_books:
        bid = book.get("id")
        if not bid or book.get("stock", 0) <= 0:
            continue
        rm    = ratings.get(bid, {})
        score = _popularity_score(bid, ratings)
        if score > 0 or rm.get("count", 0) > 0:
            result.append({
                "product_id": bid,
                "title":      book.get("title", ""),
                "author":     book.get("author", ""),
                "category":   book.get("category", ""),
                "price":      float(book.get("price", 0)),
                "score":      round(score, 3),
                "reason":     f"phổ biến ({rm.get('count', 0)} đánh giá)",
                "avg_rating": round(rm.get("avg", 0), 2),
            })

    result.sort(key=lambda x: x["score"], reverse=True)
    return result[:limit]


recommendation_service = type("RecService", (), {
    "get_personalized": staticmethod(get_personalized),
    "get_similar":      staticmethod(get_similar),
    "get_popular":      staticmethod(get_popular),
})()
