"""Minimal tifxyz reader/writer. A tifxyz segment is a directory with x.tif, y.tif, z.tif
(float32 grids, invalid cells = -1) and meta.json."""
import json, os
import numpy as np
import tifffile


def load(path):
    seg = {a: tifffile.imread(os.path.join(path, f"{a}.tif")).astype(np.float32) for a in "xyz"}
    with open(os.path.join(path, "meta.json")) as f:
        seg["meta"] = json.load(f)
    return seg


def valid_mask(seg):
    """Valid cell = x, y, z all present (the -1 sentinel marks invalid) and z > 0."""
    return (seg["x"] != -1) & (seg["y"] != -1) & (seg["z"] > 0)


def save(seg, path):
    os.makedirs(path, exist_ok=True)
    for a in "xyz":
        tifffile.imwrite(os.path.join(path, f"{a}.tif"), seg[a].astype(np.float32))
    meta = dict(seg["meta"])
    m = valid_mask(seg)
    if m.any():  # keep the bbox honest so tools that check it do not flag our edit
        pts = np.stack([seg[a][m] for a in "xyz"], 1)
        meta["bbox"] = [pts.min(0).tolist(), pts.max(0).tolist()]
    with open(os.path.join(path, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
