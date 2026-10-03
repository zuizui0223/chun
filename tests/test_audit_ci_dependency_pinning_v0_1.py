from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_ci_dependency_pinning_v0_1.py"
spec = importlib.util.spec_from_file_location("dep_audit", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def rows(text: str):
    return mod.pip_lines_from_text(text)


def test_existing_unpinned_debt_does_not_block_unrelated_edit():
    base = rows("run: python -m pip install numpy\n")
    current = rows("run: python -m pip install numpy\n")
    assert mod.new_unpinned_rows(current, base) == []


def test_new_unpinned_command_is_rejected():
    base = rows("run: python -m pip install numpy\n")
    current = rows(
        "run: python -m pip install numpy\n"
        "run: python -m pip install scipy\n"
    )
    added = mod.new_unpinned_rows(current, base)
    assert [row["command"] for row in added] == [
        "run: python -m pip install scipy"
    ]


def test_increasing_duplicate_unpinned_command_count_is_rejected():
    base = rows("run: python -m pip install numpy\n")
    current = rows(
        "run: python -m pip install numpy\n"
        "run: python -m pip install numpy\n"
    )
    assert len(mod.new_unpinned_rows(current, base)) == 1


def test_requirement_file_is_not_dependency_debt():
    current = rows(
        "run: python -m pip install --disable-pip-version-check "
        "-r requirements-family.txt\n"
    )
    assert current[0]["pinned"] is True
    assert mod.new_unpinned_rows(current, []) == []
