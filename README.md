# social-mind-eval

`social-mind-eval` is a benchmark framework prototype for evaluating **social-mind capabilities** in text dialogue models.

The project focuses on a specific question: can a language model correctly model social situations, hidden mental states, social mechanisms, dynamic consequences, normative boundaries, and context-appropriate responses?

It is **not** designed as a sociology knowledge exam, a psychology terminology benchmark, or a pure safety-refusal benchmark.

## What This Repository Contains

This repository currently includes:

- a full social-mind benchmark design
- a machine-readable taxonomy aligned with the design spec
- schemas for benchmark assets, labels, raw responses, and scored responses
- pilot benchmark clusters and gold labels
- automated validation for taxonomy, clusters, labels, and response artifacts
- report generation utilities for top-level and second-level capability profiles

## Core Evaluation Axes

The benchmark is organized around six top-level dimensions:

1. `社会语境构型`
2. `多主体心智建模`
3. `社会机制理解`
4. `社会动态推演`
5. `规范与价值裁决`
6. `社会回应生成`

Together, they define a social-mind evaluation chain:

`situation modeling -> hidden-state modeling -> mechanism understanding -> dynamic forecasting -> normative judgment -> response generation`

## Repository Guide

### Main documents

- `docs/superpowers/specs/2026-04-21-social-mind-eval-design.md`
  - full design spec
- `docs/superpowers/specs/2026-04-21-social-mind-benchmark-system.md`
  - benchmark system overview written in a more technical-report style

### Benchmark assets

- `benchmark/taxonomy/`
  - machine-readable dimension hierarchy
- `benchmark/schemas/`
  - JSON Schemas for taxonomy, clusters, labels, raw responses, and scored responses
- `benchmark/templates/`
  - authoring templates for benchmark assets
- `benchmark/rubrics/`
  - judge rubric and annotation guide
- `benchmark/pilot/`
  - pilot clusters and pilot gold labels

### Tooling

- `scripts/validate_benchmark.py`
  - validates benchmark assets and cross-file consistency
- `scripts/render_taxonomy_report.py`
  - renders a markdown taxonomy summary
- `scripts/aggregate_reports.py`
  - aggregates scored responses into diagnostic reports

### Tests

- `tests/`
  - automated tests for validation, taxonomy rendering, and report generation

## Quick Start

Run from the repository root:

```bash
pytest tests -v
python scripts/validate_benchmark.py
python scripts/render_taxonomy_report.py
```

If you later add scored responses under `benchmark/responses/scored/`, you can generate a profile report with:

```bash
python scripts/aggregate_reports.py
```

## Current Status

The repository currently provides a **benchmark prototype system**, not a finished large-scale public benchmark release.

What is already in place:

- complete design documents
- complete taxonomy
- schema-constrained benchmark assets
- pilot evaluation data
- validator and report generator
- automated tests

What is still open for future work:

- benchmark runner
- larger benchmark dataset expansion
- automated scoring pipeline
- richer failure clustering and reporting

## Recommended Reading Order

If you want to understand the framework quickly, read in this order:

1. `docs/superpowers/specs/2026-04-21-social-mind-benchmark-system.md`
2. `docs/superpowers/specs/2026-04-21-social-mind-eval-design.md`
3. `benchmark/taxonomy/social_mind_dimensions.yaml`
4. `benchmark/pilot/clusters/`
5. `benchmark/pilot/labels/pilot_gold_labels.yaml`

## License / Release Note

No explicit license or packaged release workflow has been added yet. If this repository is intended for broader public reuse, the next practical step is to add a license and a more formal release/readme structure.
