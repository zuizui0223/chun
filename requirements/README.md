# Dependency environments

Pinned Python requirement files live in this directory. This migration changes paths only; it does not normalize package versions.

Some files intentionally preserve historical replay environments. In particular, `requirements-petunieae-cross-level.txt` retains the dependency versions used for its frozen prospective result and must not be upgraded merely to match newer repository-wide pins.
