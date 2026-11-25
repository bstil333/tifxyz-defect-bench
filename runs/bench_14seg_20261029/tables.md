Segments: 14 · seeds per segment: 10 · severity levels: 4 · defects per kind per case: 3 · hit tolerance: 2 cells

### False alarms on the clean segments

| tool | flagged cells | valid cells | per 1,000 valid cells | chance of a flag landing in any defect-sized neighborhood |
|---|---|---|---|---|
| tifxyz-doctor | 25,194 | 3,981,098 | 6.33 | 92% |
| tifxyz-repair | 118,561 | 3,981,098 | 29.78 | 100% |
| tifxyz-repair (winding-aware) | 43,851 | 3,981,098 | 11.01 | 99% |
| windcheck | 1,884 | 3,981,098 | 0.47 | 17% |

### Recall by defect kind (found / planted, 95% interval) against chance

| tool | hole | sheet_jump | normal_flip | stretch | chance |
|---|---|---|---|---|---|
| tifxyz-doctor | 1640/1680 = 98% (97%–98%) | 168/1680 = 10% (9%–12%) | 1680/1680 = 100% (100%–100%) | 1648/1680 = 98% (97%–99%) | 92% |
| tifxyz-repair | 1680/1680 = 100% (100%–100%) | 1077/1680 = 64% (62%–66%) | 1680/1680 = 100% (100%–100%) | 1397/1680 = 83% (81%–85%) | 100% |
| tifxyz-repair (winding-aware) | 1680/1680 = 100% (100%–100%) | 925/1680 = 55% (53%–57%) | 1680/1680 = 100% (100%–100%) | 1326/1680 = 79% (77%–81%) | 99% |
| windcheck | 136/1680 = 8% (7%–9%) | 361/1680 = 21% (20%–24%) | 320/1680 = 19% (17%–21%) | 1460/1680 = 87% (85%–88%) | 17% |

### Sheet-jump recall by offset

| tool | 5.0 voxels | 10.0 voxels | 20.0 voxels | 40.0 voxels |
|---|---|---|---|---|
| tifxyz-doctor | 20/420 = 5% | 21/420 = 5% | 35/420 = 8% | 92/420 = 22% |
| tifxyz-repair | 127/420 = 30% | 147/420 = 35% | 383/420 = 91% | 420/420 = 100% |
| tifxyz-repair (winding-aware) | 46/420 = 11% | 79/420 = 19% | 380/420 = 90% | 420/420 = 100% |
| windcheck | 52/420 = 12% | 85/420 = 20% | 105/420 = 25% | 119/420 = 28% |

### Stretch recall by factor

| tool | 1.1 × | 1.25 × | 1.5 × | 2.0 × |
|---|---|---|---|---|
| tifxyz-doctor | 389/420 = 93% | 420/420 = 100% | 419/420 = 100% | 420/420 = 100% |
| tifxyz-repair | 137/420 = 33% | 420/420 = 100% | 420/420 = 100% | 420/420 = 100% |
| tifxyz-repair (winding-aware) | 66/420 = 16% | 420/420 = 100% | 420/420 = 100% | 420/420 = 100% |
| windcheck | 294/420 = 70% | 387/420 = 92% | 390/420 = 93% | 389/420 = 93% |

### Run health

| tool | tool runs | errors | median seconds per run |
|---|---|---|---|
| tifxyz-doctor | 560 | 0 | 2.72 |
| tifxyz-repair | 560 | 0 | 1.39 |
| tifxyz-repair (winding-aware) | 560 | 0 | 1.39 |
| windcheck | 560 | 0 | 1.14 |
