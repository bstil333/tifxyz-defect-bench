# tifxyz-defect-bench

A labeled benchmark for tifxyz segment quality checkers. It plants defects with exact known positions in a clean segment, runs a checker on the clean and the defective copy, and reports per-defect recall, the false-alarm density on the clean copy, and a chance baseline.

**Why.** Community tools check tifxyz surfaces, but measuring how often they catch real problems is hard without known answers. tifxyz-doctor's README says it has no authoritative labeled corpus of naturally occurring correct and incorrect geometry; its v0.2 reports detection of controlled synthetic steps on human-reviewed PHercParis4 patches. windcheck ships a benchmark of 274 real traces and says no independent external method has yet been measured on it. SwitchBench, posted by a community member in the Vesuvius Challenge Discord on September 30, 2026, is described there as 213 confirmed natural sheet switches on PHercParis4; we could not open its repository on November 25, 2026, so we have not run it. This benchmark takes a simple, different route: it plants defects with exact known positions (synthetic, so it does not measure natural errors) in clean public segments, runs each tool at its default settings through an adapter we wrote, and reports per-defect recall, false-alarm density on the clean copy, and a chance baseline. It complements the benchmarks above and does not replace them.

**Defects planted:** hole (a block of interior cells set invalid), sheet_jump (a block displaced along the local normal), normal_flip (a block's parameterization reversed), stretch (a block's in-plane spacing scaled).

**Results.** See `FINDINGS_2026-10-28.md` (the original report) and `FINDINGS_2026-10-29.md` (a correction to one of its findings, a fix to tifxyz-repair, and results on 22 real public segments). **The second report corrects the first:** tifxyz-repair's high recall on the two test segments came largely from a cue that fired on winding clearance, not from detection.

**Limits.** Defects are synthetic and planted on clean surfaces, so real autosegmentation errors are not covered. Real segments contain their own flags, so "clean" means only "nothing planted." The hit rule (any flag within two cells) is generous, which is why a chance baseline is reported.

**Use.** `python -m tdbench make --seg <tifxyz dir> --out <dir> --seed 1`, then `python run_bench.py` and `python summarize.py`. `BENCH_DATA=<dir>` selects the source segments. Some public segments use LZW-compressed TIFFs; install `imagecodecs` in each tool's environment.

**Tests.** `python -m unittest discover -s tests -v`. Python 3, NumPy and tifffile only.

**License.** MIT, Benjamin L. Stilwell.
