"""Adapter for tifxyz-repair with the winding-aware self-proximity option (branch winding-aware-self-proximity).

Parses the JSON emitted by the helper script (grid shape, defect_cells dict,
error field) and maps every reported [row, col] pair onto a boolean ndarray.

Limitation: none known beyond the tool's own default thresholds.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import tifffile

ROOT = Path(__file__).resolve().parents[2]

HELPER = '''\
import json
import sys
from pathlib import Path

import numpy as np
from tifxyz_repair.core import load_patch
from tifxyz_repair.deep import inspect_patch

patch = load_patch(Path(sys.argv[1]))
metrics = inspect_patch(patch, collect_cells=True, winding_aware=True)

cells = metrics.get("defect_cells") or {}
cleaned = {}
for k, v in cells.items():
    cleaned[k] = np.asarray(v).tolist()

result = {
    "grid": metrics.get("grid"),
    "cells": cleaned,
    "error": metrics.get("error"),
}
print(json.dumps(result))
'''


def flag_grid(seg_dir: str) -> "np.ndarray":
    """Run tifxyz-repair on the tifxyz segment directory *seg_dir* and return
    a boolean array of shape (rows, cols) where True marks every grid cell the
    tool itself flagged."""
    grid_shape = tifffile.imread(os.path.join(seg_dir, "x.tif")).shape
    rows, cols = int(grid_shape[0]), int(grid_shape[1])
    flag = np.zeros((rows, cols), dtype=bool)

    python_bin = str(ROOT / "venvs" / "tifxyz-repair" / "bin" / "python")

    with tempfile.TemporaryDirectory() as tmpdir:
        helper_path = os.path.join(tmpdir, "_helper.py")
        with open(helper_path, "w") as fh:
            fh.write(HELPER)

        try:
            proc = subprocess.run(
                [python_bin, helper_path, seg_dir],
                capture_output=True,
                text=True,
                timeout=600,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("tifxyz-repair helper timed out")

        if proc.returncode != 0:
            raise RuntimeError(
                f"tifxyz-repair helper exited {proc.returncode}: {proc.stderr.strip()}"
            )

        data = json.loads(proc.stdout)

    if data.get("error"):
        raise RuntimeError(f"tifxyz-repair reported error: {data['error']}")

    cells = data.get("cells") or {}
    for _defect_name, locations in cells.items():
        for loc in locations:
            if loc is None:
                continue
            r = max(0, min(int(loc[0]), rows - 1))
            c = max(0, min(int(loc[1]), cols - 1))
            flag[r, c] = True

    return flag
