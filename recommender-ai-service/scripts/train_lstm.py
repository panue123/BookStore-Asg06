"""
Train LSTM + Baseline Models (CNN1D, RNN)
──────────────────────────────────────────
Đọc synthetic_sequences.json, train 3 models, so sánh, lưu LSTM.

Usage:
  python scripts/train_lstm.py

Output:
  artifacts/lstm_behavior_model.h5
  artifacts/model_comparison.json
"""
import json
import sys
import os
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)
DATA_PATH = Path("data/synthetic_sequences.json")

MAX_SEQ_LEN = 20
FEATURE_DIM = 4   # [book_id_norm, interaction_type, timestamp_norm, price_range]
N_SEGMENTS  = 5
MAX_BOOK_ID = 120  # 12 cats × 10 books
EPOCHS      = 30
BATCH_SIZE  = 64

SEGMENTS = ["new", "casual", "engaged", "loyal", "champion"]


def load_data():
    if not DATA_PATH.exists():
        print(f"Data not found at {DATA_PATH}, generating...")
        from generate_sequences import generate, save
        seqs, custs = generate()
        save(seqs, custs)

    with open(DATA_PATH, encoding="utf-8") as f:
        sequences = json.load(f)
    return sequences


def encode_sequences(sequences: list[dict]):
    """Encode sequences → (X, y_segment, y_propensity)."""
    X_list, y_seg, y_prop = [], [], []

    for seq in sequences:
        events = seq["events"]
        seg_idx = SEGMENTS.index(seq["segment"]) if seq["segment"] in SEGMENTS else 1

        # Tính propensity từ tỉ lệ purchase events
        n_purchase = sum(1 for e in events if e["interaction_type"] == 3)
        propensity = min(n_purchase / max(len(events), 1) * 3, 1.0)

        # Encode events → matrix (MAX_SEQ_LEN, FEATURE_DIM)
        mat = np.zeros((MAX_SEQ_LEN, FEATURE_DIM), dtype=np.float32)
        for i, e in enumerate(events[:MAX_SEQ_LEN]):
            mat[i, 0] = e["book_id"] / MAX_BOOK_ID
            mat[i, 1] = e["interaction_type"] / 4.0
            # Normalize timestamp trong window 30 ngày
            mat[i, 2] = min((e["timestamp"] % (30 * 86400)) / (30 * 86400), 1.0)
            mat[i, 3] = e["price_range"] / 4.0

        X_list.append(mat)
        y_seg.append(seg_idx)
        y_prop.append(propensity)

    X = np.array(X_list, dtype=np.float32)
    y_seg = np.array(y_seg, dtype=np.int32)
    y_prop = np.array(y_prop, dtype=np.float32)
    return X, y_seg, y_prop


def build_lstm(seq_len=MAX_SEQ_LEN, feat_dim=FEATURE_DIM):
    import tensorflow as tf
    inp = tf.keras.Input(shape=(seq_len, feat_dim))
    x = tf.keras.layers.Masking(mask_value=0.0)(inp)
    x = tf.keras.layers.LSTM(64, return_sequences=True)(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.LSTM(32)(x)
    x = tf.keras.layers.Dense(16, activation="relu")(x)
    prop_out = tf.keras.layers.Dense(1, activation="sigmoid", name="propensity")(x)
    seg_out  = tf.keras.layers.Dense(N_SEGMENTS, activation="softmax", name="segment")(x)
    model = tf.keras.Model(inputs=inp, outputs=[prop_out, seg_out])
    model.compile(
        optimizer="adam",
        loss={"propensity": "mse", "segment": "sparse_categorical_crossentropy"},
        loss_weights={"propensity": 1.0, "segment": 0.5},
        metrics={"propensity": "mae", "segment": "accuracy"},
    )
    return model


def build_cnn1d(seq_len=MAX_SEQ_LEN, feat_dim=FEATURE_DIM):
    import tensorflow as tf
    inp = tf.keras.Input(shape=(seq_len, feat_dim))
    x = tf.keras.layers.Conv1D(64, 3, activation="relu", padding="same")(inp)
    x = tf.keras.layers.GlobalMaxPooling1D()(x)
    x = tf.keras.layers.Dense(16, activation="relu")(x)
    prop_out = tf.keras.layers.Dense(1, activation="sigmoid", name="propensity")(x)
    seg_out  = tf.keras.layers.Dense(N_SEGMENTS, activation="softmax", name="segment")(x)
    model = tf.keras.Model(inputs=inp, outputs=[prop_out, seg_out])
    model.compile(
        optimizer="adam",
        loss={"propensity": "mse", "segment": "sparse_categorical_crossentropy"},
        loss_weights={"propensity": 1.0, "segment": 0.5},
        metrics={"propensity": "mae", "segment": "accuracy"},
    )
    return model


def build_rnn(seq_len=MAX_SEQ_LEN, feat_dim=FEATURE_DIM):
    import tensorflow as tf
    inp = tf.keras.Input(shape=(seq_len, feat_dim))
    x = tf.keras.layers.Masking(mask_value=0.0)(inp)
    x = tf.keras.layers.SimpleRNN(64)(x)
    x = tf.keras.layers.Dense(16, activation="relu")(x)
    prop_out = tf.keras.layers.Dense(1, activation="sigmoid", name="propensity")(x)
    seg_out  = tf.keras.layers.Dense(N_SEGMENTS, activation="softmax", name="segment")(x)
    model = tf.keras.Model(inputs=inp, outputs=[prop_out, seg_out])
    model.compile(
        optimizer="adam",
        loss={"propensity": "mse", "segment": "sparse_categorical_crossentropy"},
        loss_weights={"propensity": 1.0, "segment": 0.5},
        metrics={"propensity": "mae", "segment": "accuracy"},
    )
    return model


def train_and_compare():
    print("Loading data...")
    sequences = load_data()
    X, y_seg, y_prop = encode_sequences(sequences)
    print(f"Dataset: {X.shape}, segments: {np.bincount(y_seg)}")

    # Train/val split
    split = int(len(X) * 0.8)
    X_tr, X_val = X[:split], X[split:]
    ys_tr, ys_val = y_seg[:split], y_seg[split:]
    yp_tr, yp_val = y_prop[:split], y_prop[split:]

    results = {}
    models_to_train = [
        ("LSTM",  build_lstm),
        ("CNN1D", build_cnn1d),
        ("RNN",   build_rnn),
    ]

    best_lstm = None
    for name, builder in models_to_train:
        print(f"\n── Training {name} ──")
        model = builder()
        history = model.fit(
            X_tr, {"propensity": yp_tr, "segment": ys_tr},
            validation_data=(X_val, {"propensity": yp_val, "segment": ys_val}),
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            verbose=1,
        )
        val_loss = history.history["val_loss"][-1]
        val_seg_acc = history.history.get("val_segment_accuracy", [0])[-1]
        results[name] = {
            "val_loss":     round(float(val_loss), 4),
            "val_seg_acc":  round(float(val_seg_acc), 4),
        }
        print(f"{name}: val_loss={val_loss:.4f}, val_seg_acc={val_seg_acc:.4f}")
        if name == "LSTM":
            best_lstm = model

    # Save LSTM
    lstm_path = ARTIFACTS_DIR / "lstm_behavior_model.h5"
    best_lstm.save(str(lstm_path))
    print(f"\nLSTM saved → {lstm_path}")

    # Save comparison
    comp_path = ARTIFACTS_DIR / "model_comparison.json"
    with open(comp_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Comparison saved → {comp_path}")
    print("\nModel comparison:")
    for name, r in results.items():
        print(f"  {name}: {r}")


if __name__ == "__main__":
    train_and_compare()
