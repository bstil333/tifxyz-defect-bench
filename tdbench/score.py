"""Score a tool's flagged cells against planted defects.

A detector's output is a boolean grid the same shape as the segment (True = flagged cell).
- A defect is FOUND if any flagged cell lies within `tol` cells of its block.
- False-positive rate is measured on the CLEAN segment: flagged cells per 1,000 valid cells.
Both numbers are reported per defect kind, because a tool that finds holes and misses
sheet jumps should not get an average that hides it."""
import numpy as np


def found(flag, d, tol=2):
    r0, r1 = max(0, d["r0"] - tol), d["r1"] + tol
    c0, c1 = max(0, d["c0"] - tol), d["c1"] + tol
    return bool(flag[r0:r1, c0:c1].any())


def score(flag_defective, defects, flag_clean, valid_clean, tol=2):
    by = {}
    for d in defects:
        k = by.setdefault(d["kind"], {"planted": 0, "found": 0})
        k["planted"] += 1
        k["found"] += found(flag_defective, d, tol)
    for k in by.values():
        k["recall"] = k["found"] / k["planted"] if k["planted"] else None
    n_valid = int(valid_clean.sum())
    fp = int(flag_clean[valid_clean].sum()) if n_valid else 0
    return {"by_kind": by, "clean_flagged_cells": fp, "clean_valid_cells": n_valid,
            "false_positive_per_1000_cells": 1000.0 * fp / n_valid if n_valid else None}
