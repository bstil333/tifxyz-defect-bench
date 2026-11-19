"""python -m tdbench make --seg <tifxyz dir> --out <dir> [--seed N] [--per-kind K]
Writes <out>/clean (copy), <out>/defective (tifxyz) and <out>/truth.json."""
import argparse, json, os
from . import tifxyz_io as io
from .inject import inject, KINDS


def main():
    ap = argparse.ArgumentParser(prog="tdbench")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make"); m.add_argument("--seg", required=True); m.add_argument("--out", required=True)
    m.add_argument("--seed", type=int, default=0); m.add_argument("--per-kind", type=int, default=2)
    a = ap.parse_args()
    seg = io.load(a.seg)
    bad, defects = inject(seg, KINDS, a.per_kind, a.seed)
    io.save(seg, os.path.join(a.out, "clean")); io.save(bad, os.path.join(a.out, "defective"))
    with open(os.path.join(a.out, "truth.json"), "w") as f:
        json.dump({"source": os.path.basename(os.path.normpath(a.seg)), "seed": a.seed,
                   "defects": [d.to_json() for d in defects]}, f, indent=2)
    print(f"{len(defects)} defects planted -> {a.out}")


if __name__ == "__main__":
    main()
