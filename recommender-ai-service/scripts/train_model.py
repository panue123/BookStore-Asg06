"""
Train LSTM Behavior Model (PyTorch) — primary model cho AI service.
Bám sát yêu cầu môn: LSTM + sequence modeling + multi-head output.

Usage:
  python scripts/train_model.py

Output:
  artifacts/lstm_behavior_model.pt   ← LSTM (primary)
  artifacts/behavior_model.pt        ← MLP fallback
  artifacts/model_comparison.json    ← so sánh kết quả
"""
import sys
import os
import json
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

LSTM_PATH  = ARTIFACTS_DIR / "lstm_behavior_model.pt"
MLP_PATH   = ARTIFACTS_DIR / "behavior_model.pt"
COMP_PATH  = ARTIFACTS_DIR / "model_comparison.json"

MAX_SEQ_LEN = 20
FEATURE_DIM = 5   # [product_id_norm, interaction_type, timestamp_norm, price_range, category_norm]
N_SEGMENTS  = 5
N_SAMPLES   = 2000
EPOCHS      = 50
LR          = 1e-3
BATCH_SIZE  = 64
HIDDEN_DIM  = 64

SEGMENTS = ["new", "casual", "engaged", "loyal", "champion"]
INTERACTION_TYPES = ["view", "search", "cart", "purchase", "rate"]


# ── Synthetic data generator ──────────────────────────────────────────────────

def generate_sequences(n: int = N_SAMPLES):
    """Generate synthetic event sequences with labels."""
    import random
    random.seed(42)
    np.random.seed(42)

    X_list, y_seg, y_eng, y_prop = [], [], [], []

    for _ in range(n):
        # Random customer profile
        n_events = random.randint(5, MAX_SEQ_LEN)
        pref_cats = random.sample(range(30), random.randint(1, 3))
        n_purchases = 0

        mat = np.zeros((MAX_SEQ_LEN, FEATURE_DIM), dtype=np.float32)
        current_type = 0  # view

        TRANSITIONS = {
            0: [0.4, 0.2, 0.2, 0.1, 0.1],  # view
            1: [0.5, 0.1, 0.2, 0.1, 0.1],  # search
            2: [0.2, 0.1, 0.1, 0.5, 0.1],  # cart
            3: [0.3, 0.2, 0.1, 0.1, 0.3],  # purchase
            4: [0.5, 0.2, 0.1, 0.1, 0.1],  # rate
        }

        import time
        base_ts = int(time.time()) - random.randint(0, 30 * 86400)
        ts = base_ts

        for i in range(n_events):
            pid = random.randint(1, 500)
            cat_idx = random.choice(pref_cats) if random.random() < 0.7 else random.randint(0, 29)
            price_range = random.randint(0, 4)

            mat[i, 0] = min(pid / 500, 1.0)
            mat[i, 1] = current_type / 4.0
            mat[i, 2] = min((ts % (30 * 86400)) / (30 * 86400), 1.0)
            mat[i, 3] = price_range / 4.0
            mat[i, 4] = min(cat_idx / 30, 1.0)

            if current_type == 3:
                n_purchases += 1

            ts += random.randint(3600, 72 * 3600)
            probs = TRANSITIONS[current_type]
            current_type = np.random.choice(5, p=probs)

        # Labels
        if n_purchases == 0 and n_events < 5:
            seg = 0  # new
        elif n_purchases == 0:
            seg = 1  # casual
        elif n_purchases < 3:
            seg = 2  # engaged
        elif n_purchases < 8:
            seg = 3  # loyal
        else:
            seg = 4  # champion

        propensity = min(n_purchases / max(n_events, 1) * 3, 1.0)
        engagement = min((n_events * 0.3 + n_purchases * 0.7) / 20, 1.0)

        X_list.append(mat)
        y_seg.append(seg)
        y_eng.append(engagement)
        y_prop.append(propensity)

    X     = torch.tensor(np.array(X_list), dtype=torch.float32)
    y_seg = torch.tensor(y_seg, dtype=torch.long)
    y_eng = torch.tensor(y_eng, dtype=torch.float32)
    y_prop = torch.tensor(y_prop, dtype=torch.float32)
    return X, y_seg, y_eng, y_prop


# ── LSTM Model ────────────────────────────────────────────────────────────────

class LSTMBehaviorModel(nn.Module):
    """
    LSTM sequence model — bám sát yêu cầu môn.
    input_dim=5, hidden_dim=64, output: engagement + propensity + segment
    """
    def __init__(self, input_dim=FEATURE_DIM, hidden_dim=HIDDEN_DIM, num_layers=2, n_segments=N_SEGMENTS):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers,
                            batch_first=True, dropout=0.2)
        self.dropout = nn.Dropout(0.2)
        self.engagement_head = nn.Sequential(nn.Linear(hidden_dim, 16), nn.ReLU(), nn.Linear(16, 1), nn.Sigmoid())
        self.propensity_head = nn.Sequential(nn.Linear(hidden_dim, 16), nn.ReLU(), nn.Linear(16, 1), nn.Sigmoid())
        self.segment_head    = nn.Linear(hidden_dim, n_segments)

    def forward(self, x):
        out, _ = self.lstm(x)
        last = self.dropout(out[:, -1, :])
        return self.engagement_head(last).squeeze(-1), self.propensity_head(last).squeeze(-1), self.segment_head(last)


# ── MLP fallback ──────────────────────────────────────────────────────────────

class BehaviorMLP(nn.Module):
    def __init__(self, feature_dim=10, hidden=32, n_segments=N_SEGMENTS):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(feature_dim, hidden), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(hidden, hidden // 2), nn.ReLU(),
        )
        self.engagement_head = nn.Sequential(nn.Linear(hidden // 2, 1), nn.Sigmoid())
        self.propensity_head = nn.Sequential(nn.Linear(hidden // 2, 1), nn.Sigmoid())
        self.segment_head    = nn.Linear(hidden // 2, n_segments)

    def forward(self, x):
        h = self.shared(x)
        return self.engagement_head(h).squeeze(-1), self.propensity_head(h).squeeze(-1), self.segment_head(h)


# ── Training ──────────────────────────────────────────────────────────────────

def train_model(model, X, y_seg, y_eng, y_prop, model_name: str, epochs=EPOCHS):
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    mse_loss  = nn.MSELoss()
    ce_loss   = nn.CrossEntropyLoss()

    split = int(len(X) * 0.8)
    X_tr, X_val = X[:split], X[split:]
    ys_tr, ys_val = y_seg[:split], y_seg[split:]
    ye_tr, ye_val = y_eng[:split], y_eng[split:]
    yp_tr, yp_val = y_prop[:split], y_prop[split:]

    dataset = TensorDataset(X_tr, ys_tr, ye_tr, yp_tr)
    loader  = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    print(f"\n── Training {model_name} ({epochs} epochs) ──")
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for xb, ys_b, ye_b, yp_b in loader:
            optimizer.zero_grad()
            eng_p, prop_p, seg_l = model(xb)
            loss = mse_loss(eng_p, ye_b) + mse_loss(prop_p, yp_b) + ce_loss(seg_l, ys_b) * 0.5
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        if epoch % 10 == 0:
            model.eval()
            with torch.no_grad():
                ve, vp, vs = model(X_val)
                val_loss = mse_loss(ve, ye_val) + mse_loss(vp, yp_val) + ce_loss(vs, ys_val) * 0.5
                seg_acc  = (vs.argmax(dim=-1) == ys_val).float().mean().item()
            print(f"  Epoch {epoch:3d}/{epochs} | train_loss={total_loss/len(loader):.4f} | val_loss={val_loss:.4f} | seg_acc={seg_acc:.3f}")

    # Final eval
    model.eval()
    with torch.no_grad():
        ve, vp, vs = model(X_val)
        val_loss = (mse_loss(ve, ye_val) + mse_loss(vp, yp_val) + ce_loss(vs, ys_val) * 0.5).item()
        seg_acc  = (vs.argmax(dim=-1) == ys_val).float().mean().item()
    return {"val_loss": round(val_loss, 4), "val_seg_acc": round(seg_acc, 4)}


def train():
    print("Generating synthetic sequence data...")
    X_seq, y_seg, y_eng, y_prop = generate_sequences(N_SAMPLES)
    print(f"Dataset: {X_seq.shape}, segments: {torch.bincount(y_seg).tolist()}")

    results = {}

    # 1. Train LSTM (primary)
    lstm = LSTMBehaviorModel()
    r = train_model(lstm, X_seq, y_seg, y_eng, y_prop, "LSTM (primary)")
    results["LSTM"] = r
    torch.save(lstm.state_dict(), str(LSTM_PATH))
    print(f"\nLSTM saved → {LSTM_PATH}")

    # 2. Train MLP fallback (uses flattened features)
    # Generate simple feature vectors for MLP
    np.random.seed(42)
    X_mlp = np.random.rand(N_SAMPLES, 10).astype(np.float32)
    X_mlp_t = torch.tensor(X_mlp)
    mlp = BehaviorMLP()
    r_mlp = train_model(mlp, X_mlp_t, y_seg, y_eng, y_prop, "MLP (fallback)")
    results["MLP"] = r_mlp
    torch.save(mlp.state_dict(), str(MLP_PATH))
    print(f"MLP saved → {MLP_PATH}")

    # Save comparison
    with open(COMP_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nModel comparison saved → {COMP_PATH}")
    print("\nResults:")
    for name, r in results.items():
        print(f"  {name}: val_loss={r['val_loss']:.4f}, seg_acc={r['val_seg_acc']:.3f}")

    # Quick inference test
    print("\nLSTM inference test (first 3 samples):")
    lstm.eval()
    with torch.no_grad():
        eng_p, prop_p, seg_l = lstm(X_seq[:3])
        for i in range(3):
            seg = SEGMENTS[seg_l[i].argmax().item()]
            print(f"  eng={eng_p[i]:.3f} prop={prop_p[i]:.3f} seg={seg}")


if __name__ == "__main__":
    train()
