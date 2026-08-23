#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def extract_frozen_abstract(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    start = "### Premise of the study"
    stop = "## Claim checks"
    if start not in text or stop not in text:
        raise SystemExit("cannot locate frozen AJB abstract block")
    block = text.split(start, 1)[1].split(stop, 1)[0].strip()
    return start + "\n\n" + block


def replace_abstract(text: str, abstract_block: str) -> str:
    start = "## ABSTRACT"
    stop = "**Key words:**"
    if start not in text or stop not in text:
        raise SystemExit("cannot locate manuscript abstract block")
    before, rest = text.split(start, 1)
    _, after = rest.split(stop, 1)
    return before + start + "\n\n" + abstract_block.strip() + "\n\n" + stop + after


def sort_reference_block(text: str) -> tuple[str, int]:
    start = "# REFERENCES — v0.2 verified core set"
    stop = "# OPEN ITEMS FOR v0.3"
    if start not in text or stop not in text:
        raise SystemExit("cannot locate v0.2 reference block for sorting")
    before, rest = text.split(start, 1)
    refs_text, after = rest.split(stop, 1)
    entries = [x.strip() for x in re.split(r"\n\s*\n", refs_text.strip()) if x.strip()]
    if len(entries) < 15:
        raise SystemExit(f"unexpectedly small reference block: {len(entries)} entries")
    entries = sorted(entries, key=lambda entry: re.sub(r"[*_`]", "", entry).strip().casefold())
    rebuilt = before + start + "\n\n" + "\n\n".join(entries) + "\n\n" + stop + after
    return rebuilt, len(entries)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v01", type=Path, required=True)
    ap.add_argument("--abstract-source", type=Path, required=True)
    ap.add_argument("--corrections", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    a = ap.parse_args()

    text = a.v01.read_text(encoding="utf-8")
    text = replace_abstract(text, extract_frozen_abstract(a.abstract_source))
    corrections = read_csv(a.corrections)
    applied = []

    for row in corrections:
        cid = row["correction_id"]
        ctype = row["correction_type"]
        old = row["old_text"]
        new = row["new_text"]
        if ctype in {"in_text_year", "reference_entry"}:
            n = text.count(old)
            if n < 1:
                # ECO001 rewrites the legacy pollination paragraph. The ecological-v2
                # overlay replaces that whole paragraph upstream, so its absence is
                # expected and must not block bibliographic corrections downstream.
                if cid == "ECO001" and "## Ecological synthesis supports reproductive-service filtering" in text:
                    applied.append({"correction_id": cid, "type": ctype, "occurrences": 0, "status": "superseded_by_ecological_v2_overlay"})
                    continue
                raise SystemExit(f"{cid}: old text not found")
            text = text.replace(old, new)
            applied.append({"correction_id": cid, "type": ctype, "occurrences": n})
        elif ctype == "reference_insertion":
            if new in text:
                applied.append({"correction_id": cid, "type": ctype, "occurrences": 0, "status": "already_present"})
                continue
            anchor = "Wu, Q., W. Tong, H. Zhao, R. Ge, R. Li, J. Huang, F. Li, et al. 2022."
            if anchor not in text:
                raise SystemExit(f"{cid}: reference insertion anchor not found")
            text = text.replace(anchor, new + "\n\n" + anchor, 1)
            applied.append({"correction_id": cid, "type": ctype, "occurrences": 1})
        else:
            raise SystemExit(f"{cid}: unsupported correction type {ctype}")

    text = text.replace(
        "> Draft v0.1. This manuscript consumes the frozen Paper 1 authoritative-result and analysis-disposition registries.",
        "> Draft v0.2. This manuscript consumes the frozen Paper 1 authoritative-result and analysis-disposition registries.",
        1,
    )
    text = text.replace("# REFERENCES — v0.1 verified core set", "# REFERENCES — v0.2 verified core set", 1)
    text = text.replace("# OPEN ITEMS FOR v0.2", "# OPEN ITEMS FOR v0.3", 1)
    text = text.replace("- Verify final bibliographic pagination/article numbering for Fan et al. 2026 and all source-register underlying references used in Supplement.\n", "- Verify all source-register underlying references used in Supplement and final AJB punctuation/style at copy-edit stage.\n")
    text = text.replace("- Resolve the complete AJB-format Literature Cited entries for all non-core ecological primary studies and the WFO Plant List snapshot.\n", "- Resolve complete AJB-format Literature Cited entries for any additional ecological primary studies introduced during final Supplement integration.\n")

    text, n_refs = sort_reference_block(text)

    required = [
        "Lacey, 2026",
        "Lacey, E. P. 2026.",
        "1725–1739",
        "World Flora Online Consortium. 2026.",
        "10.5281/zenodo.20782718",
        "Sun et al., 2017",
        "Zhang et al., 2024",
        "10.1111/jipb.13731",
        "> Draft v0.2.",
    ]
    for token in required:
        if token not in text:
            raise SystemExit(f"v0.2 output missing required correction token: {token}")
    forbidden = ["Lacey, 2025", "Lacey, E. P. 2025.", "1725–[final pages to verify in journal export]"]
    for token in forbidden:
        if token in text:
            raise SystemExit(f"v0.2 output retains stale token: {token}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(text, encoding="utf-8")
    summary = {
        "source_manuscript": str(a.v01),
        "abstract_source": str(a.abstract_source),
        "output_manuscript": str(a.out),
        "frozen_abstract_injected": True,
        "correction_rows": len(corrections),
        "applied": applied,
        "literature_cited_entries": n_refs,
        "literature_cited_sorted": True,
        "required_tokens_present": True,
        "stale_tokens_absent": True,
        "scientific_results_changed_by_this_step": False,
        "scope": "ecological-v2 integrated input plus abstract injection, bibliographic/source-text corrections, and reference ordering",
    }
    a.summary.parent.mkdir(parents=True, exist_ok=True)
    a.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
