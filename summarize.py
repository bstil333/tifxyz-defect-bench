"""Turn results.json into the numbers a report needs.

    python summarize.py <bench run dir>

Writes summary.json and tables.md in that directory. Everything is computed from results.json;
nothing is typed in by hand. Recall = share of planted defects with a flagged cell within `tol`
cells of the block. Because a tool that flags many cells everywhere would 'find' defects by luck,
each recall is shown next to a CHANCE baseline: the probability that a block's neighborhood contains
at least one flagged cell if the tool's flags were scattered at random at the density it shows on the
CLEAN segment. Recall far above chance is evidence of detection; recall near chance is not."""
import json, math, sys
from collections import defaultdict
from pathlib import Path

KINDS = ("hole", "sheet_jump", "normal_flip", "stretch")
TOOLS = ("doctor", "repair", "repair_winding", "windcheck")
NAMES = {"doctor": "tifxyz-doctor", "repair": "tifxyz-repair", "repair_winding": "tifxyz-repair (winding-aware)", "windcheck": "windcheck"}
BLOCK = (10, 24)  # planted block size in cells (rows, cols), from tdbench.inject default


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pct(x):
    return "n/a" if x is None else f"{100 * x:.0f}%"


def main(run):
    run = Path(run); R = json.load(open(run / "results.json"))
    tol = R["tol_cells"]; nb = (BLOCK[0] + 2 * tol) * (BLOCK[1] + 2 * tol)
    S = {"segments": R["segments"], "seeds": R["seeds"], "levels": R["levels"], "per_kind": R["per_kind"], "tol_cells": tol,
         "neighborhood_cells": nb, "tools": {}}
    # clean-segment behavior
    clean = defaultdict(lambda: {"flagged": 0, "valid": 0, "errors": 0, "per_segment": {}})
    for c in R["clean"]:
        t = clean[c["tool"]]
        if c["error"]:
            t["errors"] += 1; continue
        t["flagged"] += c["flagged_cells_clean"]; t["valid"] += c["valid_cells"]
        t["per_segment"][c["segment"]] = {"flagged": c["flagged_cells_clean"], "valid": c["valid_cells"]}
    for tool in TOOLS:
        cases = [c for c in R["cases"] if c["tool"] == tool]
        errs = [c for c in cases if c["error"]]
        dens = clean[tool]["flagged"] / clean[tool]["valid"] if clean[tool]["valid"] else None
        chance = None if dens is None else 1 - (1 - dens) ** nb
        by = {k: {"planted": 0, "found": 0} for k in KINDS}
        sev = {k: defaultdict(lambda: {"planted": 0, "found": 0}) for k in ("sheet_jump", "stretch")}
        seg = defaultdict(lambda: defaultdict(lambda: {"planted": 0, "found": 0}))
        for c in cases:
            if c["error"]:
                continue
            for d in c["defects"]:
                by[d["kind"]]["planted"] += 1; by[d["kind"]]["found"] += int(d["found"])
                seg[c["segment"]][d["kind"]]["planted"] += 1; seg[c["segment"]][d["kind"]]["found"] += int(d["found"])
                if d["kind"] in sev:
                    key = d["params"].get("offset_vox") if d["kind"] == "sheet_jump" else d["params"].get("factor")
                    sev[d["kind"]][key]["planted"] += 1; sev[d["kind"]][key]["found"] += int(d["found"])
        for k, v in by.items():
            v["recall"] = v["found"] / v["planted"] if v["planted"] else None
            v["ci95"] = wilson(v["found"], v["planted"])
        S["tools"][tool] = {
            "runs": len(cases), "errors": len(errs), "median_seconds": sorted(c["seconds"] for c in cases)[len(cases) // 2] if cases else None,
            "clean_flagged_cells": clean[tool]["flagged"], "clean_valid_cells": clean[tool]["valid"],
            "false_positive_per_1000_cells": None if dens is None else 1000 * dens, "clean_flag_density": dens,
            "chance_recall": chance, "by_kind": by,
            "severity": {k: {str(x): {**y, "recall": y["found"] / y["planted"]} for x, y in sorted(v.items())} for k, v in sev.items()},
            "per_segment": {s: {k: {**v, "recall": v["found"] / v["planted"]} for k, v in kk.items()} for s, kk in seg.items()},
            "error_examples": sorted({c["error"] for c in errs})[:3]}
    json.dump(S, open(run / "summary.json", "w"), indent=1)

    L = []
    L.append(f"Segments: {len(R['segments'])} · seeds per segment: {R['seeds']} · severity levels: {len(R['levels'])} · "
             f"defects per kind per case: {R['per_kind']} · hit tolerance: {tol} cells\n")
    L.append("### False alarms on the clean segments\n")
    L.append("| tool | flagged cells | valid cells | per 1,000 valid cells | chance of a flag landing in any defect-sized neighborhood |")
    L.append("|---|---|---|---|---|")
    for t in TOOLS:
        x = S["tools"][t]
        L.append(f"| {NAMES[t]} | {x['clean_flagged_cells']:,} | {x['clean_valid_cells']:,} | "
                 f"{x['false_positive_per_1000_cells']:.2f} | {pct(x['chance_recall'])} |")
    L.append("\n### Recall by defect kind (found / planted, 95% interval) against chance\n")
    L.append("| tool | " + " | ".join(KINDS) + " | chance |")
    L.append("|---|" + "---|" * (len(KINDS) + 1))
    for t in TOOLS:
        x = S["tools"][t]; cells = []
        for k in KINDS:
            v = x["by_kind"][k]; lo, hi = v["ci95"]
            cells.append(f"{v['found']}/{v['planted']} = {pct(v['recall'])} ({pct(lo)}–{pct(hi)})")
        L.append(f"| {NAMES[t]} | " + " | ".join(cells) + f" | {pct(x['chance_recall'])} |")
    for kind, label, unit in (("sheet_jump", "Sheet-jump recall by offset", "voxels"), ("stretch", "Stretch recall by factor", "×")):
        L.append(f"\n### {label}\n")
        keys = sorted({k for t in TOOLS for k in S["tools"][t]["severity"][kind]}, key=float)
        L.append("| tool | " + " | ".join(f"{k} {unit}" for k in keys) + " |")
        L.append("|---|" + "---|" * len(keys))
        for t in TOOLS:
            sv = S["tools"][t]["severity"][kind]
            L.append(f"| {NAMES[t]} | " + " | ".join(
                (f"{sv[k]['found']}/{sv[k]['planted']} = {pct(sv[k]['recall'])}" if k in sv else "n/a") for k in keys) + " |")
    L.append("\n### Run health\n")
    L.append("| tool | tool runs | errors | median seconds per run |")
    L.append("|---|---|---|---|")
    for t in TOOLS:
        x = S["tools"][t]
        L.append(f"| {NAMES[t]} | {x['runs']} | {x['errors']} | {x['median_seconds']} |")
    open(run / "tables.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1])
