"""Plant known defects in a clean tifxyz segment and record exactly where.

Every injector returns a Defect with `kind`, the cell block (r0, r1, c0, c1) that is the
ground truth, and parameters. Blocks are only placed where every cell is valid, and never
overlap each other, so a detector's hit or miss on a block is unambiguous."""
from dataclasses import dataclass, asdict
import numpy as np
from .tifxyz_io import valid_mask

KINDS = ("hole", "sheet_jump", "normal_flip", "stretch")


@dataclass
class Defect:
    kind: str
    r0: int
    r1: int
    c0: int
    c1: int
    params: dict

    def to_json(self):
        return asdict(self)


def _local_normal(seg, r, c):
    """Unit normal from the grid's tangent vectors at one cell (cross of d/dc and d/dr)."""
    P = np.stack([seg[a] for a in "xyz"], -1)
    r = int(np.clip(r, 1, P.shape[0] - 2)); c = int(np.clip(c, 1, P.shape[1] - 2))
    dc = P[r, c + 1] - P[r, c - 1]
    dr = P[r + 1, c] - P[r - 1, c]
    n = np.cross(dc, dr)
    return n / (np.linalg.norm(n) + 1e-9)


def _free_block(valid, taken, h, w, rng, tries=400):
    """Random h x w block that is fully valid, has a 1-cell valid margin, and avoids `taken`."""
    H, W = valid.shape
    for _ in range(tries):
        r0 = int(rng.integers(2, max(3, H - h - 2))); c0 = int(rng.integers(2, max(3, W - w - 2)))
        r1, c1 = r0 + h, c0 + w
        if r1 + 1 > H or c1 + 1 > W:
            continue
        if not valid[r0 - 1:r1 + 1, c0 - 1:c1 + 1].all():
            continue
        if taken[max(0, r0 - 6):r1 + 6, max(0, c0 - 6):c1 + 6].any():
            continue
        return r0, r1, c0, c1
    return None


def inject(seg, kinds=KINDS, per_kind=2, seed=0, block=(10, 24), jump_vox=40.0, stretch=2.0):
    """Return (defective_segment, [Defect, ...]). `block` is (rows, cols) of each planted block."""
    rng = np.random.default_rng(seed)
    out = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in seg.items()}
    valid = valid_mask(seg)
    taken = np.zeros_like(valid)
    defects = []
    for kind in kinds:
        for _ in range(per_kind):
            b = _free_block(valid, taken, block[0], block[1], rng)
            if b is None:
                continue
            r0, r1, c0, c1 = b
            sl = (slice(r0, r1), slice(c0, c1))
            params = {}
            if kind == "hole":
                for a in "xyz":
                    out[a][sl] = -1.0
            elif kind == "sheet_jump":
                n = _local_normal(seg, (r0 + r1) // 2, (c0 + c1) // 2)
                for i, a in enumerate("xyz"):
                    out[a][sl] = out[a][sl] + n[i] * jump_vox
                params = {"offset_vox": jump_vox, "normal": n.round(4).tolist()}
            elif kind == "normal_flip":  # reverse the parameterization of the block (folds at its edge)
                for a in "xyz":
                    out[a][sl] = out[a][sl][::-1]
            elif kind == "stretch":  # grow the block's in-plane spacing about its center
                for a in "xyz":
                    blk = out[a][sl]; ctr = blk.mean()
                    out[a][sl] = ctr + (blk - ctr) * stretch
                params = {"factor": stretch}
            else:
                raise ValueError(kind)
            taken[max(0, r0 - 1):r1 + 1, max(0, c0 - 1):c1 + 1] = True
            defects.append(Defect(kind, r0, r1, c0, c1, params))
    return out, defects
