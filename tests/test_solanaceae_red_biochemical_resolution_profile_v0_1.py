#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_solanaceae_red_biochemical_resolution_profile_v0_1.py"

spec = importlib.util.spec_from_file_location("solanaceae_red_profile", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"missing production runner: {SCRIPT}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class SolanaceaeRedBiochemicalProfileTests(unittest.TestCase):
    def test_numeric_proportion_presence_rule_is_strictly_greater_than_zero(self):
        self.assertEqual(mod.parse_numeric_proportion("0"), 0.0)
        self.assertEqual(mod.parse_numeric_proportion("0.25"), 0.25)
        self.assertEqual(mod.parse_numeric_proportion("25%"), 25.0)
        self.assertEqual(mod.parse_numeric_proportion(" 12.5 "), 12.5)
        self.assertIsNone(mod.parse_numeric_proportion(""))
        self.assertIsNone(mod.parse_numeric_proportion("NA"))
        self.assertIsNone(mod.parse_numeric_proportion("trace"))

    def test_carotenoid_presence_accepts_only_explicit_binary_tokens(self):
        for token in ["present", "Present", "yes", "Y", "1", "+"]:
            self.assertTrue(mod.parse_carotenoid_presence(token), token)
        for token in ["absent", "Absent", "no", "N", "0", "-"]:
            self.assertFalse(mod.parse_carotenoid_presence(token), token)
        for token in ["", "NA", "unknown", "trace", "+/-"]:
            self.assertIsNone(mod.parse_carotenoid_presence(token), token)

    def test_nested_state_codes_follow_frozen_hierarchy(self):
        states = mod.state_codes(pel=1.0, cya=0.0, dele=2.0, carotenoid=True)
        self.assertEqual(states["fine"], "C1_P1_C0_D1")
        self.assertEqual(states["intermediate"], "C1_HDELPHINIDIN")
        self.assertEqual(states["coarse"], "A1_C1")

        none = mod.state_codes(pel=0.0, cya=0.0, dele=0.0, carotenoid=False)
        self.assertEqual(none["fine"], "C0_P0_C0_D0")
        self.assertEqual(none["intermediate"], "C0_HNONE")
        self.assertEqual(none["coarse"], "A0_C0")

    def test_common_frame_drops_rare_fine_states_before_all_resolutions(self):
        raw = {
            "a": {"coarse": "A1_C0", "intermediate": "C0_HPELARGONIDIN", "fine": "C0_P1_C0_D0"},
            "b": {"coarse": "A1_C0", "intermediate": "C0_HPELARGONIDIN", "fine": "C0_P1_C0_D0"},
            "c": {"coarse": "A1_C0", "intermediate": "C0_HPELARGONIDIN", "fine": "C0_P1_C0_D0"},
            "d": {"coarse": "A1_C0", "intermediate": "C0_HPELARGONIDIN", "fine": "C0_P1_C0_D0"},
            "e": {"coarse": "A1_C0", "intermediate": "C0_HPELARGONIDIN", "fine": "C0_P1_C0_D0"},
            "rare": {"coarse": "A1_C1", "intermediate": "C1_HCYANIDIN", "fine": "C1_P0_C1_D0"},
        }
        retained, rare = mod.common_frame(raw, minimum_fine_count=5)
        self.assertEqual(retained, ["a", "b", "c", "d", "e"])
        self.assertEqual(rare, ["C1_P0_C1_D0"])

    def test_two_row_source_header_finds_subcolumns_below_spanning_label(self):
        headers = [
            ["Species", "Anthocyanidin proportion", "", "", "Carotenoid presence"],
            ["", "Pelargonidin", "Cyanidin", "Delphinidin", ""],
        ]
        self.assertEqual(
            mod.required_column_map(headers, species_column_index=0),
            {"species": 0, "pelargonidin": 1, "cyanidin": 2, "delphinidin": 3, "carotenoid": 4},
        )

    def test_terminal_classification_matches_frozen_unique_winner_gate(self):
        self.assertEqual(
            mod.classify_terminal(aucs=[0.62, 0.58, 0.55], signal_p=[0.01, 0.02, 0.03], winner_vs_runner_p=0.01),
            "PROFILE_SIGNALLED_COARSE",
        )
        self.assertEqual(
            mod.classify_terminal(aucs=[0.55, 0.63, 0.59], signal_p=[0.01, 0.01, 0.01], winner_vs_runner_p=0.01),
            "PROFILE_SIGNALLED_INTERMEDIATE",
        )
        self.assertEqual(
            mod.classify_terminal(aucs=[0.55, 0.59, 0.67], signal_p=[0.01, 0.01, 0.01], winner_vs_runner_p=0.01),
            "PROFILE_SIGNALLED_FINE",
        )
        self.assertEqual(
            mod.classify_terminal(aucs=[0.49, 0.50, 0.48], signal_p=[0.01, 0.01, 0.01], winner_vs_runner_p=0.01),
            "PROFILE_NO_PHYLOGENETIC_SIGNAL",
        )
        self.assertEqual(
            mod.classify_terminal(aucs=[0.61, 0.60, 0.59], signal_p=[0.01, 0.01, 0.01], winner_vs_runner_p=0.20),
            "PROFILE_SIGNALLED_TIED",
        )


if __name__ == "__main__":
    unittest.main()
