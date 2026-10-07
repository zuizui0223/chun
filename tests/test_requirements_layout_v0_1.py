from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_no_root_requirement_files_remain() -> None:
    assert sorted(p.name for p in ROOT.glob("requirements-*.txt")) == []


def test_requirement_files_live_under_requirements_directory() -> None:
    reqdir = ROOT / "requirements"
    assert reqdir.is_dir()
    files = sorted(reqdir.glob("requirements-*.txt"))
    assert files
    assert all(p.is_file() for p in files)
