#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected exactly one source block, found {n}")
    return text.replace(old, new, 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    base_builder = Path(__file__).with_name("build_paper1_science_v0_2_1.py")
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        v021 = td / "PAPER1_AJB_MANUSCRIPT_V0_2_1.md"
        v021_summary = td / "summary.json"
        subprocess.run([
            sys.executable, str(base_builder),
            "--source", str(args.source),
            "--out", str(v021),
            "--summary", str(v021_summary),
        ], check=True)
        text = v021.read_text(encoding="utf-8")

    banner_old = "> Draft v0.2.1. The Paper 1 v0.2 biological results are retained except for the literature-ascertainment layer reopened by the 2026-08-27 formal database search. This manuscript is governed by `data/paper1_authoritative_results_v0_2_1.csv`, `data/paper1_main_figure_manifest_v0_2_1.csv`, and `data/paper1_reference_registry_v0_2_1.csv`. The five-system candidate-free recurrence and macroevolutionary results remain unchanged."
    banner_new = "> Draft v0.2.2. The Paper 1 candidate-free and macroevolutionary results remain frozen. The literature-conditioned molecular layer was reopened after backward/forward citation chasing recovered Luo et al. (2016), which resolves the literature-side CJAPONICA F axis. This manuscript is governed by `data/paper1_authoritative_results_v0_2_2.csv`, `data/paper1_main_figure_manifest_v0_2_2.csv`, and `data/paper1_reference_registry_v0_2_2.csv`."
    text = replace_once(text, banner_old, banner_new, "governance banner")

    registry_old = "The current result set is frozen in `data/paper1_authoritative_results_v0_2_1.csv`; Main and Supplement figure roles are frozen in `data/paper1_main_figure_manifest_v0_2_1.csv`. This patch changes the literature-ascertainment layer only; superseded analyses remain in repository history and do not re-enter positive claims."
    registry_new = "The current result set is frozen in `data/paper1_authoritative_results_v0_2_2.csv`; Main and Supplement figure roles are frozen in `data/paper1_main_figure_manifest_v0_2_2.csv`. This patch changes only the literature-conditioned molecular layer after citation chasing; candidate-free measurements, yellow-development results and macroevolutionary inputs are unchanged."
    text = replace_once(text, registry_old, registry_new, "registry sentence")

    methods_old = "We first quantified axis ascertainment. After the initial evidence matrix had been frozen, a reproducible OpenAlex/Crossref/PubMed audit on 27 August 2026 recovered an additional independent red-versus-white petal transcriptomic system, *Camellia semiserrata* (Jiang et al., 2025). Under the pre-existing white-to-red orientation, this study resolved A as up; F, C, and P remained unresolved, and no public raw RNA-seq accession was located, so it entered the literature observation matrix but not the candidate-free arm. The updated literature matrix contained 11 biological systems with A/F/C/P coverage = 9/4/1/3 and six dependence clusters with coverage = 5/3/1/2. We evaluated whether anthocyanin coverage exceeded an axis-symmetric observation process while conditioning on the exact number of axes measured in each system or dependence cluster. Exact conditional enumeration preserved the resolved-axis count of every row."
    methods_new = "We first quantified axis ascertainment. A reproducible OpenAlex/Crossref/PubMed audit recovered an additional independent red-versus-white *Camellia semiserrata* system (Jiang et al., 2025), and subsequent backward/forward citation chasing recovered Luo et al. (2016), a cross-plant red/white comparison that resolves *C. japonica* DFR and FLS expression. Under the pre-existing white-to-red orientation, Luo resolves literature-side CJAPONICA A as up and F as down; C and P remain unresolved. Luo is an additional observation within the existing CJAPONICA dependence background and does not add a candidate-free dataset. The resulting literature matrix contained 12 biological systems with A/F/C/P coverage = 10/5/1/3 and six dependence clusters with coverage = 5/4/1/2. We evaluated axis ascertainment while conditioning on the exact number of axes resolved in each system or dependence cluster; exact conditional enumeration preserved every row's resolved-axis count."
    text = replace_once(text, methods_old, methods_new, "ascertainment methods")

    result_old = "The formal database-expanded mechanism matrix measured pigment axes unevenly. Across 11 biological systems, A/F/C/P coverage was 9/4/1/3. Conditional on the exact number of axes measured per system, the exact probability of anthocyanin coverage at least as enriched as observed was 0.00278854; the probability of any axis imbalance at least as extreme was 0.00860765. After dependence collapse to six independent backgrounds, coverage was 5/3/1/2 and the anthocyanin-enrichment probability was 0.046875, while the general maximum-minus-minimum imbalance test was 0.145833. The newly recovered *C. semiserrata* system therefore strengthened rather than erased the anthocyanin-heavy ascertainment result. Importantly, its absence from the public-raw candidate-free arm means that this expansion updates the observation-process estimate without changing the matched five-system recurrence comparison."
    result_new = "The expanded mechanism matrix measured pigment axes unevenly across published biological systems. Across 12 systems, A/F/C/P coverage was 10/5/1/3. Conditional on the resolved-axis count of each system, exact P was 0.00152779 for A-axis enrichment and 0.00351480 for an axis imbalance at least as large as observed. After dependence collapse to six evolutionary backgrounds, coverage was 5/4/1/2; A-specific enrichment weakened to P=0.078125 and the general axis-imbalance test to P=0.173611. Thus published observation is clearly nonuniform at the system level, but the stronger claim that anthocyanin-specific ascertainment remains detectable below 0.05 after dependence collapse is not retained. This makes the standardized same-system recurrence comparison, rather than an ascertainment-significance claim, the primary molecular result."
    text = replace_once(text, result_old, result_new, "ascertainment results")

    abstract_old = "For anthocyanin gain, literature exact-signature recurrence ranged from 0.333 to 1.0 and pairwise A/F/C/P concordance from 0.25 to 1.0. Candidate-free remeasurement fixed exact-signature recurrence at 0.333 and narrowed pairwise concordance to 0.333–0.5."
    abstract_new = "For anthocyanin gain, literature exact-signature recurrence ranged from 0.333 to 1.0 and pairwise A/F/C/P concordance from 0.333 to 1.0. Candidate-free remeasurement fixed exact-signature recurrence at 0.333 and narrowed pairwise concordance to 0.333–0.5."
    text = replace_once(text, abstract_old, abstract_new, "abstract anthocyanin bounds")

    anth_old = "On these same three clusters, selected literature left exact-signature recurrence at 0.333–1.0 and pairwise A/F/C/P concordance at 0.25–1.0. Candidate-free remeasurement reduced exact-signature recurrence to **0.333 exactly** and pairwise concordance to **0.333–0.5**. Pairwise identified-set width contracted from 0.75 to 0.1667, a reduction of 0.5833. Among five cells resolved independently in both observation regimes, two agreed and three conflicted. Standardized measurement therefore did not simply narrow uncertainty around a strongly recurrent package; it removed complete three-cluster A/F/C/P recurrence from the admissible set."
    anth_new = "On these same three clusters, literature augmented by Luo et al. (2016) left exact-signature recurrence at 0.333–1.0 and pairwise A/F/C/P concordance at 0.333–1.0. Candidate-free remeasurement reduced exact-signature recurrence to **0.333 exactly** and pairwise concordance to **0.333–0.5**. Pairwise identified-set width contracted from 0.6667 to 0.1667, a reduction of 0.5. Among six cells resolved independently in both observation regimes, two agreed and four conflicted. The newly comparable CJAPONICA F cell was a conflict: literature down versus candidate-free up. Increasing literature coverage therefore exposed additional disagreement rather than restoring complete mechanistic replay."
    text = replace_once(text, anth_old, anth_new, "anthocyanin recurrence results")

    discussion_old = "The comparison is not a test of whether candidate-gene papers are “right” or “wrong.” Candidate-selected studies often ask targeted biological questions and can resolve specific causal nodes more precisely than a broad module score. The candidate-free protocol asks a different question: if the same systems are measured with one outcome-independent pathway-wide representation, what multivariate recurrence remains identifiable? The formal database expansion provides an additional robustness check on the observation layer: adding an independent *C. semiserrata* red/white transcriptomic system increased A-axis coverage and made anthocyanin enrichment detectable even after dependence collapse, yet the study could not be added to the standardized arm without auditable public raw reads. Broader literature coverage therefore strengthened the ascertainment diagnosis while leaving the matched candidate-free recurrence estimator unchanged."
    discussion_new = "The comparison is not a test of whether candidate-gene papers are “right” or “wrong.” Targeted studies can resolve specific nodes more precisely than broad module scores. The candidate-free protocol asks a different biological question: when comparable flower-colour changes are generated repeatedly, how much of the multivariate pigment-network transition is replayed under one common measurement rule? Citation chasing sharpened that distinction. Luo et al. (2016) added an F-axis prediction to the existing CJAPONICA literature background, but the corresponding candidate-free F direction in the public Joy Kendrick system was opposite. At the same time, dependence-collapsed A-specific ascertainment weakened to P=0.078125. Thus observation nonuniformity remains a design concern, but the stronger result is empirical disagreement between literature-conditioned and standardized representations of the same evolutionary transition class, together with the loss of complete whole-package recurrence after standardized measurement."
    text = replace_once(text, discussion_old, discussion_new, "observation discussion")

    availability_old = "The current scientific manuscript consumes `data/paper1_authoritative_results_v0_2_1.csv`, `data/paper1_main_figure_manifest_v0_2_1.csv`, and `data/paper1_reference_registry_v0_2_1.csv`. The formal bibliographic search is frozen in run `33039509237`, and the updated literature-ascertainment calculation is frozen in run `33040242009`."
    availability_new = "The current scientific manuscript consumes `data/paper1_authoritative_results_v0_2_2.csv`, `data/paper1_main_figure_manifest_v0_2_2.csv`, and `data/paper1_reference_registry_v0_2_2.csv`. Formal database search and citation-chasing provenance are retained in the repository, and the corrected Luo literature recheck is frozen in hosted run `33045356947`."
    text = replace_once(text, availability_old, availability_new, "data availability")

    jiang_ref = "Jiang, H., et al. 2025. Integration of transcriptomic and chemical analysis reveals key regulatory mechanisms involved in color variation between red and white flowers of *Camellia semiserrata*. *Genetic Resources and Crop Evolution* 72(Suppl 1): 333–352. https://doi.org/10.1007/s10722-025-02606-6"
    luo_ref = "Luo, P., G. Ning, Z. Wang, Y. Shen, H. Jin, P. Li, S. Huang, J. Zhao, and M. Bao. 2016. Disequilibrium of flavonol synthase and dihydroflavonol-4-reductase expression associated tightly to white vs. red color flower formation in plants. *Frontiers in Plant Science* 6: 1257. https://doi.org/10.3389/fpls.2015.01257"
    text = replace_once(text, jiang_ref, jiang_ref + "\n\n" + luo_ref, "Luo reference insertion")

    required = [
        "A/F/C/P coverage = 10/5/1/3",
        "coverage was 5/4/1/2",
        "P=0.078125",
        "pairwise A/F/C/P concordance from 0.333 to 1.0",
        "Pairwise identified-set width contracted from 0.6667 to 0.1667",
        "Among six cells resolved independently in both observation regimes, two agreed and four conflicted",
        "10.3389/fpls.2015.01257",
        "run `33045356947`",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        raise SystemExit(f"v0.2.2 missing required tokens: {missing}")

    frozen = [
        "Candidate-free remeasurement fixed exact-signature recurrence at 0.333",
        "Candidate-free measurement point-identified exact-signature recurrence at **0.5** and pairwise concordance at **0.75**",
        "46 of 50 nontrivial splits were shared and normalized RF distance was 0.08",
        "strict P=0.00116 and dominant P=0.000080",
        "The strict×dominant shared robust event count was therefore zero",
        "Repeated flower-colour change in *Camellia* does not imply repetition of one complete A/F/C/P pigment-state package.",
    ]
    missing_frozen = [x for x in frozen if x not in text]
    if missing_frozen:
        raise SystemExit(f"v0.2.2 lost frozen science: {missing_frozen}")

    forbidden = [
        "coverage was 5/3/1/2",
        "anthocyanin-enrichment probability was 0.046875",
        "Pairwise identified-set width contracted from 0.75 to 0.1667",
        "Among five cells resolved independently in both observation regimes, two agreed and three conflicted",
    ]
    retained = [x for x in forbidden if x in text]
    if retained:
        raise SystemExit(f"v0.2.2 retains superseded tokens: {retained}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text.rstrip() + "\n", encoding="utf-8")
    summary = {
        "document_version": "Paper 1 science v0.2.2",
        "source": str(args.source),
        "base_builder": str(base_builder),
        "change_scope": "Luo 2016 literature-conditioned molecular update",
        "science_reference_count": 17,
        "candidate_free_systems_changed": False,
        "candidate_free_recurrence_changed": False,
        "yellow_changed": False,
        "macro_results_changed": False,
        "temporal_program_framing_deferred": True,
        "status": "science v0.2.2 manuscript generated",
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
