"""CommentRateServiceClient — supports both book_id (legacy) and product_id."""
from __future__ import annotations
from .base import ServiceClient, _extract_list
from ..core.config import COMMENT_SERVICE_URL


class CommentRateServiceClient(ServiceClient):
    def __init__(self):
        super().__init__(COMMENT_SERVICE_URL, "comment-rate-service")

    def get_reviews_by_product(self, product_id: int) -> dict:
        # Try product_id first, fallback to book_id for legacy
        data = self.get("/api/comments/by_book/", params={"book_id": product_id})
        if not data:
            return {"comments": [], "average_rating": 0, "total_reviews": 0}
        return data

    def get_reviews_for_products(self, product_ids: list[int]) -> dict[int, dict]:
        """Batch fetch ratings. Returns {product_id: {avg, count}}."""
        all_data = self.get("/api/comments/")
        comments = _extract_list(all_data)
        from collections import defaultdict
        stats: dict[int, dict] = defaultdict(lambda: {"sum": 0.0, "count": 0})
        for c in comments:
            # Support both book_id (legacy) and product_id
            pid = c.get("product_id") or c.get("book_id")
            r   = c.get("rating")
            if pid in product_ids and r is not None:
                stats[pid]["sum"]   += float(r)
                stats[pid]["count"] += 1
        return {
            pid: {
                "avg":   s["sum"] / s["count"] if s["count"] else 0.0,
                "count": s["count"],
            }
            for pid, s in stats.items()
        }

    def get_all_comments(self) -> list[dict]:
        data = self.get("/api/comments/")
        return _extract_list(data)


comment_client = CommentRateServiceClient()
