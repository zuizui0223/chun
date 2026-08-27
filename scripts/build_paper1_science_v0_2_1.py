#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one source block, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    text = args.source.read_text(encoding="utf-8")

    banner_old = "> Draft v0.2. This manuscript is governed by `data/paper1_authoritative_results_v0_2.csv`, `data/paper1_main_figure_manifest_v0_2.csv`, and `data/paper1_reference_registry_v0_2.csv`. The v0.1 manuscript is retained as provenance and must not be patched back into the molecular framing when it conflicts with the v0.2 result hierarchy."
    banner_new = "> Draft v0.2.1. The Paper 1 v0.2 biological results are retained except for the literature-ascertainment layer reopened by the 2026-08-27 formal database search. This manuscript is governed by `data/paper1_authoritative_results_v0_2_1.csv`, `data/paper1_main_figure_manifest_v0_2_1.csv`, and `data/paper1_reference_registry_v0_2_1.csv`. The five-system candidate-free recurrence and macroevolutionary results remain unchanged."
    text = replace_once(text, banner_old, banner_new, "governance banner")

    registry_old = "The current result set is frozen in `data/paper1_authoritative_results_v0_2.csv`; Main and Supplement figure roles are frozen in `data/paper1_main_figure_manifest_v0_2.csv`. Superseded analyses remain in repository history but do not re-enter positive claims."
    registry_new = "The current result set is frozen in `data/paper1_authoritative_results_v0_2_1.csv`; Main and Supplement figure roles are frozen in `data/paper1_main_figure_manifest_v0_2_1.csv`. This patch changes the literature-ascertainment layer only; superseded analyses remain in repository history and do not re-enter positive claims."
    text = replace_once(text, registry_old, registry_new, "registry sentence")

    ascertain_old = "We first quantified axis ascertainment. Across biological systems, published coverage was A/F/C/P = 8/4/1/3. We evaluated whether anthocyanin coverage exceeded an axis-symmetric observation process while conditioning on the exact number of axes measured in each system. The exact conditional enumeration included all assignments preserving per-system measurement counts. We also repeated the comparison after dependence collapse."
    ascertain_new = "We first quantified axis ascertainment. After the initial evidence matrix had been frozen, a reproducible OpenAlex/Crossref/PubMed audit on 27 August 2026 recovered an additional independent red-versus-white petal transcriptomic system, *Camellia semiserrata* (Jiang et al., 2025). Under the pre-existing white-to-red orientation, this study resolved A as up; F, C, and P remained unresolved, and no public raw RNA-seq accession was located, so it entered the literature observation matrix but not the candidate-free arm. The updated literature matrix contained 11 biological systems with A/F/C/P coverage = 9/4/1/3 and six dependence clusters with coverage = 5/3/1/2. We evaluated whether anthocyanin coverage exceeded an axis-symmetric observation process while conditioning on the exact number of axes measured in each system or dependence cluster. Exact conditional enumeration preserved the resolved-axis count of every row."
    text = replace_once(text, ascertain_old, ascertain_new, "ascertainment methods")

    result_old = "The published mechanism matrix measured pigment axes unevenly. Across biological systems, A/F/C/P coverage was 8/4/1/3. Conditional on the exact number of axes measured per system, the exact probability of anthocyanin coverage at least as enriched as observed was 0.00836; the probability of any axis imbalance at least as extreme was 0.02395. After dependence collapse, the anthocyanin-enrichment probability weakened to 0.140625. Thus the literature clearly contains a nonuniform observation process at the biological-system level, but the amount attributable to repeated sampling of the same evolutionary backgrounds is non-negligible."
    result_new = "The formal database-expanded mechanism matrix measured pigment axes unevenly. Across 11 biological systems, A/F/C/P coverage was 9/4/1/3. Conditional on the exact number of axes measured per system, the exact probability of anthocyanin coverage at least as enriched as observed was 0.00278854; the probability of any axis imbalance at least as extreme was 0.00860765. After dependence collapse to six independent backgrounds, coverage was 5/3/1/2 and the anthocyanin-enrichment probability was 0.046875, while the general maximum-minus-minimum imbalance test was 0.145833. The newly recovered *C. semiserrata* system therefore strengthened rather than erased the anthocyanin-heavy ascertainment result. Importantly, its absence from the public-raw candidate-free arm means that this expansion updates the observation-process estimate without changing the matched five-system recurrence comparison."
    text = replace_once(text, result_old, result_new, "ascertainment results")

    discussion_old = "The comparison is not a test of whether candidate-gene papers are “right” or “wrong.” Candidate-selected studies often ask targeted biological questions and can resolve specific causal nodes more precisely than a broad module score. The candidate-free protocol asks a different question: if the same systems are measured with one outcome-independent pathway-wide representation, what multivariate recurrence remains identifiable?"
    discussion_new = "The comparison is not a test of whether candidate-gene papers are “right” or “wrong.” Candidate-selected studies often ask targeted biological questions and can resolve specific causal nodes more precisely than a broad module score. The candidate-free protocol asks a different question: if the same systems are measured with one outcome-independent pathway-wide representation, what multivariate recurrence remains identifiable? The formal database expansion provides an additional robustness check on the observation layer: adding an independent *C. semiserrata* red/white transcriptomic system increased A-axis coverage and made anthocyanin enrichment detectable even after dependence collapse, yet the study could not be added to the standardized arm without auditable public raw reads. Broader literature coverage therefore strengthened the ascertainment diagnosis while leaving the matched candidate-free recurrence estimator unchanged."
    text = replace_once(text, discussion_old, discussion_new, "observation discussion")

    availability_old = "The current manuscript consumes `data/paper1_authoritative_results_v0_2.csv`, `data/paper1_main_figure_manifest_v0_2.csv`, and `data/paper1_reference_registry_v0_2.csv`."
    availability_new = "The current scientific manuscript consumes `data/paper1_authoritative_results_v0_2_1.csv`, `data/paper1_main_figure_manifest_v0_2_1.csv`, and `data/paper1_reference_registry_v0_2_1.csv`. The formal bibliographic search is frozen in run `33039509237`, and the updated literature-ascertainment calculation is frozen in run `33040242009`."
    text = replace_once(text, availability_old, availability_new, "data availability")

    fan_ref = "Fan, M., H. Jiang, Y. Qu, Y. Zhang, X. Li, and Y. Wang. 2026. Transposable element-mediated structural variation drives flower colour diversification in *Camellia*. *Plant Biotechnology Journal* 24: 1725–1739. https://doi.org/10.1111/pbi.70442"
    jiang_ref = "Jiang, H., et al. 2025. Integration of transcriptomic and chemical analysis reveals key regulatory mechanisms involved in color variation between red and white flowers of *Camellia semiserrata*. *Genetic Resources and Crop Evolution* 72(Suppl 1): 333–352. https://doi.org/10.1007/s10722-025-02606-6"
    text = replace_once(text, fan_ref, fan_ref + "\n\n" + jiang_ref, "Jiang reference insertion")

    required_new = [
        "A/F/C/P coverage = 9/4/1/3",
        "coverage was 5/3/1/2",
        "0.00278854",
        "0.046875",
        "10.1007/s10722-025-02606-6",
        "run `33040242009`",
    ]
    missing_new = [token for token in required_new if token not in text]
    if missing_new:
        raise SystemExit(f"missing v0.2.1 ascertainment tokens: {missing_new}")

    frozen_tokens = [
        "Candidate-free remeasurement fixed exact-signature recurrence at 0.333",
        "Candidate-free measurement point-identified exact-signature recurrence at **0.5** and pairwise concordance at **0.75**",
        "46 of 50 nontrivial splits were shared and normalized RF distance was 0.08",
        "strict P=0.00116 and dominant P=0.000080",
        "The strict×dominant shared robust event count was therefore zero",
        "Repeated flower-colour change in *Camellia* does not imply repetition of one complete A/F/C/P pigment-state package.",
    ]
    missing_frozen = [token for token in frozen_tokens if token not in text]
    if missing_frozen:
        raise SystemExit(f"v0.2.1 patch lost frozen Paper 1 science tokens: {missing_frozen}")

    forbidden_old = [
        "published coverage was A/F/C/P = 8/4/1/3",
        "anthocyanin-enrichment probability weakened to 0.140625",
        "paper1_authoritative_results_v0_2.csv`; Main and Supplement figure roles are frozen in `data/paper1_main_figure_manifest_v0_2.csv",
    ]
    retained_old = [token for token in forbidden_old if token in text]
    if retained_old:
        raise SystemExit(f"v0.2.1 patch retains superseded ascertainment tokens: {retained_old}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text.rstrip() + "\n", encoding="utf-8")
    summary = {
        "document_version": "Paper 1 science v0.2.1",
        "source": str(args.source),
        "change_scope": "literature ascertainment only",
        "new_literature_cluster": "CSEMISERRATA",
        "candidate_free_systems_changed": False,
        "candidate_free_recurrence_changed": False,
        "macro_results_changed": False,
        "frozen_science_tokens_preserved": len(frozen_tokens),
        "reference_count_before_novelty_framing": 16,
        "status": "science v0.2.1 manuscript generated",
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
