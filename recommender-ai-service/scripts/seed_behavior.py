"""
Seed behavior data for model testing/training.

Safe default:
- export mode writes synthetic interactions to JSON file (no runtime pollution)

Optional:
- track mode sends events to /api/v1/track for isolated demo customers

Usage:
    python scripts/seed_behavior.py
    python scripts/seed_behavior.py --mode export --output data/synthetic_behavior_events.json
    python scripts/seed_behavior.py --mode track --customer-id-offset 1000
"""
import sys
import json
import time
import argparse
from pathlib import Path
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8011"
CUSTOMER_ID_OFFSET = 1000
DEFAULT_MODE = "export"
DEFAULT_OUTPUT = "data/synthetic_behavior_events.json"

# customer_id → list of (product_id, interaction_type, rating_or_None)
INTERACTIONS = [
    # Customer 1 — lập trình, sách kỹ thuật
    (1, 1,  "view",     None),
    (1, 1,  "cart",     None),
    (1, 1,  "purchase", None),
    (1, 1,  "rate",     5),
    (1, 2,  "view",     None),
    (1, 2,  "purchase", None),
    (1, 2,  "rate",     4),
    (1, 9,  "view",     None),
    (1, 9,  "cart",     None),
    (1, 4,  "view",     None),
    (1, 4,  "purchase", None),
    (1, 4,  "rate",     5),

    # Customer 2 — điện tử, công nghệ
    (2, 9,  "view",     None),
    (2, 9,  "cart",     None),
    (2, 9,  "purchase", None),
    (2, 9,  "rate",     5),
    (2, 11, "view",     None),
    (2, 11, "cart",     None),
    (2, 10, "view",     None),
    (2, 10, "purchase", None),
    (2, 10, "rate",     4),
    (2, 1,  "view",     None),
    (2, 3,  "view",     None),

    # Customer 3 — sách văn học, lịch sử
    (3, 4,  "view",     None),
    (3, 4,  "purchase", None),
    (3, 4,  "rate",     5),
    (3, 5,  "view",     None),
    (3, 5,  "purchase", None),
    (3, 5,  "rate",     5),
    (3, 8,  "view",     None),
    (3, 8,  "purchase", None),
    (3, 8,  "rate",     4),
    (3, 3,  "view",     None),
    (3, 3,  "purchase", None),

    # Customer 4 — thời trang, làm đẹp
    (4, 12, "view",     None),
    (4, 12, "cart",     None),
    (4, 12, "purchase", None),
    (4, 13, "view",     None),
    (4, 13, "cart",     None),
    (4, 14, "view",     None),
    (4, 14, "purchase", None),
    (4, 14, "rate",     5),
    (4, 15, "view",     None),
    (4, 15, "purchase", None),

    # Customer 5 — thể thao, đồ chơi
    (5, 16, "view",     None),
    (5, 16, "cart",     None),
    (5, 16, "purchase", None),
    (5, 17, "view",     None),
    (5, 17, "purchase", None),
    (5, 17, "rate",     5),
    (5, 18, "view",     None),
    (5, 18, "cart",     None),
    (5, 6,  "view",     None),
    (5, 6,  "purchase", None),

    # Customer 6 — sách kinh doanh, kỹ năng
    (6, 6,  "view",     None),
    (6, 6,  "purchase", None),
    (6, 6,  "rate",     5),
    (6, 7,  "view",     None),
    (6, 7,  "purchase", None),
    (6, 7,  "rate",     5),
    (6, 1,  "view",     None),
    (6, 2,  "view",     None),
    (6, 2,  "purchase", None),

    # Customer 7 — đa dạng (loyal customer)
    (7, 1,  "view",     None),
    (7, 1,  "purchase", None),
    (7, 3,  "view",     None),
    (7, 3,  "purchase", None),
    (7, 4,  "view",     None),
    (7, 4,  "purchase", None),
    (7, 7,  "view",     None),
    (7, 7,  "purchase", None),
    (7, 9,  "view",     None),
    (7, 9,  "purchase", None),
    (7, 9,  "rate",     5),
    (7, 11, "view",     None),
    (7, 11, "purchase", None),
    (7, 17, "view",     None),
    (7, 17, "purchase", None),
    (7, 17, "rate",     5),

    # Customer 8 — new user, chỉ xem
    (8, 1,  "view",     None),
    (8, 3,  "view",     None),
    (8, 9,  "view",     None),
    (8, 11, "view",     None),

    # Customer 9 — grocery, gia dụng
    (9, 21, "view",     None),
    (9, 21, "purchase", None),
    (9, 21, "rate",     5),
    (9, 22, "view",     None),
    (9, 22, "purchase", None),
    (9, 25, "view",     None),
    (9, 26, "view",     None),
    (9, 26, "purchase", None),

    # Customer 10 — champion (mua nhiều nhất)
    (10, 1,  "purchase", None),
    (10, 2,  "purchase", None),
    (10, 3,  "purchase", None),
    (10, 4,  "purchase", None),
    (10, 5,  "purchase", None),
    (10, 6,  "purchase", None),
    (10, 7,  "purchase", None),
    (10, 9,  "purchase", None),
    (10, 9,  "rate",     5),
    (10, 11, "purchase", None),
    (10, 11, "rate",     5),
    (10, 14, "purchase", None),
    (10, 17, "purchase", None),
    (10, 17, "rate",     5),
]


def _post(url: str, body: dict) -> tuple[int, dict]:
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)}


def _to_events(customer_id_offset: int) -> list[dict]:
    events: list[dict] = []
    for customer_id, product_id, itype, rating in INTERACTIONS:
        payload = {
            "customer_id": customer_id + customer_id_offset,
            "product_id": product_id,
            "interaction_type": itype,
        }
        if rating is not None:
            payload["rating"] = rating
        events.append(payload)
    return events


def export_events(output_path: str, customer_id_offset: int = CUSTOMER_ID_OFFSET) -> int:
    events = _to_events(customer_id_offset)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported {len(events)} synthetic events -> {out}")
    return len(events)


def track_events(base_url: str = BASE_URL, customer_id_offset: int = CUSTOMER_ID_OFFSET):
    print(f"Seeding behavior interactions → {base_url}")
    ok = 0
    fail = 0
    for payload in _to_events(customer_id_offset):

        code, resp = _post(f"{base_url}/api/v1/track", payload)
        if code == 200 and resp.get("tracked"):
            ok += 1
        else:
            fail += 1
            if fail <= 3:
                print(
                    f"  WARN: C{payload['customer_id']}→P{payload['product_id']} "
                    f"[{payload['interaction_type']}] → {code} {resp}"
                )

    print(f"Behavior seeded: {ok} tracked, {fail} failed")
    return ok


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["export", "track"], default=DEFAULT_MODE)
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--customer-id-offset", type=int, default=CUSTOMER_ID_OFFSET)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--allow-low-offset", action="store_true")
    args = parser.parse_args()

    if args.mode == "export":
        export_events(args.output, args.customer_id_offset)
        sys.exit(0)

    if args.customer_id_offset < 1000 and not args.allow_low_offset:
        raise SystemExit(
            "Refusing to track with customer_id_offset < 1000. "
            "Use --allow-low-offset only in isolated test DBs."
        )

    track_events(args.base_url, args.customer_id_offset)
