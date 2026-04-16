"""
Seed sản phẩm demo đa domain — 10 nhóm, 30+ sản phẩm, có cover_image.
Usage:
  python manage.py shell -c "from modules.catalog.seeds.products_seed import run; run()"
"""
from modules.catalog.infrastructure.models.category_model import CategoryModel
from modules.catalog.infrastructure.models.product_model import ProductModel
from modules.catalog.infrastructure.models.brand_model import BrandModel
from modules.catalog.infrastructure.models.product_type_model import ProductTypeModel

PRODUCT_TYPES = [
    {"name": "book",        "attribute_schema": {"author": "str", "pages": "int", "publisher": "str", "isbn": "str"}},
    {"name": "smartphone",  "attribute_schema": {"brand": "str", "ram": "str", "storage": "str", "os": "str"}},
    {"name": "laptop",      "attribute_schema": {"brand": "str", "cpu": "str", "ram": "str", "storage": "str"}},
    {"name": "clothing",    "attribute_schema": {"material": "str", "gender": "str", "care": "str"}},
    {"name": "shoes",       "attribute_schema": {"material": "str", "gender": "str", "sole": "str"}},
    {"name": "cosmetic",    "attribute_schema": {"skin_type": "str", "volume": "str", "ingredients": "str"}},
    {"name": "sports_gear", "attribute_schema": {"sport": "str", "material": "str", "weight": "str"}},
    {"name": "toy",         "attribute_schema": {"age_range": "str", "material": "str", "battery": "str"}},
    {"name": "food",        "attribute_schema": {"weight": "str", "expiry": "str", "origin": "str"}},
    {"name": "stationery",  "attribute_schema": {"material": "str", "color": "str", "quantity": "str"}},
    {"name": "auto_part",   "attribute_schema": {"material": "str", "size": "str", "type": "str"}},
]

BRANDS = [
    {"name": "NXB Trẻ",       "slug": "nxb-tre"},
    {"name": "NXB Kim Đồng",  "slug": "nxb-kim-dong"},
    {"name": "NXB Lao Động",  "slug": "nxb-lao-dong"},
    {"name": "Apple",         "slug": "apple"},
    {"name": "Samsung",       "slug": "samsung"},
    {"name": "Dell",          "slug": "dell"},
    {"name": "Uniqlo",        "slug": "uniqlo"},
    {"name": "Nike",          "slug": "nike"},
    {"name": "L'Oréal",       "slug": "loreal"},
    {"name": "Lego",          "slug": "lego"},
    {"name": "Vinamilk",      "slug": "vinamilk"},
    {"name": "Thiên Long",    "slug": "thien-long"},
    {"name": "Michelin",      "slug": "michelin"},
    {"name": "Castrol",       "slug": "castrol"},
    {"name": "Yonex",         "slug": "yonex"},
    {"name": "Trung Nguyên",  "slug": "trung-nguyen"},
]

# Unsplash stable image URLs (no API key needed, free to use)
PRODUCTS = [
    # ── SÁCH / BOOKS ─────────────────────────────────────────────────────────
    {
        "category_slug": "books-programming", "product_type": "book", "brand": "NXB Lao Động",
        "name": "Clean Code: Nghệ thuật viết code sạch",
        "sku": "BOOK-CC-001", "price": 189000, "stock": 50,
        "cover_image": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400&q=80",
        "description": "Hướng dẫn viết code dễ đọc, dễ bảo trì theo chuẩn Robert C. Martin.",
        "attributes": {"author": "Robert C. Martin", "pages": 431, "publisher": "NXB Lao Động", "isbn": "978-604-77-1234-1"},
    },
    {
        "category_slug": "books-programming", "product_type": "book", "brand": "NXB Lao Động",
        "name": "Design Patterns: Gang of Four",
        "sku": "BOOK-DP-002", "price": 220000, "stock": 30,
        "cover_image": "https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=400&q=80",
        "description": "23 mẫu thiết kế phần mềm kinh điển từ Gang of Four.",
        "attributes": {"author": "Erich Gamma", "pages": 395, "publisher": "NXB Lao Động", "isbn": "978-604-77-1234-2"},
    },
    {
        "category_slug": "books-science", "product_type": "book", "brand": "NXB Trẻ",
        "name": "Lược sử thời gian",
        "sku": "BOOK-SC-001", "price": 145000, "stock": 35,
        "cover_image": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=400&q=80",
        "description": "Stephen Hawking giải thích vũ trụ từ Big Bang đến lỗ đen.",
        "attributes": {"author": "Stephen Hawking", "pages": 212, "publisher": "NXB Trẻ", "isbn": "978-604-77-2345-2"},
    },
    {
        "category_slug": "books-history", "product_type": "book", "brand": "NXB Trẻ",
        "name": "Sapiens: Lược sử loài người",
        "sku": "BOOK-HI-001", "price": 199000, "stock": 60,
        "cover_image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&q=80",
        "description": "Yuval Noah Harari kể lại hành trình 70.000 năm của loài người.",
        "attributes": {"author": "Yuval Noah Harari", "pages": 559, "publisher": "NXB Thế Giới", "isbn": "978-604-77-3456-3"},
    },
    {
        "category_slug": "books-fiction", "product_type": "book", "brand": "NXB Trẻ",
        "name": "Tôi thấy hoa vàng trên cỏ xanh",
        "sku": "BOOK-FI-001", "price": 120000, "stock": 80,
        "cover_image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&q=80",
        "description": "Tiểu thuyết nổi tiếng của Nguyễn Nhật Ánh về tuổi thơ miền quê.",
        "attributes": {"author": "Nguyễn Nhật Ánh", "pages": 348, "publisher": "NXB Trẻ", "isbn": "978-604-77-4567-4"},
    },
    {
        "category_slug": "books-business", "product_type": "book", "brand": "NXB Lao Động",
        "name": "Khởi nghiệp tinh gọn",
        "sku": "BOOK-BU-001", "price": 175000, "stock": 45,
        "cover_image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80",
        "description": "Eric Ries hướng dẫn xây dựng startup theo phương pháp Lean.",
        "attributes": {"author": "Eric Ries", "pages": 336, "publisher": "NXB Lao Động", "isbn": "978-604-77-6789-6"},
    },
    {
        "category_slug": "books-self-help", "product_type": "book", "brand": "NXB Lao Động",
        "name": "Đắc nhân tâm",
        "sku": "BOOK-SH-001", "price": 88000, "stock": 100,
        "cover_image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&q=80",
        "description": "Dale Carnegie — cuốn sách kỹ năng giao tiếp bán chạy nhất mọi thời đại.",
        "attributes": {"author": "Dale Carnegie", "pages": 320, "publisher": "NXB Tổng Hợp TP.HCM", "isbn": "978-604-77-7890-7"},
    },
    {
        "category_slug": "books-children", "product_type": "book", "brand": "NXB Kim Đồng",
        "name": "Hoàng tử bé",
        "sku": "BOOK-CH-001", "price": 75000, "stock": 90,
        "cover_image": "https://images.unsplash.com/photo-1589998059171-988d887df646?w=400&q=80",
        "description": "Antoine de Saint-Exupéry — câu chuyện cổ tích dành cho mọi lứa tuổi.",
        "attributes": {"author": "Antoine de Saint-Exupéry", "pages": 112, "publisher": "NXB Kim Đồng", "isbn": "978-604-77-2468-2"},
    },
    # ── ĐIỆN TỬ / ELECTRONICS ────────────────────────────────────────────────
    {
        "category_slug": "electronics-phones", "product_type": "smartphone", "brand": "Samsung",
        "name": "Samsung Galaxy S24 Ultra",
        "sku": "ELEC-SS-S24U", "price": 31990000, "stock": 15,
        "cover_image": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&q=80",
        "description": "Flagship Samsung 2024 với bút S Pen, camera 200MP, chip Snapdragon 8 Gen 3.",
        "attributes": {"brand": "Samsung", "ram": "12GB", "storage": "256GB", "os": "Android 14"},
    },
    {
        "category_slug": "electronics-phones", "product_type": "smartphone", "brand": "Apple",
        "name": "iPhone 15 Pro Max",
        "sku": "ELEC-AP-IP15PM", "price": 34990000, "stock": 12,
        "cover_image": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&q=80",
        "description": "iPhone 15 Pro Max với chip A17 Pro, camera 48MP, khung titanium.",
        "attributes": {"brand": "Apple", "ram": "8GB", "storage": "256GB", "os": "iOS 17"},
    },
    {
        "category_slug": "electronics-laptops", "product_type": "laptop", "brand": "Dell",
        "name": "Dell XPS 15 9530",
        "sku": "ELEC-DL-XPS15", "price": 42990000, "stock": 8,
        "cover_image": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400&q=80",
        "description": "Laptop cao cấp Dell XPS 15 với màn hình OLED 3.5K, Intel Core i7-13700H.",
        "attributes": {"brand": "Dell", "cpu": "Intel Core i7-13700H", "ram": "16GB DDR5", "storage": "512GB NVMe SSD"},
    },
    # ── THỜI TRANG / FASHION ─────────────────────────────────────────────────
    {
        "category_slug": "fashion-tops", "product_type": "clothing", "brand": "Uniqlo",
        "name": "Áo phông Uniqlo UT Graphic",
        "sku": "FASH-UQ-UT001", "price": 299000, "stock": 200,
        "cover_image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80",
        "description": "Áo phông cotton 100% chất lượng cao, thiết kế graphic độc đáo.",
        "attributes": {"material": "100% Cotton", "gender": "Unisex", "care": "Giặt máy 30°C"},
    },
    {
        "category_slug": "fashion-shoes", "product_type": "shoes", "brand": "Nike",
        "name": "Nike Air Max 270",
        "sku": "FASH-NK-AM270", "price": 3290000, "stock": 50,
        "cover_image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80",
        "description": "Giày thể thao Nike Air Max 270 với đệm khí lớn nhất từ trước đến nay.",
        "attributes": {"material": "Mesh + Synthetic", "gender": "Unisex", "sole": "Air Max cushioning"},
    },
    # ── LÀM ĐẸP / BEAUTY ─────────────────────────────────────────────────────
    {
        "category_slug": "beauty", "product_type": "cosmetic", "brand": "L'Oréal",
        "name": "L'Oréal Paris Revitalift Serum",
        "sku": "BEAU-LO-RV001", "price": 450000, "stock": 80,
        "cover_image": "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&q=80",
        "description": "Serum chống lão hóa với 1.5% Pure Hyaluronic Acid, làm căng da tức thì.",
        "attributes": {"skin_type": "Mọi loại da", "volume": "30ml", "ingredients": "Hyaluronic Acid, Pro-Retinol"},
    },
    {
        "category_slug": "beauty", "product_type": "cosmetic", "brand": "L'Oréal",
        "name": "L'Oréal Paris True Match Foundation",
        "sku": "BEAU-LO-TM001", "price": 320000, "stock": 60,
        "cover_image": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&q=80",
        "description": "Kem nền True Match với 33 sắc thái, che phủ hoàn hảo suốt 24 giờ.",
        "attributes": {"skin_type": "Da thường đến da dầu", "volume": "30ml", "ingredients": "SPF 17, Vitamin E"},
    },
    # ── THỂ THAO / SPORTS ────────────────────────────────────────────────────
    {
        "category_slug": "sports", "product_type": "sports_gear", "brand": "Nike",
        "name": "Bóng đá Nike Premier League",
        "sku": "SPRT-NK-BL001", "price": 890000, "stock": 40,
        "cover_image": "https://images.unsplash.com/photo-1575361204480-aadea25e6e68?w=400&q=80",
        "description": "Bóng đá chính thức Premier League 2024, kích thước 5.",
        "attributes": {"sport": "Bóng đá", "material": "Polyurethane", "weight": "410-450g"},
    },
    {
        "category_slug": "sports", "product_type": "sports_gear", "brand": "Yonex",
        "name": "Vợt cầu lông Yonex Astrox 88D",
        "sku": "SPRT-YX-AX88D", "price": 4500000, "stock": 20,
        "cover_image": "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=400&q=80",
        "description": "Vợt cầu lông cao cấp Yonex Astrox 88D dành cho tay đánh phải.",
        "attributes": {"sport": "Cầu lông", "material": "Carbon fiber", "weight": "83g"},
    },
    # ── ĐỒ CHƠI / TOYS ───────────────────────────────────────────────────────
    {
        "category_slug": "toys", "product_type": "toy", "brand": "Lego",
        "name": "LEGO Technic Bugatti Chiron 42083",
        "sku": "TOYS-LG-TC42083", "price": 8990000, "stock": 10,
        "cover_image": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=400&q=80",
        "description": "Bộ LEGO Technic Bugatti Chiron 3599 mảnh, tỉ lệ 1:8.",
        "attributes": {"age_range": "16+", "material": "ABS Plastic", "battery": "Không cần pin"},
    },
    {
        "category_slug": "toys", "product_type": "toy", "brand": "Lego",
        "name": "LEGO City Police Station 60316",
        "sku": "TOYS-LG-CP60316", "price": 1990000, "stock": 25,
        "cover_image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80",
        "description": "Đồn cảnh sát LEGO City với 668 mảnh, phù hợp trẻ 6-12 tuổi.",
        "attributes": {"age_range": "6-12", "material": "ABS Plastic", "battery": "Không cần pin"},
    },
    # ── THỰC PHẨM / GROCERY ──────────────────────────────────────────────────
    {
        "category_slug": "grocery", "product_type": "food", "brand": "Vinamilk",
        "name": "Sữa tươi Vinamilk 100% Organic 1L",
        "sku": "GROC-VM-ORG1L", "price": 52000, "stock": 500,
        "cover_image": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80",
        "description": "Sữa tươi hữu cơ 100% từ trang trại bò sữa organic đạt chuẩn quốc tế.",
        "attributes": {"weight": "1000ml", "expiry": "21 ngày", "origin": "Việt Nam"},
    },
    {
        "category_slug": "grocery", "product_type": "food", "brand": "Trung Nguyên",
        "name": "Cà phê rang xay Trung Nguyên Legend",
        "sku": "GROC-TN-LEG250", "price": 95000, "stock": 300,
        "cover_image": "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400&q=80",
        "description": "Cà phê rang xay đặc biệt Trung Nguyên Legend, hương vị đậm đà.",
        "attributes": {"weight": "250g", "expiry": "12 tháng", "origin": "Việt Nam"},
    },
    # ── VĂN PHÒNG PHẨM / OFFICE ──────────────────────────────────────────────
    {
        "category_slug": "office-supplies", "product_type": "stationery", "brand": "Thiên Long",
        "name": "Bút bi Thiên Long TL-027 (hộp 20 cây)",
        "sku": "OFFI-TL-TL027", "price": 45000, "stock": 1000,
        "cover_image": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=400&q=80",
        "description": "Bút bi Thiên Long TL-027 mực xanh, ngòi 0.8mm, viết trơn mượt.",
        "attributes": {"material": "Nhựa ABS", "color": "Xanh", "quantity": "20 cây/hộp"},
    },
    {
        "category_slug": "office-supplies", "product_type": "stationery", "brand": "Thiên Long",
        "name": "Tập vở học sinh Thiên Long 200 trang",
        "sku": "OFFI-TL-VHS200", "price": 18000, "stock": 2000,
        "cover_image": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=400&q=80",
        "description": "Tập vở học sinh kẻ ngang 200 trang, giấy trắng 70gsm.",
        "attributes": {"material": "Giấy 70gsm", "color": "Trắng", "quantity": "1 cuốn"},
    },
    # ── Ô TÔ & XE MÁY / AUTOMOTIVE ───────────────────────────────────────────
    {
        "category_slug": "automotive", "product_type": "auto_part", "brand": "Michelin",
        "name": "Lốp xe máy Michelin Pilot Street 2",
        "sku": "AUTO-MC-PS2-90", "price": 890000, "stock": 50,
        "cover_image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80",
        "description": "Lốp xe máy Michelin Pilot Street 2, kích thước 90/80-17, bám đường tốt.",
        "attributes": {"material": "Cao su tổng hợp", "size": "90/80-17", "type": "Tubeless"},
    },
    {
        "category_slug": "automotive", "product_type": "auto_part", "brand": "Castrol",
        "name": "Dầu nhớt Castrol Power 1 Racing 10W-40",
        "sku": "AUTO-CS-PR10W40", "price": 185000, "stock": 200,
        "cover_image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&q=80",
        "description": "Dầu nhớt tổng hợp cao cấp Castrol Power 1 Racing cho xe máy thể thao.",
        "attributes": {"material": "Dầu tổng hợp", "volume": "1L", "viscosity": "10W-40"},
    },
    # ── GIA DỤNG / HOME APPLIANCES ────────────────────────────────────────────
    {
        "category_slug": "home-appliances", "product_type": "stationery", "brand": "Samsung",
        "name": "Nồi cơm điện Samsung 1.8L",
        "sku": "HOME-SS-NC18", "price": 1290000, "stock": 35,
        "cover_image": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400&q=80",
        "description": "Nồi cơm điện Samsung 1.8L, nấu cơm ngon, giữ ấm 24h.",
        "attributes": {"material": "Inox + Nhựa ABS", "capacity": "1.8L", "power": "700W"},
    },
    {
        "category_slug": "home-appliances", "product_type": "stationery", "brand": "Samsung",
        "name": "Máy lọc không khí Samsung AX40",
        "sku": "HOME-SS-AX40", "price": 4990000, "stock": 18,
        "cover_image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80",
        "description": "Máy lọc không khí Samsung AX40, lọc bụi mịn PM2.5, diện tích 40m².",
        "attributes": {"material": "Nhựa ABS", "coverage": "40m²", "filter": "HEPA H13"},
    },
    # ── BỔ SUNG DỮ LIỆU ĐA DẠNG CHO GỢI Ý AI ────────────────────────────────
    {
        "category_slug": "books-psychology", "product_type": "book", "brand": "NXB Trẻ",
        "name": "Tư duy nhanh và chậm",
        "sku": "BOOK-PSY-001", "price": 210000, "stock": 42,
        "cover_image": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=400&q=80",
        "description": "Daniel Kahneman phân tích hai hệ thống tư duy ảnh hưởng tới quyết định hàng ngày.",
        "attributes": {"author": "Daniel Kahneman", "pages": 612, "publisher": "NXB Trẻ", "isbn": "978-604-77-9876-5"},
    },
    {
        "category_slug": "electronics-audio", "product_type": "smartphone", "brand": "Apple",
        "name": "AirPods Pro 2 USB-C",
        "sku": "ELEC-AP-APP2", "price": 5890000, "stock": 30,
        "cover_image": "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=400&q=80",
        "description": "Tai nghe chống ồn chủ động, âm thanh không gian cá nhân hóa.",
        "attributes": {"brand": "Apple", "ram": "N/A", "storage": "N/A", "os": "iOS/Android"},
    },
    {
        "category_slug": "fashion-bags", "product_type": "clothing", "brand": "Uniqlo",
        "name": "Túi đeo chéo Uniqlo Round Mini",
        "sku": "FASH-UQ-BAG01", "price": 590000, "stock": 120,
        "cover_image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&q=80",
        "description": "Túi mini gọn nhẹ chống nước nhẹ, phù hợp đi làm và du lịch.",
        "attributes": {"material": "Nylon", "gender": "Unisex", "care": "Lau ẩm"},
    },
    {
        "category_slug": "beauty", "product_type": "cosmetic", "brand": "L'Oréal",
        "name": "L'Oréal UV Defender SPF50+",
        "sku": "BEAU-LO-UV50", "price": 285000, "stock": 95,
        "cover_image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400&q=80",
        "description": "Kem chống nắng bảo vệ da khỏi tia UVA/UVB và bụi mịn đô thị.",
        "attributes": {"skin_type": "Mọi loại da", "volume": "50ml", "ingredients": "Niacinamide, UV Filter"},
    },
    {
        "category_slug": "sports", "product_type": "sports_gear", "brand": "Nike",
        "name": "Thảm tập yoga Nike Essential 6mm",
        "sku": "SPRT-NK-YOGA6", "price": 690000, "stock": 70,
        "cover_image": "https://images.unsplash.com/photo-1599447421416-3414500d18a5?w=400&q=80",
        "description": "Thảm tập êm, chống trượt, phù hợp yoga và pilates.",
        "attributes": {"sport": "Yoga", "material": "TPE", "weight": "900g"},
    },
    {
        "category_slug": "toys", "product_type": "toy", "brand": "Lego",
        "name": "LEGO Creator 3-in-1 Pirate Ship",
        "sku": "TOYS-LG-CR31109", "price": 3290000, "stock": 22,
        "cover_image": "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=400&q=80",
        "description": "Bộ LEGO sáng tạo 3 mô hình trong 1: tàu cướp biển, quán trọ, đảo đầu lâu.",
        "attributes": {"age_range": "9+", "material": "ABS Plastic", "battery": "Không cần pin"},
    },
    {
        "category_slug": "grocery", "product_type": "food", "brand": "Vinamilk",
        "name": "Sữa chua uống Probi Vinamilk lốc 4",
        "sku": "GROC-VM-PROBI4", "price": 32000, "stock": 420,
        "cover_image": "https://images.unsplash.com/photo-1559563458-527698bf5295?w=400&q=80",
        "description": "Sữa chua uống men sống hỗ trợ tiêu hóa, vị thanh mát.",
        "attributes": {"weight": "4 x 130ml", "expiry": "30 ngày", "origin": "Việt Nam"},
    },
    {
        "category_slug": "office-supplies", "product_type": "stationery", "brand": "Thiên Long",
        "name": "Bút dạ quang Thiên Long HL-03 (vỉ 5 màu)",
        "sku": "OFFI-TL-HL03", "price": 28000, "stock": 850,
        "cover_image": "https://images.unsplash.com/photo-1456735190827-d1262f71b8a3?w=400&q=80",
        "description": "Bút dạ quang nhiều màu, mực bền sáng, thích hợp học tập và làm việc.",
        "attributes": {"material": "Nhựa", "color": "5 màu", "quantity": "5 cây/vỉ"},
    },
    {
        "category_slug": "automotive", "product_type": "auto_part", "brand": "Michelin",
        "name": "Bơm lốp mini Michelin 12V",
        "sku": "AUTO-MC-PUMP12", "price": 1190000, "stock": 40,
        "cover_image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=400&q=80",
        "description": "Bơm lốp điện mini dùng cổng 12V, có đồng hồ đo áp suất.",
        "attributes": {"material": "Hợp kim + Nhựa", "size": "Compact", "type": "12V Electric"},
    },
    {
        "category_slug": "home-appliances", "product_type": "stationery", "brand": "Samsung",
        "name": "Ấm siêu tốc Samsung 1.7L",
        "sku": "HOME-SS-KET17", "price": 790000, "stock": 64,
        "cover_image": "https://images.unsplash.com/photo-1595475884562-073c30d45670?w=400&q=80",
        "description": "Ấm đun nước siêu tốc thân inox, tự ngắt khi sôi, an toàn cho gia đình.",
        "attributes": {"material": "Inox 304", "capacity": "1.7L", "power": "1800W"},
    },
]


def run():
    # Seed product types
    type_map: dict = {}
    for pt in PRODUCT_TYPES:
        obj, _ = ProductTypeModel.objects.get_or_create(
            name=pt["name"], defaults={"attribute_schema": pt["attribute_schema"]}
        )
        type_map[pt["name"]] = obj

    # Seed brands
    brand_map: dict = {}
    for b in BRANDS:
        obj, _ = BrandModel.objects.get_or_create(slug=b["slug"], defaults={"name": b["name"]})
        brand_map[b["name"]] = obj

    cat_map = {c.slug: c for c in CategoryModel.objects.all()}
    created = 0
    for p in PRODUCTS:
        cat = cat_map.get(p["category_slug"])
        if not cat:
            # Try partial slug match (e.g. old slug 'lap-trinh' vs new 'books-programming')
            print(f"  WARNING: category '{p['category_slug']}' not found, skipping '{p['name']}'")
            continue
        try:
            _, is_new = ProductModel.objects.update_or_create(
                sku=p.get("sku", p["name"][:32]),
                defaults={
                    "name":         p["name"],
                    "category":     cat,
                    "brand":        brand_map.get(p.get("brand", "")),
                    "product_type": type_map.get(p.get("product_type", "")),
                    "price":        p["price"],
                    "stock":        p["stock"],
                    "description":  p["description"],
                    "cover_image":  p.get("cover_image", ""),
                    "attributes":   p["attributes"],
                },
            )
            if is_new:
                created += 1
        except Exception as e:
            print(f"  WARNING: could not seed product '{p['name']}': {e}")
    print(f"Products seeded: {created} new, {len(PRODUCTS) - created} already existed")
    return created
