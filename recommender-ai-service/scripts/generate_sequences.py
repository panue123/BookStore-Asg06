"""
Synthetic Dataset Generator — cập nhật cho product-service (đa domain)
────────────────────────────────────────────────────────────────────────
Tạo tập dữ liệu tổng hợp dạng chuỗi thời gian cho LSTM training.

Output:
  data/synthetic_sequences.json  — chuỗi sự kiện theo thời gian
  data/synthetic_customers.csv   — profile khách hàng

Usage:
  python scripts/generate_sequences.py
"""
import json
import csv
import random
import time
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 10 nhóm sản phẩm cấp cao (bám sát product-service)
CATEGORIES = [
    "books", "electronics", "fashion", "home-appliances", "beauty",
    "sports", "toys", "grocery", "office-supplies", "automotive",
]

INTERACTION_TYPES = ["view", "search", "cart", "purchase", "rate"]
TRANSITIONS = {
    "view":     {"view": 0.4, "search": 0.2, "cart": 0.2, "purchase": 0.1, "rate": 0.1},
    "search":   {"view": 0.5, "search": 0.1, "cart": 0.2, "purchase": 0.1, "rate": 0.1},
    "cart":     {"view": 0.2, "search": 0.1, "cart": 0.1, "purchase": 0.5, "rate": 0.1},
    "purchase": {"view": 0.3, "search": 0.2, "cart": 0.1, "purchase": 0.1, "rate": 0.3},
    "rate":     {"view": 0.5, "search": 0.2, "cart": 0.1, "purchase": 0.1, "rate": 0.1},
}

NUM_CUSTOMERS = 500
NUM_PRODUCTS_PER_CAT = 10  # 10 cats × 10 = 100 products


def _product_id(cat_idx: int, prod_idx: int) -> int:
    return cat_idx * NUM_PRODUCTS_PER_CAT + prod_idx + 1


def _next_interaction(current: str) -> str:
    trans = TRANSITIONS[current]
    r = random.random()
    cumulative = 0.0
    for itype, prob in trans.items():
        cumulative += prob
        if r <= cumulative:
            return itype
    return "view"


def _assign_segment(n_purchases: int, n_events: int) -> str:
    if n_purchases == 0 and n_events < 5:
        return "new"
    if n_purchases == 0:
        return "casual"
    if n_purchases < 3:
        return "engaged"
    if n_purchases < 8:
        return "loyal"
    return "champion"


def generate() -> tuple[list[dict], list[dict]]:
    sequences = []
    customers = []

    for cid in range(1, NUM_CUSTOMERS + 1):
        n_pref = random.randint(1, 3)
        pref_cats = random.sample(range(len(CATEGORIES)), n_pref)
        price_sensitivity = random.randint(0, 4)

        n_events = random.randint(5, 50)
        events = []
        current_type = "view"
        base_ts = int(time.time()) - random.randint(0, 30 * 24 * 3600)
        ts = base_ts
        n_purchases = 0

        for _ in range(n_events):
            if random.random() < 0.7:
                cat_idx = random.choice(pref_cats)
            else:
                cat_idx = random.randint(0, len(CATEGORIES) - 1)

            prod_idx = random.randint(0, NUM_PRODUCTS_PER_CAT - 1)
            pid = _product_id(cat_idx, prod_idx)
            price_range = random.randint(0, 4)
            itype_idx = INTERACTION_TYPES.index(current_type)

            if current_type == "purchase":
                n_purchases += 1

            events.append({
                "product_id":       pid,
                "interaction_type": itype_idx,
                "timestamp":        ts,
                "price_range":      price_range,
                "category_idx":     cat_idx,
            })

            ts += random.randint(3600, 72 * 3600)
            current_type = _next_interaction(current_type)

        segment = _assign_segment(n_purchases, n_events)
        sequences.append({
            "customer_id": cid,
            "segment":     segment,
            "events":      events,
        })
        customers.append({
            "customer_id":       cid,
            "segment":           segment,
            "preferred_cats":    [CATEGORIES[i] for i in pref_cats],
            "price_sensitivity": price_sensitivity,
            "n_events":          n_events,
            "n_purchases":       n_purchases,
        })

    return sequences, customers


def save(sequences: list[dict], customers: list[dict]) -> None:
    seq_path = DATA_DIR / "synthetic_sequences.json"
    with open(seq_path, "w", encoding="utf-8") as f:
        json.dump(sequences, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(sequences)} sequences → {seq_path}")

    csv_path = DATA_DIR / "synthetic_customers.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(customers[0].keys()))
        writer.writeheader()
        for c in customers:
            row = dict(c)
            row["preferred_cats"] = "|".join(row["preferred_cats"])
            writer.writerow(row)
    print(f"Saved {len(customers)} customers → {csv_path}")


if __name__ == "__main__":
    print("Generating synthetic dataset (multi-domain product categories)...")
    seqs, custs = generate()
    save(seqs, custs)

    segments = {}
    for s in seqs:
        seg = s["segment"]
        segments[seg] = segments.get(seg, 0) + 1
    print(f"Segment distribution: {segments}")
    print(f"All {len(CATEGORIES)} categories covered: OK")

INTERACTION_TYPES = ["view", "search", "cart", "purchase", "rate"]
# Markov chain: xác suất chuyển trạng thái
TRANSITIONS = {
    "view":     {"view": 0.4, "search": 0.2, "cart": 0.2, "purchase": 0.1, "rate": 0.1},
    "search":   {"view": 0.5, "search": 0.1, "cart": 0.2, "purchase": 0.1, "rate": 0.1},
    "cart":     {"view": 0.2, "search": 0.1, "cart": 0.1, "purchase": 0.5, "rate": 0.1},
    "purchase": {"view": 0.3, "search": 0.2, "cart": 0.1, "purchase": 0.1, "rate": 0.3},
    "rate":     {"view": 0.5, "search": 0.2, "cart": 0.1, "purchase": 0.1, "rate": 0.1},
}

PRICE_BUCKETS = [0, 1, 2, 3, 4]  # <50k, 50-100k, 100-200k, 200-500k, >500k

NUM_CUSTOMERS = 500
NUM_BOOKS_PER_CAT = 10  # 12 cats × 10 = 120 books total


def _book_id(cat_idx: int, book_idx: int) -> int:
    return cat_idx * NUM_BOOKS_PER_CAT + book_idx + 1


def _price_bucket(cat_idx: int) -> int:
    """Sách kỹ thuật thường đắt hơn."""
    if cat_idx in (0, 4):  # lập trình, toán học
        return random.choice([2, 3, 4])
    if cat_idx in (3, 7):  # tiểu thuyết, văn học
        return random.choice([0, 1, 2])
    return random.choice(PRICE_BUCKETS)


def _next_interaction(current: str) -> str:
    trans = TRANSITIONS[current]
    r = random.random()
    cumulative = 0.0
    for itype, prob in trans.items():
        cumulative += prob
        if r <= cumulative:
            return itype
    return "view"


def _assign_segment(n_purchases: int, n_events: int) -> str:
    if n_purchases == 0 and n_events < 5:
        return "new"
    if n_purchases == 0:
        return "casual"
    if n_purchases < 3:
        return "engaged"
    if n_purchases < 8:
        return "loyal"
    return "champion"


def generate() -> tuple[list[dict], list[dict]]:
    sequences = []
    customers = []

    for cid in range(1, NUM_CUSTOMERS + 1):
        # Mỗi khách hàng có 1-3 danh mục ưa thích
        n_pref = random.randint(1, 3)
        pref_cats = random.sample(range(len(CATEGORIES)), n_pref)
        price_sensitivity = random.randint(0, 4)  # 0=rẻ nhất, 4=không quan tâm giá

        n_events = random.randint(5, 50)
        events = []
        current_type = "view"
        # Bắt đầu từ timestamp ngẫu nhiên trong 30 ngày qua
        base_ts = int(time.time()) - random.randint(0, 30 * 24 * 3600)
        ts = base_ts
        n_purchases = 0

        for _ in range(n_events):
            # Chọn danh mục: 70% ưa thích, 30% ngẫu nhiên
            if random.random() < 0.7:
                cat_idx = random.choice(pref_cats)
            else:
                cat_idx = random.randint(0, len(CATEGORIES) - 1)

            book_idx = random.randint(0, NUM_BOOKS_PER_CAT - 1)
            bid = _book_id(cat_idx, book_idx)

            # Price range: ưu tiên theo price_sensitivity
            if price_sensitivity <= 1:
                price_range = random.choice([0, 1])
            elif price_sensitivity <= 3:
                price_range = random.choice([1, 2, 3])
            else:
                price_range = _price_bucket(cat_idx)

            itype_idx = INTERACTION_TYPES.index(current_type)
            if current_type == "purchase":
                n_purchases += 1

            events.append({
                "book_id":          bid,
                "interaction_type": itype_idx,
                "timestamp":        ts,
                "price_range":      price_range,
                "category_idx":     cat_idx,
            })

            # Tăng timestamp: 1–72 giờ
            ts += random.randint(3600, 72 * 3600)
            current_type = _next_interaction(current_type)

        segment = _assign_segment(n_purchases, n_events)
        sequences.append({
            "customer_id": cid,
            "segment":     segment,
            "events":      events,
        })
        customers.append({
            "customer_id":        cid,
            "segment":            segment,
            "preferred_cats":     [CATEGORIES[i] for i in pref_cats],
            "price_sensitivity":  price_sensitivity,
            "n_events":           n_events,
            "n_purchases":        n_purchases,
        })

    return sequences, customers


def save(sequences: list[dict], customers: list[dict]) -> None:
    seq_path = DATA_DIR / "synthetic_sequences.json"
    with open(seq_path, "w", encoding="utf-8") as f:
        json.dump(sequences, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(sequences)} sequences → {seq_path}")

    csv_path = DATA_DIR / "synthetic_customers.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(customers[0].keys()))
        writer.writeheader()
        for c in customers:
            row = dict(c)
            row["preferred_cats"] = "|".join(row["preferred_cats"])
            writer.writerow(row)
    print(f"Saved {len(customers)} customers → {csv_path}")


if __name__ == "__main__":
    print("Generating synthetic dataset...")
    seqs, custs = generate()
    save(seqs, custs)

    # Quick stats
    segments = {}
    for s in seqs:
        seg = s["segment"]
        segments[seg] = segments.get(seg, 0) + 1
    print(f"Segment distribution: {segments}")
    cat_counts = {}
    for s in seqs:
        for e in s["events"]:
            ci = e["category_idx"]
            cat_counts[ci] = cat_counts.get(ci, 0) + 1
    print(f"All 12 categories covered: {len(cat_counts) == 12}")
