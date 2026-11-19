import os, sys, unittest, glob
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tdbench import tifxyz_io as io
from tdbench.inject import inject, KINDS
from tdbench.score import score

DATA = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "..", "data", "*")))


class InjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seg = io.load(DATA[0])
        cls.bad, cls.defects = inject(cls.seg, KINDS, per_kind=2, seed=3)

    def test_all_kinds_planted(self):
        self.assertEqual({d.kind for d in self.defects}, set(KINDS))
        self.assertEqual(len(self.defects), 8)

    def test_blocks_do_not_overlap(self):
        g = np.zeros(self.seg["x"].shape, int)
        for d in self.defects:
            g[d.r0:d.r1, d.c0:d.c1] += 1
        self.assertEqual(g.max(), 1)

    def test_changes_are_confined_to_planted_blocks(self):
        changed = np.zeros(self.seg["x"].shape, bool)
        for a in "xyz":
            changed |= self.bad[a] != self.seg[a]
        inside = np.zeros_like(changed)
        for d in self.defects:
            inside[d.r0:d.r1, d.c0:d.c1] = True
        self.assertFalse((changed & ~inside).any())

    def test_hole_is_invalid_and_jump_is_offset(self):
        for d in self.defects:
            sl = (slice(d.r0, d.r1), slice(d.c0, d.c1))
            if d.kind == "hole":
                self.assertTrue((self.bad["x"][sl] == -1).all())
            if d.kind == "sheet_jump":
                step = np.linalg.norm(np.stack([self.bad[a][sl] - self.seg[a][sl] for a in "xyz"], -1), axis=-1)
                self.assertTrue(np.allclose(step, d.params["offset_vox"], atol=1e-2))
            if d.kind == "stretch":
                self.assertEqual(d.params["factor"], 2.0)

    def test_flip_reverses_rows(self):
        for d in self.defects:
            if d.kind == "normal_flip":
                sl = (slice(d.r0, d.r1), slice(d.c0, d.c1))
                self.assertTrue(np.array_equal(self.bad["x"][sl], self.seg["x"][sl][::-1]))

    def test_deterministic(self):
        _, again = inject(self.seg, KINDS, per_kind=2, seed=3)
        self.assertEqual([d.to_json() for d in again], [d.to_json() for d in self.defects])

    def test_scoring_perfect_and_empty_detector(self):
        H, W = self.seg["x"].shape
        truth = [d.to_json() for d in self.defects]
        perfect = np.zeros((H, W), bool)
        for d in self.defects:
            perfect[d.r0:d.r1, d.c0:d.c1] = True
        v = io.valid_mask(self.seg)
        s = score(perfect, truth, np.zeros((H, W), bool), v)
        self.assertTrue(all(k["recall"] == 1.0 for k in s["by_kind"].values()))
        self.assertEqual(s["false_positive_per_1000_cells"], 0.0)
        s0 = score(np.zeros((H, W), bool), truth, np.ones((H, W), bool), v)
        self.assertTrue(all(k["recall"] == 0.0 for k in s0["by_kind"].values()))
        self.assertGreater(s0["false_positive_per_1000_cells"], 900)


if __name__ == "__main__":
    unittest.main()
