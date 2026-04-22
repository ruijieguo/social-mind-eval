# Social Mind Benchmark Assets

This directory contains the executable benchmark assets derived from `docs/superpowers/specs/2026-04-21-social-mind-eval-design.md`.

## Structure

- `taxonomy/`: dimension hierarchy and metadata
- `schemas/`: JSON Schemas for validation
- `templates/`: reusable cluster templates
- `rubrics/`: scoring and annotation rules
- `pilot/`: pilot benchmark data

## Current scope note

The taxonomy YAML currently encodes the pilot subset needed by the implemented
assets in this repository. The full normative hierarchy is defined in
`docs/superpowers/specs/2026-04-21-social-mind-eval-design.md`.

## Validation

Run from the repository root:

```bash
python scripts/validate_benchmark.py
```

## Taxonomy report

Run from the repository root:

```bash
python scripts/render_taxonomy_report.py
```

## Full verification

Run from the repository root:

```bash
pytest tests -v
python scripts/validate_benchmark.py
python scripts/render_taxonomy_report.py
```

Convenience command:

```bash
pytest tests -v && python scripts/validate_benchmark.py && python scripts/render_taxonomy_report.py
```

Expected:

- all tests pass
- validator prints `VALIDATION PASSED`
- taxonomy summary prints six top-level dimensions
