# ASTROGATION — Interstellar flight profiles and observational signatures of positive-energy warp shells

Reproduction package for the paper (English canonical / Japanese translation
in `paper/`). Everything in the paper is machine-generated from the catalogs
in `results/` and verified by the certification suite.

日本語の説明は `README_ja.md` を参照。

## What this is

We compute the first admissibility-constrained interstellar maneuver catalog
for the radiative momentum warpshell of Le (arXiv:2606.22531), and map every
maneuver to observer-frame light curves: an exact forward null during
saturated acceleration, a deceleration flash with closed-form decay
$F \propto e^{7\eta-3\Delta\eta_{\rm tot}}$, and a gravitational-wave
silence discriminator.

## Reproduce

Environment: Python 3.12, numpy, scipy, pytest, matplotlib (a conda
environment containing warpax 1.3.0 was used; warpax is needed only for the
cross-check connection test).

```
# 1. Certification suite (C1-C19 + style lints; under one minute)
python -m pytest tests

# 2. Regenerate the catalogs (maneuvers, ~15 min; signatures, ~1 min)
python scripts/make_catalog.py
python scripts/make_signatures.py

# 3. Regenerate paper numbers, tables, and figures; compile
python scripts/make_paper_numbers.py
python scripts/make_figures_paper_en.py
cd paper && tectonic paper_en.tex && tectonic paper_ja.tex
```

The quarantined archaeology tests (v2-retracted structures) run with
`pytest --run-archaeology`.

## Layout

`CLAUDE.md` project constitution / `conventions.md` conventions ledger /
`ASSUMPTIONS.md` assumptions ledger / `docs/reports/` phase gate reports
(formula ledger, STOP reports, reconciliation) / `src/astrogation/` certified
library / `tests/` certification suite / `results/` catalogs and signatures /
`paper/` manuscripts, generated numbers, tables, figures.

## Authority labels

Every published number inherits a label: [R] exact closed form, [N]
published numerics (never extrapolated), [H] heuristic (display only),
[R(A3)/provisional] the conservative floor pending reconciliation (see the
paper, Methods).

## License and citation

Code: MIT. Paper: CC BY 4.0. This package uses warpax and world_tube
(MIT, An T. Le). If you use this catalog, cite the paper and
arXiv:2606.22531.
