Segments: 2 · seeds per segment: 10 · severity levels: 4 · defects per kind per case: 3 · hit tolerance: 2 cells

### False alarms on the clean segments

| tool | flagged cells | valid cells | per 1,000 valid cells | chance of a flag landing in any defect-sized neighborhood |
|---|---|---|---|---|
| tifxyz-doctor | 99 | 267,342 | 0.37 | 14% |
| tifxyz-repair | 22,245 | 267,342 | 83.21 | 100% |
| tifxyz-repair (winding-aware) | 33 | 267,342 | 0.12 | 5% |
| windcheck | 0 | 267,342 | 0.00 | 0% |

### Recall by defect kind (found / planted, 95% interval) against chance

| tool | hole | sheet_jump | normal_flip | stretch | chance |
|---|---|---|---|---|---|
| tifxyz-doctor | 236/240 = 98% (96%–99%) | 34/240 = 14% (10%–19%) | 240/240 = 100% (98%–100%) | 240/240 = 100% (98%–100%) | 14% |
| tifxyz-repair | 240/240 = 100% (98%–100%) | 222/240 = 92% (88%–95%) | 240/240 = 100% (98%–100%) | 231/240 = 96% (93%–98%) | 100% |
| tifxyz-repair (winding-aware) | 240/240 = 100% (98%–100%) | 128/240 = 53% (47%–60%) | 240/240 = 100% (98%–100%) | 187/240 = 78% (72%–83%) | 5% |
| windcheck | 7/240 = 3% (1%–6%) | 126/240 = 52% (46%–59%) | 59/240 = 25% (20%–30%) | 229/240 = 95% (92%–97%) | 0% |

### Sheet-jump recall by offset

| tool | 5.0 voxels | 10.0 voxels | 20.0 voxels | 40.0 voxels |
|---|---|---|---|---|
| tifxyz-doctor | 0/60 = 0% | 0/60 = 0% | 3/60 = 5% | 31/60 = 52% |
| tifxyz-repair | 49/60 = 82% | 53/60 = 88% | 60/60 = 100% | 60/60 = 100% |
| tifxyz-repair (winding-aware) | 0/60 = 0% | 11/60 = 18% | 57/60 = 95% | 60/60 = 100% |
| windcheck | 9/60 = 15% | 36/60 = 60% | 40/60 = 67% | 41/60 = 68% |

### Stretch recall by factor

| tool | 1.1 × | 1.25 × | 1.5 × | 2.0 × |
|---|---|---|---|---|
| tifxyz-doctor | 60/60 = 100% | 60/60 = 100% | 60/60 = 100% | 60/60 = 100% |
| tifxyz-repair | 51/60 = 85% | 60/60 = 100% | 60/60 = 100% | 60/60 = 100% |
| tifxyz-repair (winding-aware) | 7/60 = 12% | 60/60 = 100% | 60/60 = 100% | 60/60 = 100% |
| windcheck | 51/60 = 85% | 59/60 = 98% | 59/60 = 98% | 60/60 = 100% |

### Run health

| tool | tool runs | errors | median seconds per run |
|---|---|---|---|
| tifxyz-doctor | 80 | 0 | 1.3 |
| tifxyz-repair | 80 | 0 | 1.05 |
| tifxyz-repair (winding-aware) | 80 | 0 | 1.0 |
| windcheck | 80 | 0 | 0.72 |
