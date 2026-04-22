# social-mind-eval

`social-mind-eval` is a benchmark framework prototype for evaluating social-mind capabilities in text dialogue models.

## Repository structure

- `docs/superpowers/specs/`: design and system documents
- `benchmark/taxonomy/`: machine-readable dimension hierarchy
- `benchmark/schemas/`: JSON Schemas for benchmark assets
- `benchmark/templates/`: authoring templates for clusters and task types
- `benchmark/rubrics/`: judge and annotation guidance
- `benchmark/pilot/`: pilot clusters and gold labels
- `scripts/`: validation, taxonomy rendering, and report aggregation scripts
- `tests/`: automated tests for schemas, validation, taxonomy, and reporting

## Key documents

- `docs/superpowers/specs/2026-04-21-social-mind-eval-design.md`
- `docs/superpowers/specs/2026-04-21-social-mind-benchmark-system.md`

## Validation

Run from the repository root:

```bash
pytest tests -v
python scripts/validate_benchmark.py
python scripts/render_taxonomy_report.py
```
