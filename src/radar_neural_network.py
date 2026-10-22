#!/usr/bin/env python3
"""Train a small CPU-friendly CNN on measurement-disjoint radar segments."""
from __future__ import annotations
import argparse, json, random
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

CLASSES = ["drone", "bird", "human"]
LABELS = {**{f"D{i}": "drone" for i in range(1, 7)}, "black-headed gull": "bird", "heron": "bird", "pigeon": "bird", "raven": "bird", "seagull": "bird", "seagull and black-headed gull": "bird", "human_run": "human", "human_walk": "human"}

def groups(ms, seed):
    rng = np.random.default_rng(seed); out = {}; targets = {"train": .70, "validation": .15, "test": .15}
    for cls in CLASSES:
        g = [m for m in ms if m["class"] == cls]; total = sum(m["n"] for m in g); counts = {k: 0 for k in targets}
        for i in sorted(rng.permutation(len(g)), key=lambda j: g[j]["n"], reverse=True):
            s = min(targets, key=lambda k: counts[k] / max(targets[k] * total, 1)); out[g[i]["id"]] = s; counts[s] += g[i]["n"]
    return out

def load_data(path, seed):
    raw = np.load(path, allow_pickle=True)
    if raw.shape != (130, 6): raise ValueError(f"expected (130, 6), got {raw.shape}")
    ms = []
    for i, row in enumerate(raw):
        label = str(np.asarray(row[0]).squeeze()); signal = np.asarray(row[1])
        if label == "CR": continue
        if signal.shape[0] != 1280 or not np.iscomplexobj(signal): raise ValueError(f"bad signal at {i}")
        ms.append({"id": i, "class": LABELS[label], "n": signal.shape[1], "signal": signal})
    split = groups(ms, seed); xs = {s: [] for s in ("train", "validation", "test")}; ys = {s: [] for s in xs}
    for m in ms:
        s = split[m["id"]]; a = np.abs(m["signal"]).astype(np.float32).T.reshape(-1, 5, 256); xs[s].append(a); ys[s].extend([CLASSES.index(m["class"])] * len(a))
    x = {s: np.concatenate(xs[s]) for s in xs}; y = {s: np.array(ys[s], dtype=np.int64) for s in xs}; mean, std = x["train"].mean(), x["train"].std()
    return {s: (x[s] - mean) / max(std, 1e-6) for s in x}, y, {"train_mean": float(mean), "train_std": float(std), "counts": {s: len(y[s]) for s in y}}

class RadarCNN(nn.Module):
    def __init__(self):
        super().__init__(); self.body = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d(1)); self.head = nn.Linear(64, 3)
    def forward(self, x): return self.head(self.body(x).flatten(1))

def score(y, p):
    cm = np.zeros((3, 3), dtype=int)
    for a, b in zip(y, p): cm[a, b] += 1
    per = {}; fs = []
    for i, c in enumerate(CLASSES):
        pr = cm[i, i] / max(cm[:, i].sum(), 1); re = cm[i, i] / max(cm[i].sum(), 1); f = 2 * pr * re / max(pr + re, 1e-12); fs.append(f); per[c] = {"precision": pr, "recall": re, "f1": f}
    return {"accuracy": float(np.trace(cm) / cm.sum()), "macro_f1": float(np.mean(fs)), "per_class": per, "confusion_matrix": cm.tolist(), "n_segments": int(cm.sum()), "classes": CLASSES}

def main():
    p = argparse.ArgumentParser(); p.add_argument("--data", type=Path, required=True); p.add_argument("--output", type=Path, default=Path("results/radar-neural-network")); p.add_argument("--epochs", type=int, default=8); p.add_argument("--batch-size", type=int, default=256); p.add_argument("--seed", type=int, default=590); a = p.parse_args()
    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed); x, y, prep = load_data(a.data, a.seed); model = RadarCNN(); opt = torch.optim.Adam(model.parameters(), lr=1e-3); criterion = nn.CrossEntropyLoss(); loader = DataLoader(TensorDataset(torch.from_numpy(x["train"][:, None]), torch.from_numpy(y["train"])), batch_size=a.batch_size, shuffle=True)
    history = []; best = (-1, None)
    for epoch in range(1, a.epochs + 1):
        model.train()
        for xb, yb in loader: opt.zero_grad(); criterion(model(xb), yb).backward(); opt.step()
        model.eval()
        with torch.no_grad(): pred = model(torch.from_numpy(x["validation"][:, None])).argmax(1).numpy()
        val = score(y["validation"], pred); history.append({"epoch": epoch, **val})
        if val["macro_f1"] > best[0]: best = (val["macro_f1"], {k: v.clone() for k, v in model.state_dict().items()})
    model.load_state_dict(best[1]); model.eval()
    with torch.no_grad(): pred = model(torch.from_numpy(x["test"][:, None])).argmax(1).numpy()
    result = {"model": "RadarCNN", "seed": a.seed, "epochs": a.epochs, "input": "normalized magnitude 5x256", "reflector_policy": "excluded", "preprocessing": prep, "validation": history[-1], "test": score(y["test"], pred), "history": history}
    a.output.mkdir(parents=True, exist_ok=True); (a.output / "radar-neural-network-metrics.json").write_text(json.dumps(result, indent=2) + "\n"); torch.save(model.state_dict(), a.output / "radar-cnn.pt"); print(json.dumps(result, indent=2))
if __name__ == "__main__": main()
