"""Disaggregate tifxyz-repair's findings by defect type (its own labels). Run with the repair venv's python:
    ../venvs/tifxyz-repair/bin/python repair_by_type.py <bench run dir>
Same planted cases as run_bench.py (same seeds, levels, injector); no thresholds are changed."""
import json, os, sys, tempfile
from multiprocessing import Pool
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from tdbench import tifxyz_io as io
from tdbench.inject import inject, KINDS
from tifxyz_repair.core import load_patch
from tifxyz_repair.deep import inspect_patch
LEVELS = ((5.0, 1.1), (10.0, 1.25), (20.0, 1.5), (40.0, 2.0)); TOL = 2

def cells_by_type(d):
    m = inspect_patch(load_patch(Path(d)), collect_cells=True, winding_aware=bool(int(os.environ.get('WINDING', '0'))), winding_min_frac=float(os.environ.get('WFRAC', '0.02')))
    return {k: np.asarray(v, dtype=int).reshape(-1, 2) for k, v in (m.get("defect_cells") or {}).items()}, m["grid"]

def grid(cells, shape):
    g = np.zeros(shape, bool)
    if len(cells): g[np.clip(cells[:, 0], 0, shape[0]-1), np.clip(cells[:, 1], 0, shape[1]-1)] = True
    return g

def job(a):
    seg_name, seed, lv = a
    seg = io.load(str(ROOT / os.environ.get("BENCH_DATA", "data") / seg_name)); jump, stretch = LEVELS[lv]
    bad, defects = inject(seg, KINDS, 3, seed, jump_vox=jump, stretch=stretch)
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "x"); io.save(bad, d); by, shape = cells_by_type(d)
    out = []
    for t, c in by.items():
        g = grid(c, tuple(shape))
        for x in defects:
            hit = bool(g[max(0, x.r0-TOL):x.r1+TOL, max(0, x.c0-TOL):x.c1+TOL].any())
            out.append((t, x.kind, hit))
    return out, sorted(by)

def clean_job(seg_name):
    seg = io.load(str(ROOT / os.environ.get("BENCH_DATA", "data") / seg_name)); valid = io.valid_mask(seg)
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "c"); io.save(seg, d); by, shape = cells_by_type(d)
    return {t: int(grid(c, tuple(shape))[valid].sum()) for t, c in by.items()}, int(valid.sum())

if __name__ == "__main__":
    run = Path(sys.argv[1]); segs = sorted(p.name for p in (ROOT / os.environ.get("BENCH_DATA", "data")).iterdir() if p.is_dir())
    with Pool(12) as p:
        res = p.map(job, [(s, sd, lv) for s in segs for sd in range(1, 11) for lv in range(4)])
        cl = p.map(clean_job, segs)
    types = sorted({t for _, ts in res for t in ts})
    agg = {t: {k: [0, 0] for k in KINDS} for t in types}
    for rows, _ in res:
        for t, k, hit in rows:
            agg[t][k][1] += 1; agg[t][k][0] += int(hit)
    valid = sum(v for _, v in cl); dens = {t: sum(c.get(t, 0) for c, _ in cl) / valid for t in types}
    out = {"types": types, "clean_flag_per_1000": {t: 1000 * dens[t] for t in types},
           "recall": {t: {k: agg[t][k][0] / agg[t][k][1] for k in KINDS} for t in types},
           "counts": agg}
    json.dump(out, open(run / ("repair_by_type_winding.json" if os.environ.get("WINDING") == "1" else "repair_by_type.json"), "w"), indent=1)
    print("type | clean flags /1000 cells | " + " | ".join(KINDS))
    for t in types:
        print(f"{t} | {1000*dens[t]:.2f} | " + " | ".join(f"{agg[t][k][0]}/{agg[t][k][1]}" for k in KINDS))
