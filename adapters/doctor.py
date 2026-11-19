"""Adapter for tifxyz-doctor.

Runs `tifxyz-doctor audit <seg_dir> --json <tmp>/audit.json` and recursively
walks the JSON to collect flagged cells from "rc", "bbox_rc", "quad_a", and
"quad_b" entries.

Limitation: tifxyz-doctor lists at most 50 located examples per kind of
finding, so the returned grid may under-represent very large defect regions.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import tifffile

ROOT = Path(__file__).resolve().parents[2]


def flag_grid(seg_dir: str) -> "np.ndarray":
    """Run tifxyz-doctor on the tifxyz segment directory seg_dir and return a boolean array of shape (rows, cols),
    the same shape as the segment grid, where True marks every grid cell the tool itself flagged."""
    shape = tifffile.imread(os.path.join(seg_dir, "x.tif")).shape[:2]
    rows, cols = shape
    flags = np.zeros((rows, cols), dtype=bool)

    with tempfile.TemporaryDirectory() as tmp:
        audit_json = os.path.join(tmp, "audit.json")
        tool = str(ROOT / "venvs" / "tifxyz-doctor" / "bin" / "tifxyz-doctor")
        subprocess.run(
            [tool, "audit", seg_dir, "--json", audit_json],
            check=False,
            capture_output=True,
        )
        with open(audit_json, "r") as f:
            data = json.load(f)

    def _walk(obj):
        if isinstance(obj, dict):
            if "rc" in obj:
                rc = obj["rc"]
                if isinstance(rc, (list, tuple)) and len(rc) == 2:
                    r, c = int(rc[0]), int(rc[1])
                    if 0 <= r < rows and 0 <= c < cols:
                        flags[r, c] = True
            if "bbox_rc" in obj:
                bbox = obj["bbox_rc"]
                if isinstance(bbox, (list, tuple)) and len(bbox) == 2:
                    r0, c0 = int(bbox[0][0]), int(bbox[0][1])
                    r1, c1 = int(bbox[1][0]), int(bbox[1][1])
                    r0 = max(0, min(r0, rows - 1))
                    r1 = max(0, min(r1, rows - 1))
                    c0 = max(0, min(c0, cols - 1))
                    c1 = max(0, min(c1, cols - 1))
                    if r0 <= r1 and c0 <= c1:
                        flags[r0:r1 + 1, c0:c1 + 1] = True
            for key in ("quad_a", "quad_b"):
                if key in obj:
                    q = obj[key]
                    if isinstance(q, (list, tuple)) and len(q) == 2:
                        r, c = int(q[0]), int(q[1])
                        if 0 <= r < rows and 0 <= c < cols:
                            flags[r, c] = True
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)

    _walk(data)
    return flags
