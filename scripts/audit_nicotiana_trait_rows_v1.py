#!/usr/bin/env python3
"""Audit the prefrozen Nicotiana eligibility/fine/coarse trait schema; no phylogenetic signal is computed."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path("analysis/_generated/nicotiana_source_v1")
OUT = BASE / "trait_audit.json"

FINE_MAP = {
    "magenta": "MAGENTA",
    "red": "RED",
    "pink": "PINK",
    "uv-white": "UV_WHITE",
    "white": "WHITE",
    "yellow": "YELLOW",
    "green": "GREEN",
    "dark green": "DARK_GREEN",
}
RANKS = {"subsp.", "ssp.", "var.", "f."}


def clean(x: str) -> str:
    return re.sub(r"\s+", " ", x or "").strip()


def read_tsv(path: Path):
    return [[clean(v) for v in line.rstrip("\n").split("\t")] for line in path.read_text(encoding="utf-8").splitlines()]


def normalize_hybrid_marker(s: str) -> str:
    return s.replace("×", "x").replace("✕", "x")


def reconcile_s1_s2_label(s1_label: str, s2_label: str):
    """Allow only source-footnote removal when reconciling positional S1/S2 labels."""
    a = clean(s1_label)
    b = clean(s2_label)
    if a == b:
        return b, "NONE"
    candidate = a
    edits = []
    if candidate.endswith("**"):
        candidate = candidate[:-2].rstrip()
        edits.append("TRAILING_DOUBLE_ASTERISK_FOOTNOTE")
    candidate2 = re.sub(r"(?<=[A-Za-z])b$", "", candidate)
    if candidate2 != candidate:
        candidate = candidate2
        edits.append("TRAILING_B_FOOTNOTE")
    if candidate == b and edits:
        return b, "+".join(edits)
    raise ValueError(f"non-footnote S1/S2 label mismatch: {a!r} != {b!r}; normalized S1={candidate!r}")


def canonical_taxon(label: str) -> str:
    s = clean(normalize_hybrid_marker(label))
    low = s.lower()
    if low.startswith("synthetic "):
        s = s[len("synthetic "):].strip()
    if not (s.startswith("N. ") or s.startswith("Nicotiana ")):
        return s
    if s.startswith("N. "):
        s = "Nicotiana " + s[3:]
    toks = s.split()
    if len(toks) < 2:
        raise ValueError(f"unparsable Nicotiana label: {label}")
    base = ["Nicotiana"]
    j = 1
    if toks[j].lower() == "x":
        base.append("x")
        j += 1
        if j >= len(toks):
            raise ValueError(f"hybrid label lacks epithet: {label}")
    base.append(toks[j].strip("'‘’\""))
    j += 1
    if j + 1 < len(toks) and toks[j].lower() in RANKS:
        base.extend([toks[j].lower(), toks[j + 1].strip("'‘’\"")])
    return " ".join(base)


def main():
    s1 = read_tsv(BASE / "table_00.tsv")
    s2 = read_tsv(BASE / "table_01.tsv")
    s4 = read_tsv(BASE / "table_03.tsv")
    h1, h2, h4 = s1[0], s2[0], s4[0]
    expected1 = ["Species", "Section", "Ploidy", "No. of flowersa", "No. of plants"]
    expected2 = ["Species", "Spectral reflectance colour", "Bee colour", "Hummingbird colour", "Presence of chloroplasts in petals"]
    expected4 = ["Hybrid", "Maternal Progenitor", "Paternal Progenitor", "Age (millions of years)"]
    if h1 != expected1:
        raise SystemExit(f"S1 header drift: {h1}")
    if h2 != expected2:
        raise SystemExit(f"S2 header drift: {h2}")
    if h4 != expected4:
        raise SystemExit(f"S4 header drift: {h4}")

    r1 = [row for row in s1[1:] if any(row)]
    r2 = [row for row in s2[1:] if any(row)]
    r4 = [row for row in s4[1:] if any(row)]
    if len(r1) != len(r2):
        raise SystemExit(f"S1/S2 row count mismatch: {len(r1)} vs {len(r2)}")

    reconciled = []
    reconciliation_counts = Counter()
    reconciliation_examples = []
    for source_row, (a, b) in enumerate(zip(r1, r2), start=2):
        try:
            label, mode = reconcile_s1_s2_label(a[0], b[0])
        except ValueError as e:
            raise SystemExit(f"S1/S2 positional identity failure at row {source_row}: {e}")
        reconciled.append(label)
        reconciliation_counts[mode] += 1
        if mode != "NONE":
            reconciliation_examples.append({"row": source_row, "S1": a[0], "S2": b[0], "mode": mode})
    if len(reconciled) != len(set(reconciled)):
        dup = [x for x, n in Counter(reconciled).items() if n > 1]
        raise SystemExit(f"duplicate accession/morph labels after footnote-only reconciliation: {dup}")

    hybrid_raw = [r[0] for r in r4]
    hybrid_taxa = {canonical_taxon(x) for x in hybrid_raw}

    fine_raw_all = [clean(r[1]).lower().replace("–", "-").replace("—", "-") for r in r2]
    fine_raw_nonempty = sorted(set(x for x in fine_raw_all if x))
    unknown_fine = sorted(set(fine_raw_nonempty) - set(FINE_MAP))
    if unknown_fine:
        raise SystemExit(f"HOLD_SCHEMA unknown non-empty spectral categories: {unknown_fine}")
    coarse_raw_all = [clean(r[4]).lower() for r in r2]
    coarse_raw_nonempty = sorted(set(x for x in coarse_raw_all if x))
    if set(coarse_raw_nonempty) - {"yes", "no"}:
        raise SystemExit(f"HOLD_SCHEMA unknown non-empty source petal coarse states: {coarse_raw_nonempty}")

    rows = []
    by_taxon = defaultdict(lambda: {"fine": set(), "coarse": set(), "source_labels": [], "sections": set(), "ploidies": set()})
    structurally_eligible_taxa = set()
    joint_missing_rows = []
    for source_row, (a, b, label) in enumerate(zip(r1, r2, reconciled), start=2):
        taxon = canonical_taxon(label)
        ploidy = clean(a[2]).lower()
        fine_key = clean(b[1]).lower().replace("–", "-").replace("—", "-")
        coarse_key = clean(b[4]).lower()
        fine = FINE_MAP[fine_key] if fine_key else None
        coarse = (
            "CHLOROPHYLL_PRESENT" if coarse_key == "yes" else
            "CHLOROPHYLL_ABSENT" if coarse_key == "no" else
            None
        )
        in_hybrid_table = taxon in hybrid_taxa
        structural_eligible = ploidy == "diploid" and not in_hybrid_table
        joint_trait_observed = fine is not None and coarse is not None
        joint_eligible = structural_eligible and joint_trait_observed
        if structural_eligible:
            structurally_eligible_taxa.add(taxon)
        if structural_eligible and not joint_trait_observed:
            joint_missing_rows.append({
                "source_row": source_row,
                "source_label": label,
                "taxon": taxon,
                "missing_fine": fine is None,
                "missing_coarse": coarse is None,
            })
        row = {
            "source_row": source_row,
            "source_label_S1": a[0],
            "source_label_S2": b[0],
            "reconciled_source_label": label,
            "canonical_taxon": taxon,
            "section": a[1],
            "ploidy": ploidy,
            "fine_state": fine,
            "source_petals_field": b[4],
            "coarse_state": coarse,
            "in_S4_hybrid_origin_table": in_hybrid_table,
            "structurally_eligible_nonhybrid_diploid": structural_eligible,
            "joint_fine_coarse_observed": joint_trait_observed,
            "joint_trait_eligible": joint_eligible,
        }
        rows.append(row)
        # The frozen analysis population is the joint observation regime: a
        # source row must provide both fine spectral category and coarse petal
        # chlorophyll/chloroplast state. Missing coarse values are never inferred
        # from visible colour.
        if joint_eligible:
            x = by_taxon[taxon]
            x["fine"].add(fine)
            x["coarse"].add(coarse)
            x["source_labels"].append(label)
            x["sections"].add(a[1])
            x["ploidies"].add(ploidy)

    taxa = []
    for taxon in sorted(by_taxon):
        x = by_taxon[taxon]
        taxa.append({
            "taxon": taxon,
            "fine_states": sorted(x["fine"]),
            "coarse_states": sorted(x["coarse"]),
            "source_labels": x["source_labels"],
            "sections": sorted(x["sections"]),
            "ploidies": sorted(x["ploidies"]),
        })

    coarse_groups = Counter("|".join(t["coarse_states"]) for t in taxa)
    fine_presence = Counter()
    fine_by_definite_coarse = defaultdict(set)
    definite_coarse_n = Counter()
    for t in taxa:
        for s in t["fine_states"]:
            fine_presence[s] += 1
        if len(t["coarse_states"]) == 1:
            c = t["coarse_states"][0]
            definite_coarse_n[c] += 1
            fine_by_definite_coarse[c].update(t["fine_states"])

    summary = {
        "source_doi": "10.1093/aob/mcv048",
        "source_tables": {
            "S1": {"table_index": 0, "rows_excluding_header": len(r1), "header": h1},
            "S2": {"table_index": 1, "rows_excluding_header": len(r2), "header": h2},
            "S4": {"table_index": 3, "rows_excluding_header": len(r4), "header": h4},
        },
        "s1_s2_positional_identity_after_source_footnote_normalization": True,
        "s1_s2_label_reconciliation_counts": dict(reconciliation_counts),
        "s1_s2_label_reconciliation_examples": reconciliation_examples,
        "ploidy_counts_accession_rows": dict(Counter(r["ploidy"] for r in rows)),
        "hybrid_table_raw_labels": hybrid_raw,
        "hybrid_table_canonical_taxa": sorted(hybrid_taxa),
        "fine_source_categories_nonempty": fine_raw_nonempty,
        "fine_missing_source_rows": sum(x == "" for x in fine_raw_all),
        "coarse_source_values_nonempty": coarse_raw_nonempty,
        "coarse_missing_source_rows": sum(x == "" for x in coarse_raw_all),
        "structurally_eligible_nonhybrid_diploid_taxa": len(structurally_eligible_taxa),
        "structurally_eligible_rows_missing_joint_trait": joint_missing_rows,
        "joint_trait_eligible_accession_rows": sum(r["joint_trait_eligible"] for r in rows),
        "eligible_taxon_units": len(taxa),
        "eligible_taxa": taxa,
        "fine_state_taxon_presence": dict(sorted(fine_presence.items())),
        "coarse_allowed_set_counts": dict(sorted(coarse_groups.items())),
        "definite_coarse_taxon_counts": dict(sorted(definite_coarse_n.items())),
        "fine_states_within_definite_coarse": {k: sorted(v) for k, v in sorted(fine_by_definite_coarse.items())},
        "multi_fine_taxa": sum(len(t["fine_states"]) > 1 for t in taxa),
        "multi_coarse_taxa": sum(len(t["coarse_states"]) > 1 for t in taxa),
        "pre_tree_admission_checks": {
            "eligible_taxa_ge_20": len(taxa) >= 20,
            "both_definite_coarse_classes_ge_5": all(definite_coarse_n[c] >= 5 for c in ("CHLOROPHYLL_PRESENT", "CHLOROPHYLL_ABSENT")),
            "one_definite_coarse_class_ge_10_and_ge_3_fine": any(definite_coarse_n[c] >= 10 and len(fine_by_definite_coarse[c]) >= 3 for c in definite_coarse_n),
        },
        "field_terminology_note": "Supplement S2 header is 'Presence of chloroplasts in petals'; article Methods/Fig. S6 describe the analysed biological axis as presence/absence of chlorophyll in corolla tissue. No state is inferred from visible colour.",
        "missingness_rule": "Only non-hybrid diploid source rows with both an explicit spectral category and explicit yes/no petal coarse state enter taxon-level allowed-state sets. Empty source fields are missing, never inferred. Unknown non-empty codes remain schema failures.",
        "identity_normalization_boundary": "Only S1 trailing ** and attached final footnote b are removed, and only when the resulting S1 string exactly equals the positional S2 identifier. No taxon/accession/morph token is otherwise altered.",
    }
    OUT.write_text(json.dumps({"summary": summary, "accession_rows": rows}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("NICOTIANA_TRAIT_AUDIT=" + json.dumps(summary, ensure_ascii=False))
    if not all(summary["pre_tree_admission_checks"].values()):
        raise SystemExit("pre-tree trait admission gate failed")


if __name__ == "__main__":
    main()
