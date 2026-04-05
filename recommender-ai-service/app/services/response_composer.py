"""
ResponseComposer
─────────────────
Composes final chatbot responses per intent.
Each handler receives structured data and returns a human-readable answer.
All text is generated from data — no hardcoded product lists.
"""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _fmt_price(p: float) -> str:
    return f"{int(p):,}đ"


def _fmt_book(b: dict) -> str:
    title  = b.get("title", "N/A")
    author = b.get("author", "")
    price  = float(b.get("price", 0))
    cat    = b.get("category", "")
    rating = b.get("avg_rating", 0)
    reason = b.get("reason", "")
    line   = f"📚 **{title}**"
    if author:
        line += f" — {author}"
    if cat:
        line += f" [{cat}]"
    line += f"\n   💰 {_fmt_price(price)}"
    if rating:
        line += f" | ⭐ {rating:.1f}"
    if reason:
        line += f"\n   💡 {reason}"
    return line


def compose(
    intent: str,
    entities: dict[str, Any],
    data: dict[str, Any],
    customer_id: int | None = None,
) -> str:
    """
    Route to the correct composer based on intent.
    data contains pre-fetched structured data from services.
    """
    composers = {
        "faq":              _compose_faq,
        "return_policy":    _compose_return_policy,
        "payment_support":  _compose_payment_support,
        "shipping_support": _compose_shipping_support,
        "product_advice":   _compose_product_advice,
        "order_support":    _compose_order_support,
        "general_search":   _compose_general_search,
        "fallback":         _compose_fallback,
    }
    fn = composers.get(intent, _compose_fallback)
    return fn(entities, data, customer_id)


def _compose_faq(entities: dict, data: dict, customer_id: int | None) -> str:
    sources = data.get("sources", [])
    if not sources:
        return (
            "Tôi chưa tìm thấy thông tin phù hợp trong cơ sở dữ liệu. "
            "Vui lòng liên hệ support@moonbooks.vn để được hỗ trợ! 📧"
        )
    top = sources[0]
    answer = f"**{top['title']}**\n\n{top['content']}"
    if len(sources) > 1:
        answer += f"\n\n---\n💡 Xem thêm: **{sources[1]['title']}**"
    return answer


def _compose_return_policy(entities: dict, data: dict, customer_id: int | None) -> str:
    sources = data.get("sources", [])
    if sources:
        top = sources[0]
        return f"**Chính sách đổi trả MoonBooks**\n\n{top['content']}"
    return (
        "**Chính sách đổi trả MoonBooks**\n\n"
        "MoonBooks chấp nhận đổi trả trong vòng 7 ngày kể từ ngày nhận hàng.\n"
        "Điều kiện: sách còn nguyên vẹn, chưa qua sử dụng.\n"
        "Liên hệ: support@moonbooks.vn hoặc hotline 1800-xxxx."
    )


def _compose_payment_support(entities: dict, data: dict, customer_id: int | None) -> str:
    sources = data.get("sources", [])
    if sources:
        top = sources[0]
        return f"**Thanh toán tại MoonBooks**\n\n{top['content']}"
    return (
        "**Phương thức thanh toán MoonBooks**\n\n"
        "• 💳 Thẻ tín dụng/ghi nợ (Visa, Mastercard)\n"
        "• 💵 COD — Thanh toán khi nhận hàng\n"
        "• 🏦 Chuyển khoản ngân hàng\n"
        "Tất cả giao dịch được mã hóa SSL."
    )


def _compose_shipping_support(entities: dict, data: dict, customer_id: int | None) -> str:
    sources = data.get("sources", [])
    if sources:
        top = sources[0]
        return f"**Giao hàng tại MoonBooks**\n\n{top['content']}"
    return (
        "**Thông tin giao hàng MoonBooks**\n\n"
        "• 📦 Giao hàng tiêu chuẩn: 3–5 ngày làm việc\n"
        "• ⚡ Giao hàng nhanh: 1–2 ngày (phụ phí)\n"
        "• 🎁 Miễn phí ship cho đơn từ 300.000đ\n"
        "Theo dõi đơn hàng trong mục 'Đơn hàng của tôi'."
    )


def _compose_product_advice(entities: dict, data: dict, customer_id: int | None) -> str:
    recs = data.get("recommendations", [])
    budget_max = entities.get("budget_max")
    category   = entities.get("category")
    keywords   = entities.get("product_keywords", [])

    if not recs:
        context = data.get("rag_context", "")
        if context:
            return f"Dựa trên thông tin tôi có:\n\n{context}\n\nBạn muốn tìm hiểu thêm về sách nào?"
        return (
            "Tôi chưa tìm thấy sách phù hợp với yêu cầu của bạn. "
            "Hãy thử mô tả rõ hơn về thể loại hoặc chủ đề bạn quan tâm! 📚"
        )

    header_parts = ["💡 **Gợi ý sách dành cho bạn**"]
    if category:
        header_parts.append(f"thể loại: {category}")
    if budget_max:
        header_parts.append(f"dưới {_fmt_price(budget_max)}")
    if keywords:
        header_parts.append(f"từ khóa: {', '.join(keywords[:3])}")

    header = " | ".join(header_parts)
    lines  = [header, ""]
    for b in recs[:5]:
        lines.append(_fmt_book(b))
        lines.append("")

    lines.append("Bạn muốn biết thêm về cuốn nào? 😊")
    return "\n".join(lines)


def _compose_order_support(entities: dict, data: dict, customer_id: int | None) -> str:
    order_data = data.get("order_data", {})

    if not order_data.get("found"):
        return order_data.get("message", "Không tìm thấy thông tin đơn hàng.")

    # Single order detail
    if "order_id" in order_data:
        o = order_data
        lines = [
            f"📦 **Đơn hàng #{o['order_id']}**",
            f"Trạng thái: {o['status']}",
            f"Tổng tiền: {_fmt_price(o['total'])}",
            f"Ngày đặt: {o['created']}",
        ]
        if o.get("address"):
            lines.append(f"Địa chỉ: {o['address']}")
        ship = o.get("shipping", {})
        if ship.get("status"):
            lines.append(f"\n🚚 **Vận chuyển**: {ship['status']}")
            if ship.get("tracking"):
                lines.append(f"Mã tracking: {ship['tracking']}")
            if ship.get("eta"):
                lines.append(f"Dự kiến giao: {ship['eta']}")
        pay = o.get("payment", {})
        if pay.get("status"):
            lines.append(f"\n💳 **Thanh toán**: {pay['status']}")
            if pay.get("method"):
                lines.append(f"Phương thức: {pay['method']}")
        return "\n".join(lines)

    # List of orders
    orders = order_data.get("orders", [])
    lines  = [f"📦 **{order_data['count']} đơn hàng gần đây của bạn:**", ""]
    for o in orders:
        lines.append(
            f"• Đơn #{o['order_id']} | {o['status']} | "
            f"{_fmt_price(o['total'])} | {o['items']} sản phẩm | {o['created']}"
        )
    lines.append("\nNhập mã đơn hàng để xem chi tiết (ví dụ: 'đơn hàng #123')")
    return "\n".join(lines)


def _compose_general_search(entities: dict, data: dict, customer_id: int | None) -> str:
    recs    = data.get("recommendations", [])
    sources = data.get("sources", [])
    keywords = entities.get("product_keywords", [])

    if recs:
        kw_str = ", ".join(keywords[:3]) if keywords else "từ khóa của bạn"
        lines  = [f"🔍 **Kết quả tìm kiếm: '{kw_str}'**", ""]
        for b in recs[:5]:
            lines.append(_fmt_book(b))
            lines.append("")
        return "\n".join(lines)

    if sources:
        return f"🔍 **Thông tin tìm thấy:**\n\n{sources[0]['content']}"

    kw_str = ", ".join(keywords[:3]) if keywords else "từ khóa"
    return (
        f"Không tìm thấy kết quả cho '{kw_str}'. "
        "Thử tìm với từ khóa khác hoặc hỏi tôi về thể loại sách bạn quan tâm! 🔍"
    )


def _compose_fallback(entities: dict, data: dict, customer_id: int | None) -> str:
    sources = data.get("sources", [])
    if sources:
        return (
            f"Tôi tìm thấy thông tin có thể liên quan:\n\n"
            f"**{sources[0]['title']}**\n{sources[0]['content']}\n\n"
            "Bạn có muốn hỏi thêm điều gì không? 😊"
        )
    return (
        "Xin lỗi, tôi chưa hiểu rõ câu hỏi của bạn. 🤔\n\n"
        "Tôi có thể giúp bạn:\n"
        "• 💡 **Gợi ý sách** — 'Gợi ý sách lập trình cho tôi'\n"
        "• 🔍 **Tìm sách** — 'Tìm sách của tác giả X'\n"
        "• 📦 **Đơn hàng** — 'Đơn hàng của tôi'\n"
        "• 🔄 **Đổi trả** — 'Chính sách đổi trả'\n"
        "• 💳 **Thanh toán** — 'Phương thức thanh toán'"
    )
