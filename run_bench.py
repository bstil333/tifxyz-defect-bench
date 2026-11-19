"""Run the three community QA tools on planted-defect segments and record what each one flags.

    python run_bench.py [--seeds N] [--out runs/bench_<stamp>]

For each public segment, each seed and each severity level it plants defects (known positions),
writes the defective segment, runs every tool's adapter on it, and records per-defect found/missed.
It also runs every tool on the CLEAN segment to measure false alarms. Adapters never see truth.
Writes results.json (every case, every tool, errors included)."""
import argparse, importlib.util, json, os, sys, tempfile, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from tdbench import tifxyz_io as io          # noqa: E402
from tdbench.inject import inject, KINDS      # noqa: E402
from tdbench.score import found               # noqa: E402

TOOLS = ("doctor", "repair", "repair_winding", "windcheck")
# severity levels pair a sheet-jump offset (voxels) with a stretch factor; hole and normal_flip have no severity
LEVELS = ((5.0, 1.1), (10.0, 1.25), (20.0, 1.5), (40.0, 2.0))
PER_KIND = 3
TOL = 2


def adapter(name):
    spec = importlib.util.spec_from_file_location("adapter_" + name, HERE / "adapters" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.flag_grid


def run_tool(tool, seg_dir):
    t0 = time.time()
    try:
        flag = adapter(tool)(seg_dir)
        return flag, None, round(time.time() - t0, 2)
    except Exception as e:  # noqa: BLE001 - a tool crash is a result, not a harness failure
        return None, f"{type(e).__name__}: {e}"[:300], round(time.time() - t0, 2)


def case_job(a):
    seg_name, seed, level = a
    jump, stretch = LEVELS[level]
    seg = io.load(str(ROOT / os.environ.get("BENCH_DATA", "data") / seg_name))
    bad, defects = inject(seg, KINDS, PER_KIND, seed, jump_vox=jump, stretch=stretch)
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "defective"); io.save(bad, d)
        for tool in TOOLS:
            flag, err, secs = run_tool(tool, d)
            rec = {"segment": seg_name, "seed": seed, "level": level, "tool": tool, "error": err, "seconds": secs,
                   "flagged_cells": None if flag is None else int(flag.sum()),
                   "defects": [{"kind": x.kind, "r0": x.r0, "r1": x.r1, "c0": x.c0, "c1": x.c1, "params": x.params,
                                "found": None if flag is None else bool(found(flag, x.to_json(), TOL))} for x in defects]}
            rows.append(rec)
    return rows


def clean_job(a):
    seg_name, tool = a
    seg = io.load(str(ROOT / os.environ.get("BENCH_DATA", "data") / seg_name))
    valid = io.valid_mask(seg)
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "clean"); io.save(seg, d)
        flag, err, secs = run_tool(tool, d)
    return {"segment": seg_name, "tool": tool, "error": err, "seconds": secs,
            "valid_cells": int(valid.sum()), "grid": list(valid.shape),
            "flagged_cells_clean": None if flag is None else int(flag[valid].sum()),
            "flagged_cells_clean_any": None if flag is None else int(flag.sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default=str(ROOT / "runs" / ("bench_" + time.strftime("%Y%m%d_%H%M%S"))))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    segs = sorted(p.name for p in (ROOT / os.environ.get("BENCH_DATA", "data")).iterdir() if p.is_dir())
    jobs = [(s, seed, lv) for s in segs for seed in range(1, a.seeds + 1) for lv in range(len(LEVELS))]
    t0 = time.time()
    with Pool(a.workers) as pool:
        cases = [r for rows in pool.map(case_job, jobs, chunksize=1) for r in rows]
        clean = pool.map(clean_job, [(s, t) for s in segs for t in TOOLS], chunksize=1)
    out = {"segments": segs, "seeds": a.seeds, "levels": [{"jump_vox": j, "stretch": s} for j, s in LEVELS],
           "per_kind": PER_KIND, "tol_cells": TOL, "cases": cases, "clean": clean,
           "wall_seconds": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(a.out, "results.json"), "w"))
    errs = sum(1 for c in cases if c["error"]) + sum(1 for c in clean if c["error"])
    print(f"{len(cases)} tool-case runs, {len(clean)} clean runs, {errs} errors, {out['wall_seconds']} s -> {a.out}")


if __name__ == "__main__":
    main()
