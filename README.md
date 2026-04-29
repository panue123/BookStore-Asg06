# E-Commerce Microservices + AI Service

Kiến trúc **Microservices + DDD + AI Service** cho môn Kiến trúc và Thiết kế Phần mềm.  
**Status: Final Submission Ready ✅**

---

## Quick Start

```bash
# 1. Build và start toàn bộ hệ thống
docker-compose up --build -d

# 2. Chờ services khởi động (~2-3 phút)
#    Verify AI service ready trước khi seed:
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8011/health'); print('AI ready')"

# 3. Seed behavior data
python recommender-ai-service/scripts/seed_behavior.py

# 4. Build AI-service artifacts for the assignment
python recommender-ai-service/scripts/generate_data_user500.py
cd recommender-ai-service
python -m app.ml.evaluate_models
python -m app.ml.select_best_model

# 5. Verify 28/28 passed
python smoke_test.py

# 6. Demo
bash demo_curl.sh
```

**Truy cập:**
- Frontend: http://localhost:8000
- AI API (Django): http://localhost:8011/health
- Product API: http://localhost:8013/api/products/
- User API: http://localhost:8001/api/users/
- Notification API: http://localhost:8014/api/notifications/
- Neo4j Browser: http://localhost:7474 (neo4j/neo4j_password)
- RabbitMQ UI: http://localhost:15672 (guest/guest)

---

## Kiến trúc tổng quan

```
api-gateway (8000)
├── auth-service (8012)           — JWT authentication
├── user-service (8001)           — Unified users + role + RBAC (manager/staff/customer)
├── product-service (8013)        — Product catalog/category/stock (replaces book+catalog)
├── cart-service (8003)           — Shopping cart → calls product-service
├── order-service (8004)          — Order management + Saga
├── pay-service (8005)            — Payment processing
├── ship-service (8006)           — Shipping & tracking
├── comment-rate-service (8008)   — Reviews & ratings
├── notification-service (8014)   — Async notifications (email/SMS queue)
└── recommender-ai-service (8011) — Django AI service: RNN + LSTM + biLSTM + Neo4j Graph + RAG + Chatbot

Infrastructure:
  db-mysql      — auth, user, order, pay, ship, notification
  db-postgres   — product, cart, comment, recommender
  rabbitmq      — async events (order saga)
  neo4j         — knowledge graph (hybrid recommendation)
```

Legacy services `book-service`, `catalog-service`, `customer-service`, `staff-service`, `manager-service` đã bị loại khỏi runtime chính.

---

## Hybrid Recommendation Score

```
final_score = w1 * lstm_score + w2 * graph_score + w3 * content_score + w4 * rating_score
            = 0.40 * lstm   + 0.25 * graph      + 0.25 * content     + 0.10 * rating
```

- **LSTM (0.40):** PyTorch sequence model, input = chuỗi sự kiện view/search/cart/purchase/rate
- **Graph (0.25):** Neo4j collaborative filtering — customers who bought X also bought Y
- **Content (0.25):** Category/brand affinity từ interaction history
- **Rating (0.10):** Community rating popularity

---

## Cách start hệ thống

```bash
# 1. Build và start toàn bộ
docker-compose up --build

# 2. Chờ tất cả services healthy (~2-3 phút)
docker-compose ps

# 3. Truy cập
# Frontend:       http://localhost:8000
# AI health:       http://localhost:8011/health
# Product API:    http://localhost:8013/api/products/
# User API:       http://localhost:8001/api/users/
# Notification:   http://localhost:8014/api/notifications/
# Neo4j Browser:  http://localhost:7474 (neo4j/neo4j_password)
# RabbitMQ UI:    http://localhost:15672 (guest/guest)
```

---

## Cách seed dữ liệu

Product-service tự seed khi khởi động (xem `entrypoint.sh`). Để seed thủ công:

```bash
# Seed categories (10 top-level + subcategories)
docker exec $(docker ps -qf name=product-service) python manage.py shell -c \
  "from modules.catalog.seeds.categories_seed import run; run()"

# Seed products (25+ sản phẩm đa domain)
docker exec $(docker ps -qf name=product-service) python manage.py shell -c \
  "from modules.catalog.seeds.products_seed import run; run()"
```

---

## Cách train LSTM model

```bash
# Trong container (recommended)
docker exec $(docker ps -qf name=recommender-ai-service) python scripts/train_model.py

# Local (cần torch)
cd recommender-ai-service
pip install torch numpy
python scripts/train_model.py

# Output:
#   artifacts/lstm_behavior_model.pt   ← LSTM primary
#   artifacts/behavior_model.pt        ← MLP fallback
#   artifacts/model_comparison.json    ← comparison results
```

Model được tự động train khi container khởi động nếu chưa có checkpoint.

---

## Cách reindex Knowledge Base

```bash
# Via API (recommended)
curl -X POST http://localhost:8011/api/v1/kb/reindex

# Via script trong container
docker exec $(docker ps -qf name=recommender-ai-service) python scripts/reindex_kb.py

# Check status
curl http://localhost:8011/api/v1/kb/status
```

KB được build từ: seed_kb.json (FAQ/policy) + product-service (đa domain) + comment-rate-service (reviews).

---

## Cách verify hệ thống (smoke test)

```bash
# Chạy smoke test đầy đủ
python smoke_test.py

# Custom URLs
python smoke_test.py --gateway http://localhost:8000 --ai http://localhost:8011 --product http://localhost:8013
```

---

## API chính

### Product Service
```
GET  /api/products/                     — list (paginated)
POST /api/products/                     — create
GET  /api/products/{id}/                — detail
PUT  /api/products/{id}/                — update
GET  /api/products/filter/              — filter (min_price, max_price, category_slug, in_stock)
GET  /api/products/search/?q=laptop     — search
GET  /api/categories/                   — list categories (tree)
GET  /api/health/                       — health check
```

### AI Service
```
POST /api/v1/chat                       — chatbot (intent → response)
GET  /api/v1/recommend/{customer_id}    — personalized recommendations
GET  /api/v1/recommend/similar/{id}     — similar products
GET  /api/v1/analyze-customer/{id}      — behavior profile (LSTM/MLP/rule-based)
POST /api/v1/track                      — track interaction (→ DB + Neo4j)
POST /api/v1/kb/reindex                 — rebuild KB + FAISS index
GET  /api/v1/kb/status                  — KB stats
GET  /health                            — service health + hybrid weights
```

### API Gateway (proxy)
```
/api/users/*             → user-service
/api/customers/*         → user-service (compat)
/api/staff/*             → user-service (compat)
/api/manager/*           → user-service (compat)
/api/products/*          → product-service
/api/categories/*        → product-service
/api/v1/*                → recommender-ai-service
/api/ai/*                → recommender-ai-service
/api/auth/*              → auth-service (public)
/api/notifications/*     → notification-service
/api/orders/*            → order-service (JWT required)
/api/carts/*             → cart-service (JWT required)
/api/payments/*          → pay-service (JWT required)
/health/                 → gateway health aggregation
```

---

## Test chat API

```bash
# Tư vấn sản phẩm
curl -X POST http://localhost:8011/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Gợi ý laptop dưới 20 triệu", "customer_id": 1}'

# Hỏi chính sách
curl -X POST http://localhost:8011/api/v1/chat \
  -d '{"message": "Chính sách đổi trả như thế nào?"}'

# Tìm sản phẩm điện tử
curl -X POST http://localhost:8011/api/v1/chat \
  -d '{"message": "Tôi muốn mua điện thoại Samsung"}'

# Quick action
curl -X POST http://localhost:8011/api/v1/chat \
  -d '{"message": "", "quick_action": "recommend", "customer_id": 1}'

# Qua API Gateway
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Sản phẩm thể thao nào đang hot?"}'
```

---

## Migration kiến trúc

1. Runtime chính chỉ dùng: user-service, product-service, cart/order/pay/ship/comment, notification-service, recommender-ai-service
2. `book-service` + `catalog-service` được thay bởi `product-service`
3. Dữ liệu sách cũ migrate sang `product_type="book"`
4. `customer/staff/manager` hợp nhất vào `user-service` với RBAC role claims
5. AI service chạy Django-only; gateway route `/api/v1/*` vào recommender-ai-service

---

## 10 Product Domains

| Slug | Tên | Subcategories |
|------|-----|---------------|
| books | Sách | programming, science, history, fiction, math, business, self-help, literature, philosophy, psychology, art, children |
| electronics | Điện tử | phones, laptops, audio, cameras |
| fashion | Thời trang | tops, bottoms, shoes, bags |
| home-appliances | Gia dụng | — |
| beauty | Làm đẹp | — |
| sports | Thể thao | — |
| toys | Đồ chơi | — |
| grocery | Thực phẩm | — |
| office-supplies | Văn phòng phẩm | — |
| automotive | Ô tô & Xe máy | — |
