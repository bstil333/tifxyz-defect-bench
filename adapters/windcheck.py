"""Adapter for windcheck (self-intersection census).

Parses the *_check_certificate.json produced by `windcheck check` and flags
grid cells listed in "crossing_sites" (both quad_a and quad_b of each entry).

Limitation: if the certificate contains a key "crossing_sites_truncated_to"
and len(crossing_sites) equals that integer cap, the tool has truncated the
list and some crossing sites may be missing from the output.
"""

import glob
import json
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import tifffile

ROOT = Path(__file__).resolve().parents[2]


def flag_grid(seg_dir: str) -> "np.ndarray":
    """Run windcheck on the tifxyz segment directory seg_dir and return a boolean array of shape (rows, cols),
    the same shape as the segment grid, where True marks every grid cell the tool itself flagged."""
    seg_dir = os.path.abspath(seg_dir)
    rows, cols = tifffile.imread(os.path.join(seg_dir, "x.tif")).shape[:2]
    flags = np.zeros((rows, cols), dtype=bool)

    with tempfile.TemporaryDirectory() as tmp:
        tool = str(ROOT / "venvs" / "windcheck" / "bin" / "windcheck")
        proc = subprocess.run(
            [tool, "check", seg_dir, "--out", tmp],
            capture_output=True,
            text=True,
            check=False,
        )

        matches = glob.glob(os.path.join(tmp, "*_check_certificate.json"))
        if not matches:
            tail = (proc.stdout or "")[-500:] + (proc.stderr or "")[-500:]
            raise RuntimeError(
                f"windcheck certificate not found in {tmp!r}. "
                f"Tool output tail:\n{tail}"
            )

        with open(matches[0], "r") as f:
            cert = json.load(f)

        sites = cert.get("crossing_sites", [])
        for site in sites:
            for key in ("quad_a", "quad_b"):
                loc = site.get(key)
                if loc is None:
                    continue
                r = max(0, min(int(loc[0]), rows - 1))
                c = max(0, min(int(loc[1]), cols - 1))
                flags[r, c] = True

    return flags
