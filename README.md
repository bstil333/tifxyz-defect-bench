# tifxyz-defect-bench

Plant known defects in a clean tifxyz surface, then measure how many a QA tool finds and how many
flags it raises on the original, which contains no planted defect.

Existing community tools check tifxyz surfaces, but their own READMEs say they have no labeled
corpus to measure precision and recall against. This gives them one: every defect's position is
known exactly.

## Defect kinds
| kind | what is planted |
|---|---|
| hole | a block of interior cells set invalid |
| sheet_jump | a block displaced along the local normal (a sheet switch) |
| normal_flip | a block's parameterization reversed (folds at its edge) |
| stretch | a block's in-plane spacing scaled about its center |

## Use
```
python -m tdbench make --seg <tifxyz dir> --out <dir> --seed 1
```
Writes `clean/`, `defective/` and `truth.json`. Run any QA tool on both, convert its findings to a
boolean grid of flagged cells, and pass them to `tdbench.score.score`.

## Test
```
python -m unittest discover -s tests -v
```
MIT license. Python 3, NumPy and tifffile only.

## Added 2026-10-29
* `adapters/repair_winding.py`: tifxyz-repair with its optional winding-aware self-proximity mode (see `FINDINGS_2026-10-29.md`).
* `BENCH_DATA=<dir>` selects the folder of source segments (default `data`); `BENCH_DATA=data_all` runs the 14-segment set.
* Some public segments use LZW-compressed TIFFs; install `imagecodecs` in each tool's environment.
* `repair_by_type.py` takes `WINDING=1` (and `WFRAC=<fraction>`) to split the winding-aware result by cue.

## Correction (2026-10-29, recorded 2026-11-18)
An earlier note called the 8.3% of valid cells flagged by tifxyz-repair's `self_proximity` cue "false
alarms" on clean surfaces. That label was wrong. The flagged pairs on the two PHerc0332 segments sit a nearly
constant 411-422 columns apart (one wrap of the scroll) and 6-10 voxels apart in 3D: those segments are
multi-wrap bands, and each cell sits beside the next turn of the same sheet. "Clean" here means "no planted
defect", not "no self-proximity". On multi-wrap bands a flag count is flags remaining, not verified false
alarms, because these surfaces have no answer key for self-proximity. Stretch, flip and self-proximity
regions on real segments need a person to inspect them before anyone calls them errors; interior holes are
objective.
