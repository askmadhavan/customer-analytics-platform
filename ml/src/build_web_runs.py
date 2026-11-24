"""Precompute the example model runs shown in the web app.

Trains the same Random Forest as train.py for every combination of the
five RFM features and three test splits, and writes the metrics the
Training and Evaluation pages need to api/app/static/models.json.

Run from the repository root:  python ml/src/build_web_runs.py
"""
import itertools
import json
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split

DATA_PATH = "ml/data/training/customer_churn.csv"
OUT_PATH = "api/app/static/models.json"
FEATS = ["recency", "frequency", "monetary", "avg_order_value", "customer_lifetime_days"]
GRID = np.linspace(0, 1, 21)
THRESHOLDS = [round(t, 2) for t in np.arange(0.05, 0.96, 0.05)]


def confusion(y_true, prob):
    out = []
    for t in THRESHOLDS:
        p = (prob >= t).astype(int)
        out.append([
            int(((p == 1) & (y_true == 1)).sum()), int(((p == 0) & (y_true == 1)).sum()),
            int(((p == 1) & (y_true == 0)).sum()), int(((p == 0) & (y_true == 0)).sum()),
        ])
    return out


def roc_points(y_true, prob):
    fpr, tpr, _ = roc_curve(y_true, prob)
    return [round(float(v), 3) for v in np.interp(GRID, fpr, tpr)]


def main():
    df = pd.read_csv(DATA_PATH)
    y = df["churn"].values
    models = {}
    start = time.time()
    for split in [0.1, 0.2, 0.3]:
        for k in range(1, len(FEATS) + 1):
            for combo in itertools.combinations(FEATS, k):
                cols = list(combo)
                X = df[cols].values
                Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=split, random_state=42)
                model = RandomForestClassifier(
                    n_estimators=200, class_weight="balanced", random_state=42, n_jobs=-1
                ).fit(Xtr, ytr)
                p_test = model.predict_proba(Xte)[:, 1]
                p_all = model.predict_proba(X)[:, 1]
                key = f"{int(split * 100)}:{','.join(cols)}"
                models[key] = {
                    "n_train": int(len(ytr)), "n_test": int(len(yte)),
                    "base_test": round(float(yte.mean()), 4), "base_all": round(float(y.mean()), 4),
                    "auc_test": round(float(roc_auc_score(yte, p_test)), 4),
                    "auc_all": round(float(roc_auc_score(y, p_all)), 4),
                    "roc_test": roc_points(yte, p_test), "roc_all": roc_points(y, p_all),
                    "cm_test": confusion(yte, p_test), "cm_all": confusion(y, p_all),
                    "imp": [round(float(v), 4) for v in model.feature_importances_],
                }
                print(key, models[key]["auc_test"], f"{time.time() - start:.0f}s", flush=True)

    rec = df["recency"].values
    windows = list(range(30, 361, 15))
    sample = df.sample(12, random_state=11)[
        ["customer_unique_id", "recency", "frequency", "monetary", "avg_order_value"]
    ]
    insights = {
        "n": int(len(df)),
        "windows": windows,
        "churned_at": [int((rec > w).sum()) for w in windows],
        "freq": df["frequency"].clip(upper=4).value_counts().sort_index().astype(int).tolist(),
        "recency_hist": np.histogram(rec, bins=list(range(0, 660, 30)))[0].astype(int).tolist(),
        "sample": sample.round(2).to_dict(orient="records"),
    }
    with open(OUT_PATH, "w") as f:
        json.dump(
            {"features": FEATS, "thresholds": THRESHOLDS, "grid": [round(g, 2) for g in GRID],
             "models": models, "insights": insights},
            f, separators=(",", ":"),
        )
    print("wrote", OUT_PATH)


if __name__ == "__main__":
    main()
