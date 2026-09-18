from __future__ import annotations

import io
import unittest
import zipfile

import numpy as np
from Bio import Phylo

from scripts.flowercolor_persistence_axis_v0_1 import (
    persistence_curve,
    summarize_tree_archive,
    tree_axis_diagnostics,
)


class PersistenceAxisTests(unittest.TestCase):
    def test_ultrametric_tree_is_classified_as_relative_time_axis(self):
        tree = Phylo.read(io.StringIO("((A:1,B:1):1,(C:1,D:1):1);"), "newick")
        d = tree_axis_diagnostics(tree)
        self.assertEqual(d["axis_class"], "RELATIVE_DIVERGENCE_TIME")
        self.assertAlmostEqual(d["root_to_tip_cv"], 0.0, places=12)
        self.assertAlmostEqual(d["tree_height"], 2.0, places=12)

    def test_non_ultrametric_tree_is_not_called_time(self):
        tree = Phylo.read(io.StringIO("((A:1,B:2):1,(C:1,D:1):1);"), "newick")
        d = tree_axis_diagnostics(tree)
        self.assertEqual(d["axis_class"], "NORMALIZED_PATRISTIC_DISTANCE")
        self.assertGreater(d["root_to_tip_cv"], 0.0)

    def test_persistence_curve_uses_state_frequency_baseline(self):
        distance = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9], dtype=float)
        same = np.array([1, 1, 1, 0, 0, 0], dtype=bool)
        rows = persistence_curve(distance, same, bins=np.array([0.0, 0.5, 1.0]))
        self.assertEqual(len(rows), 2)
        self.assertAlmostEqual(rows[0]["baseline_same_probability"], 0.5)
        self.assertAlmostEqual(rows[0]["same_probability"], 1.0)
        self.assertAlmostEqual(rows[0]["excess_same_probability"], 0.5)
        self.assertAlmostEqual(rows[1]["same_probability"], 0.0)
        self.assertAlmostEqual(rows[1]["excess_same_probability"], -0.5)

    def test_tree_archive_summary_keeps_time_label_only_for_ultrametric_members(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("Ultra.tre", "((A:1,B:1):1,(C:1,D:1):1);")
            zf.writestr("NonUltra.tre", "((A:1,B:2):1,(C:1,D:1):1);")
        s = summarize_tree_archive(buf.getvalue())
        self.assertEqual(s["tree_count"], 2)
        self.assertEqual(s["relative_time_tree_count"], 1)
        self.assertEqual(s["normalized_patristic_tree_count"], 1)
        self.assertEqual(s["members"]["Ultra.tre"]["axis_class"], "RELATIVE_DIVERGENCE_TIME")
        self.assertEqual(s["members"]["NonUltra.tre"]["axis_class"], "NORMALIZED_PATRISTIC_DISTANCE")


if __name__ == "__main__":
    unittest.main()
