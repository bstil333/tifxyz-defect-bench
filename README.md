# tifxyz-defect-bench

A labeled benchmark for tifxyz segment quality checkers. It plants defects with exact known positions in a clean segment, runs a checker on the clean and the defective copy, and reports per-defect recall, the false-alarm density on the clean copy, and a chance baseline.

**Why.** The READMEs of tifxyz-doctor, tifxyz-repair and windcheck say that no labeled corpus exists to measure how often they catch real problems. This is a first one.

**Defects planted:** hole (a block of interior cells set invalid), sheet_jump (a block displaced along the local normal), normal_flip (a block's parameterization reversed), stretch (a block's in-plane spacing scaled).

**Results.** See `FINDINGS_2026-10-28.md` (the original report) and `FINDINGS_2026-10-29.md` (a correction to one of its findings, a fix to tifxyz-repair, and results on 22 real public segments). **The second report corrects the first:** tifxyz-repair's high recall on the two test segments came largely from a cue that fired on winding clearance, not from detection.

**Limits.** Defects are synthetic and planted on clean surfaces, so real autosegmentation errors are not covered. Real segments contain their own flags, so "clean" means only "nothing planted." The hit rule (any flag within two cells) is generous, which is why a chance baseline is reported.

**Use.** `python -m tdbench make --seg <tifxyz dir> --out <dir> --seed 1`, then `python run_bench.py` and `python summarize.py`. `BENCH_DATA=<dir>` selects the source segments. Some public segments use LZW-compressed TIFFs; install `imagecodecs` in each tool's environment.

**Tests.** `python -m unittest discover -s tests -v`. Python 3, NumPy and tifffile only.

**License.** MIT, Benjamin L. Stilwell.
