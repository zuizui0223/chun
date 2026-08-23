#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path

REPLACEMENTS = [
    (
        "The presence of large service effects in A, W, and Y systems did not support a red-specific bird-pollination syndrome.",
        "The presence of large service effects in A, W, and Y systems did not support a red-specific bird-pollination syndrome (Kunitake et al., 2004; Sun et al., 2017; Zhang et al., 2024).",
    ),
    (
        "Bird access versus bird exclusion gave RR = **2.29**, whereas *Apis cerana* introduction versus no-bee cages gave RR = **2.56**; their equal-weight geometric mean was **2.42**.",
        "Bird access versus bird exclusion gave RR = **2.29**, whereas *Apis cerana* introduction versus no-bee cages gave RR = **2.56**; their equal-weight geometric mean was **2.42** (Zhang et al., 2024; Liu et al., 2025).",
    ),
    (
        "Pollinator-reliability gradients converged on the same mechanism: across five registered effects, higher legitimate-bee availability predicted greater fruit set or lower pollen limitation and greater distance from a nesting aggregation predicted lower fruit set (**5/5** in the expected direction).",
        "Pollinator-reliability gradients converged on the same mechanism: across five registered effects, higher legitimate-bee availability predicted greater fruit set or lower pollen limitation and greater distance from a nesting aggregation predicted lower fruit set (**5/5** in the expected direction; Xie et al., 2013; Li et al., 2021).",
    ),
    (
        "In *C. pubipetala*, supplemental pollination increased fruit set from 4/60 to 7/30 flowers (RR = **3.50**, reconstructed SE[lnRR] = 0.586, approximate 95% RR interval 1.11–11.03).",
        "In *C. pubipetala*, supplemental pollination increased fruit set from 4/60 to 7/30 flowers (RR = **3.50**, reconstructed SE[lnRR] = 0.586, approximate 95% RR interval 1.11–11.03; Chai et al., 2019).",
    ),
    (
        "In contrast, *C. petelotii* showed no detectable open-versus-supplemental difference despite a large bird-exclusion effect.",
        "In contrast, *C. petelotii* showed no detectable open-versus-supplemental difference despite a large bird-exclusion effect (Sun et al., 2017).",
    ),
    (
        "Across eight *C. oleifera* forests, pollen limitation declined as legitimate *Andrena camellia* visit density increased (reported *P* = 0.004).",
        "Across eight *C. oleifera* forests, pollen limitation declined as legitimate *Andrena camellia* visit density increased (reported *P* = 0.004; Xie et al., 2013).",
    ),
    (
        "A cooler northward *C. hainanica* site delayed anthesis by 45 d, reduced peak visitation by 92%, reduced pollen deposition by 57%, and produced zero natural fruit set while hand cross-pollination still produced fruit.",
        "A cooler northward *C. hainanica* site delayed anthesis by 45 d, reduced peak visitation by 92%, reduced pollen deposition by 57%, and produced zero natural fruit set while hand cross-pollination still produced fruit (Yuan et al., 2025).",
    ),
    (
        "Seasonal *C. perpetua* data showed winter/summer nectar-volume and sucrose:hexose ratios of approximately 3.51 and 7.11, with stronger winter bird/reproductive weighting.",
        "Seasonal *C. perpetua* data showed winter/summer nectar-volume and sucrose:hexose ratios of approximately 3.51 and 7.11, with stronger winter bird/reproductive weighting (Jiang et al., 2025).",
    ),
    (
        "Only one admitted flower-specific *Camellia* manipulation measured pigment response directly, and its cold treatment was confounded with darkness.",
        "Only one admitted flower-specific *Camellia* manipulation measured pigment response directly, and its cold treatment was confounded with darkness (Berruti et al., 2015).",
    ),
    (
        "Finally, a paired same-visible-red comparison between *C. rusticana* and *C. japonica* showed an approximately **23.45-fold** difference in bumblebee visitation together with UV/fluorescence differences, demonstrating that coarse visible hue is not a unique pollinator-functional state.",
        "Finally, a paired same-visible-red comparison between *C. rusticana* and *C. japonica* showed an approximately **23.45-fold** difference in bumblebee visitation together with UV/fluorescence differences, demonstrating that coarse visible hue is not a unique pollinator-functional state (Mori et al., 2023).",
    ),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    text = a.input.read_text(encoding='utf-8')
    for old, new in REPLACEMENTS:
        n = text.count(old)
        if n != 1:
            raise SystemExit(f'ecological citation anchor count={n}: {old[:80]}')
        text = text.replace(old, new, 1)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(text, encoding='utf-8')
    print(f'added {len(REPLACEMENTS)} ecological citation anchors')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
