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


def canonical_taxon(label: str) -> str:
    s = clean(normalize_hybrid_marker(label))
    low = s.lower()
    if low.startswith("synthetic "):
        s = s[len("synthetic "):].strip()
    # Non-Nicotiana synthetic shorthand and TH32 are retained verbatim; they are
    # source-designated hybrids and are used only to audit the exclusion map.
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
    h1 = s1[0]
    h2 = s2[0]
    h4 = s4[0]
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
    labels1 = [r[0] for r in r1]
    labels2 = [r[0] for r in r2]
    if labels1 != labels2:
        mismatches = [(i + 2, a, b) for i, (a, b) in enumerate(zip(labels1, labels2)) if a != b]
        raise SystemExit(f"S1/S2 positional identity mismatch: {mismatches[:10]}")
    if len(labels1) != len(set(labels1)):
        raise SystemExit("duplicate accession/morph labels in S1")

    hybrid_raw = [r[0] for r in r4]
    hybrid_taxa = {canonical_taxon(x) for x in hybrid_raw}

    fine_raw = sorted(set(clean(r[1]).lower().replace("–", "-").replace("—", "-") for r in r2))
    unknown_fine = sorted(set(fine_raw) - set(FINE_MAP))
    if unknown_fine:
        raise SystemExit(f"HOLD_SCHEMA unknown spectral categories: {unknown_fine}")
    coarse_raw = sorted(set(clean(r[4]).lower() for r in r2))
    if set(coarse_raw) - {"yes", "no"}:
        raise SystemExit(f"HOLD_SCHEMA unknown source petal coarse states: {coarse_raw}")

    rows = []
    by_taxon = defaultdict(lambda: {"fine": set(), "coarse": set(), "source_labels": [], "sections": set(), "ploidies": set()})
    for a, b in zip(r1, r2):
        label = a[0]
        taxon = canonical_taxon(label)
        ploidy = clean(a[2]).lower()
        fine_key = clean(b[1]).lower().replace("–", "-").replace("—", "-")
        fine = FINE_MAP[fine_key]
        # The supplement labels this yes/no field "Presence of chloroplasts in petals";
        # the article methods/ASR describe the same recorded floral axis as
        # presence/absence of chlorophyll. Preserve both terms explicitly.
        coarse = "CHLOROPHYLL_PRESENT" if clean(b[4]).lower() == "yes" else "CHLOROPHYLL_ABSENT"
        in_hybrid_table = taxon in hybrid_taxa
        eligible = ploidy == "diploid" and not in_hybrid_table
        row = {
            "source_label": label,
            "canonical_taxon": taxon,
            "section": a[1],
            "ploidy": ploidy,
            "fine_state": fine,
            "source_petals_field": b[4],
            "coarse_state": coarse,
            "in_S4_hybrid_origin_table": in_hybrid_table,
            "eligible_nonhybrid_diploid": eligible,
        }
        rows.append(row)
        if eligible:
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
        "s1_s2_positional_identity": True,
        "ploidy_counts_accession_rows": dict(Counter(r["ploidy"] for r in rows)),
        "hybrid_table_raw_labels": hybrid_raw,
        "hybrid_table_canonical_taxa": sorted(hybrid_taxa),
        "fine_source_categories": fine_raw,
        "coarse_source_values": coarse_raw,
        "eligible_accession_rows": sum(r["eligible_nonhybrid_diploid"] for r in rows),
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
    }
    OUT.write_text(json.dumps({"summary": summary, "accession_rows": rows}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("NICOTIANA_TRAIT_AUDIT=" + json.dumps(summary, ensure_ascii=False))
    if not all(summary["pre_tree_admission_checks"].values()):
        raise SystemExit("pre-tree trait admission gate failed")


if __name__ == "__main__":
    main()
