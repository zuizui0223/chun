from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "paper1_submission_v10", ROOT / "scripts" / "run_paper1_submission_v1_0.py"
)
submission = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(submission)


def _full_source_fixture() -> str:
    return "\n\n".join(edit["old"] for edit in submission.SIMPSON_CLARIFICATIONS)


def test_simpson_editorial_replacements_are_exhaustive_and_unique() -> None:
    original = _full_source_fixture()
    corrected = submission.apply_simpson_clarifications(original)
    for edit in submission.SIMPSON_CLARIFICATIONS:
        assert edit["new"] in corrected, edit["label"]
        assert edit["old"] not in corrected, edit["label"]


def test_simpson_wording_patch_is_fail_closed_on_source_drift() -> None:
    source = _full_source_fixture()
    with pytest.raises(SystemExit, match="expected one source span"):
        submission.apply_simpson_clarifications(
            source.replace(submission.SIMPSON_CLARIFICATIONS[0]["old"], "MISSING", 1)
        )
    with pytest.raises(SystemExit, match="expected one source span"):
        submission.apply_simpson_clarifications(
            source + "\n\n" + submission.SIMPSON_CLARIFICATIONS[0]["old"]
        )


def test_simpson_abstract_clarification_preserves_frozen_242_words() -> None:
    abstract = submission.AJB_ABSTRACT_V10_034
    assert submission.abstract_word_count(abstract + "\n\n**Key words:** test") == 242

    # Add other required manuscript snippets strictly outside the abstract.
    other_spans = "\n\n".join(
        edit["old"] for edit in submission.SIMPSON_CLARIFICATIONS[2:]
    )
    input_text = abstract + "\n\n**Key words:** test\n\n" + other_spans
    updated = submission.apply_simpson_clarifications(input_text)
    assert submission.abstract_word_count(updated) == 242
    assert "its 0.333 floor" in updated
    assert "its 0.5 floor" in updated
    assert "R = sum_s(c_s/n)^2" in updated
    assert "Differences in those mathematical floors" in updated
