"""
Seed danh mục sản phẩm đa domain — tối thiểu 10 nhóm cấp cao.
Category là dữ liệu trong DB — không phải enum cứng.

Usage:
  python manage.py shell -c "from modules.catalog.seeds.categories_seed import run; run()"
"""
from modules.catalog.infrastructure.models.category_model import CategoryModel

# ── 10 nhóm sản phẩm cấp cao (top-level) ─────────────────────────────────────
TOP_LEVEL = [
    {"name": "Sách",              "slug": "books",            "icon": "📚", "description": "Sách các thể loại"},
    {"name": "Điện tử",           "slug": "electronics",      "icon": "📱", "description": "Điện thoại, laptop, thiết bị điện tử"},
    {"name": "Thời trang",        "slug": "fashion",          "icon": "👗", "description": "Quần áo, giày dép, phụ kiện"},
    {"name": "Gia dụng",          "slug": "home-appliances",  "icon": "🏠", "description": "Đồ gia dụng, nội thất"},
    {"name": "Làm đẹp",           "slug": "beauty",           "icon": "💄", "description": "Mỹ phẩm, chăm sóc da, nước hoa"},
    {"name": "Thể thao",          "slug": "sports",           "icon": "⚽", "description": "Dụng cụ thể thao, fitness"},
    {"name": "Đồ chơi",           "slug": "toys",             "icon": "🧸", "description": "Đồ chơi trẻ em, game"},
    {"name": "Thực phẩm",         "slug": "grocery",          "icon": "🛒", "description": "Thực phẩm, đồ uống, thực phẩm chức năng"},
    {"name": "Văn phòng phẩm",    "slug": "office-supplies",  "icon": "🖊️", "description": "Văn phòng phẩm, thiết bị văn phòng"},
    {"name": "Ô tô & Xe máy",     "slug": "automotive",       "icon": "🚗", "description": "Phụ kiện ô tô, xe máy"},
]

# ── Danh mục con cho Sách ─────────────────────────────────────────────────────
BOOK_SUBCATEGORIES = [
    {"name": "Lập trình",    "slug": "books-programming",  "icon": "💻", "parent_slug": "books", "description": "Sách lập trình, công nghệ"},
    {"name": "Khoa học",     "slug": "books-science",      "icon": "🔬", "parent_slug": "books", "description": "Khoa học tự nhiên"},
    {"name": "Lịch sử",      "slug": "books-history",      "icon": "📜", "parent_slug": "books", "description": "Lịch sử Việt Nam và thế giới"},
    {"name": "Tiểu thuyết",  "slug": "books-fiction",      "icon": "📖", "parent_slug": "books", "description": "Tiểu thuyết trong và ngoài nước"},
    {"name": "Toán học",     "slug": "books-math",         "icon": "📐", "parent_slug": "books", "description": "Toán học, thống kê"},
    {"name": "Kinh doanh",   "slug": "books-business",     "icon": "💼", "parent_slug": "books", "description": "Kinh doanh, quản trị"},
    {"name": "Kỹ năng sống", "slug": "books-self-help",    "icon": "🌱", "parent_slug": "books", "description": "Phát triển bản thân"},
    {"name": "Văn học",      "slug": "books-literature",   "icon": "✍️", "parent_slug": "books", "description": "Văn học Việt Nam"},
    {"name": "Triết học",    "slug": "books-philosophy",   "icon": "🧠", "parent_slug": "books", "description": "Triết học Đông Tây"},
    {"name": "Tâm lý",       "slug": "books-psychology",   "icon": "💭", "parent_slug": "books", "description": "Tâm lý học"},
    {"name": "Nghệ thuật",   "slug": "books-art",          "icon": "🎨", "parent_slug": "books", "description": "Nghệ thuật, âm nhạc"},
    {"name": "Thiếu nhi",    "slug": "books-children",     "icon": "🧒", "parent_slug": "books", "description": "Sách thiếu nhi"},
]

# ── Danh mục con cho Điện tử ──────────────────────────────────────────────────
ELECTRONICS_SUBCATEGORIES = [
    {"name": "Điện thoại",  "slug": "electronics-phones",   "icon": "📱", "parent_slug": "electronics", "description": "Điện thoại thông minh"},
    {"name": "Laptop",      "slug": "electronics-laptops",  "icon": "💻", "parent_slug": "electronics", "description": "Máy tính xách tay"},
    {"name": "Tai nghe",    "slug": "electronics-audio",    "icon": "🎧", "parent_slug": "electronics", "description": "Tai nghe, loa"},
    {"name": "Máy ảnh",     "slug": "electronics-cameras",  "icon": "📷", "parent_slug": "electronics", "description": "Máy ảnh, máy quay"},
]

# ── Danh mục con cho Thời trang ───────────────────────────────────────────────
FASHION_SUBCATEGORIES = [
    {"name": "Áo",      "slug": "fashion-tops",    "icon": "👕", "parent_slug": "fashion", "description": "Áo các loại"},
    {"name": "Quần",    "slug": "fashion-bottoms", "icon": "👖", "parent_slug": "fashion", "description": "Quần các loại"},
    {"name": "Giày dép","slug": "fashion-shoes",   "icon": "👟", "parent_slug": "fashion", "description": "Giày dép"},
    {"name": "Túi xách","slug": "fashion-bags",    "icon": "👜", "parent_slug": "fashion", "description": "Túi xách, ba lô"},
]

# ── Danh mục con cho các domain còn lại ───────────────────────────────────────
HOME_SUBCATEGORIES = [
    {"name": "Thiết bị bếp", "slug": "home-appliances-kitchen", "icon": "🍳", "parent_slug": "home-appliances", "description": "Nồi, bếp, đồ gia dụng nhà bếp"},
    {"name": "Điện gia dụng", "slug": "home-appliances-electrical", "icon": "🔌", "parent_slug": "home-appliances", "description": "Ấm siêu tốc, máy lọc, máy hút bụi"},
]

BEAUTY_SUBCATEGORIES = [
    {"name": "Son môi", "slug": "beauty-lipstick", "icon": "💋", "parent_slug": "beauty", "description": "Son môi, son dưỡng"},
    {"name": "Kem nền", "slug": "beauty-foundation", "icon": "🧴", "parent_slug": "beauty", "description": "Kem nền, cushion"},
    {"name": "Chăm sóc da", "slug": "beauty-skincare", "icon": "✨", "parent_slug": "beauty", "description": "Sữa rửa mặt, serum, kem dưỡng"},
]

SPORTS_SUBCATEGORIES = [
    {"name": "Fitness", "slug": "sports-fitness", "icon": "🏋️", "parent_slug": "sports", "description": "Dụng cụ tập gym, yoga"},
    {"name": "Bóng đá", "slug": "sports-football", "icon": "⚽", "parent_slug": "sports", "description": "Bóng, giày, phụ kiện bóng đá"},
    {"name": "Cầu lông", "slug": "sports-badminton", "icon": "🏸", "parent_slug": "sports", "description": "Vợt, cầu, phụ kiện cầu lông"},
]

TOYS_SUBCATEGORIES = [
    {"name": "LEGO", "slug": "toys-lego", "icon": "🧱", "parent_slug": "toys", "description": "Đồ chơi lắp ráp LEGO"},
    {"name": "Đồ chơi sáng tạo", "slug": "toys-creative", "icon": "🎨", "parent_slug": "toys", "description": "Đồ chơi phát triển tư duy"},
]

GROCERY_SUBCATEGORIES = [
    {"name": "Sữa & dinh dưỡng", "slug": "grocery-dairy", "icon": "🥛", "parent_slug": "grocery", "description": "Sữa, sữa chua, dinh dưỡng"},
    {"name": "Cà phê & trà", "slug": "grocery-coffee-tea", "icon": "☕", "parent_slug": "grocery", "description": "Cà phê, trà, đồ uống"},
]

OFFICE_SUBCATEGORIES = [
    {"name": "Bút viết", "slug": "office-supplies-writing", "icon": "🖊️", "parent_slug": "office-supplies", "description": "Bút bi, bút dạ, bút chì"},
    {"name": "Sổ giấy", "slug": "office-supplies-paper", "icon": "📒", "parent_slug": "office-supplies", "description": "Tập, sổ, giấy in"},
]

AUTOMOTIVE_SUBCATEGORIES = [
    {"name": "Lốp xe", "slug": "automotive-tires", "icon": "🛞", "parent_slug": "automotive", "description": "Lốp, săm, phụ kiện lốp"},
    {"name": "Dầu nhớt", "slug": "automotive-oil", "icon": "🛢️", "parent_slug": "automotive", "description": "Dầu nhớt, dung dịch bảo dưỡng"},
]


def run():
    created = 0
    slug_to_obj: dict = {}

    # 1. Top-level categories
    for cat in TOP_LEVEL:
        try:
            obj, is_new = CategoryModel.objects.update_or_create(
                slug=cat["slug"],
                defaults={k: v for k, v in cat.items() if k != "parent_slug"},
            )
            slug_to_obj[cat["slug"]] = obj
            if is_new:
                created += 1
        except Exception as e:
            # Fallback: try to get by name if slug conflict
            try:
                obj = CategoryModel.objects.get(name=cat["name"])
                slug_to_obj[cat["slug"]] = obj
                print(f"  INFO: reused existing category '{cat['name']}' (slug mismatch)")
            except CategoryModel.DoesNotExist:
                print(f"  WARNING: could not seed category '{cat['name']}': {e}")

    # 2. Sub-categories
    all_subs = (
        BOOK_SUBCATEGORIES
        + ELECTRONICS_SUBCATEGORIES
        + FASHION_SUBCATEGORIES
        + HOME_SUBCATEGORIES
        + BEAUTY_SUBCATEGORIES
        + SPORTS_SUBCATEGORIES
        + TOYS_SUBCATEGORIES
        + GROCERY_SUBCATEGORIES
        + OFFICE_SUBCATEGORIES
        + AUTOMOTIVE_SUBCATEGORIES
    )
    for cat in all_subs:
        parent = slug_to_obj.get(cat.get("parent_slug"))
        data = {k: v for k, v in cat.items() if k != "parent_slug"}
        data["parent"] = parent
        try:
            obj, is_new = CategoryModel.objects.update_or_create(
                slug=cat["slug"], defaults=data
            )
            slug_to_obj[cat["slug"]] = obj
            if is_new:
                created += 1
        except Exception as e:
            try:
                obj = CategoryModel.objects.get(name=cat["name"])
                slug_to_obj[cat["slug"]] = obj
            except CategoryModel.DoesNotExist:
                print(f"  WARNING: could not seed sub-category '{cat['name']}': {e}")

    total = len(TOP_LEVEL) + len(all_subs)
    print(f"Categories seeded: {created} new, {total - created} already existed")
    return created
