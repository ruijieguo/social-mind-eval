from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _format_error_path(error: jsonschema.ValidationError) -> str:
    path_str = "$"
    for part in error.absolute_path:
        if isinstance(part, int):
            path_str += f"[{part}]"
        else:
            path_str += f".{part}"
    return path_str


def validate_yaml_against_schema(path: Path, schema: dict[str, Any]) -> list[str]:
    try:
        document = load_yaml(path)
    except (yaml.YAMLError, OSError) as exc:
        return [f"{path.name}:$: failed to load yaml: {exc}"]

    validator = jsonschema.Draft202012Validator(schema)
    errors = []

    for error in validator.iter_errors(document):
        errors.append(f"{path.name}:{_format_error_path(error)}: {error.message}")

    return sorted(errors)


def _extract_dimension_ids(taxonomy: Any) -> set[str]:
    ids: set[str] = set()
    if not isinstance(taxonomy, dict):
        return ids

    for dimension in taxonomy.get("dimensions", []):
        if isinstance(dimension, dict):
            if "id" in dimension:
                ids.add(str(dimension["id"]))
            for subdimension in dimension.get("subdimensions", []):
                if isinstance(subdimension, dict):
                    if "id" in subdimension:
                        ids.add(str(subdimension["id"]))
                    for capability in subdimension.get("capabilities", []):
                        if isinstance(capability, dict) and "id" in capability:
                            ids.add(str(capability["id"]))
    return ids


def _validate_taxonomy_file(path: Path) -> list[str]:
    errors: list[str] = []

    try:
        taxonomy = load_yaml(path)
    except (yaml.YAMLError, OSError) as exc:
        return [f"{path.name}:$: failed to load yaml: {exc}"]
    if not isinstance(taxonomy, dict):
        return [f"{path.name}:$: taxonomy must be a mapping"]

    if "dimensions" not in taxonomy or not isinstance(taxonomy["dimensions"], list):
        errors.append(f"{path.name}:$.dimensions: expected list of top-level dimensions")

    seen_ids: set[str] = set()
    valid_task_families = {"T1", "T2", "T3", "T4", "T5", "T6"}

    for dimension in taxonomy.get("dimensions", []):
        if not isinstance(dimension, dict):
            continue
        dimension_id = str(dimension.get("id", ""))
        if dimension_id in seen_ids:
            errors.append(f"{path.name}:$.dimensions: duplicate taxonomy id '{dimension_id}'")
        elif dimension_id:
            seen_ids.add(dimension_id)

        for subdimension in dimension.get("subdimensions", []):
            if not isinstance(subdimension, dict):
                continue
            sub_id = str(subdimension.get("id", ""))
            if sub_id in seen_ids:
                errors.append(f"{path.name}:$.subdimensions: duplicate taxonomy id '{sub_id}'")
            elif sub_id:
                seen_ids.add(sub_id)

            task_family = subdimension.get("task_family")
            if task_family and str(task_family) not in valid_task_families:
                errors.append(
                    f"{path.name}:$.subdimensions[{sub_id}].task_family: invalid task_family '{task_family}'"
                )

            for capability in subdimension.get("capabilities", []):
                if not isinstance(capability, dict):
                    continue
                capability_id = str(capability.get("id", ""))
                if capability_id in seen_ids:
                    errors.append(
                        f"{path.name}:$.capabilities: duplicate taxonomy id '{capability_id}'"
                    )
                elif capability_id:
                    seen_ids.add(capability_id)

    extracted = _extract_dimension_ids(taxonomy)
    if not extracted:
        errors.append(f"{path.name}:$: no dimension ids found")

    return errors


def _validate_label_coverage(
    clusters_dir: Path,
    labels_path: Path,
    known_dimension_ids: set[str],
) -> list[str]:
    try:
        labels_doc = load_yaml(labels_path)
    except (yaml.YAMLError, OSError) as exc:
        return [f"{labels_path.name}:$: failed to load yaml: {exc}"]

    errors: list[str] = []
    labels = labels_doc.get("labels", []) if isinstance(labels_doc, dict) else []
    if not isinstance(labels, list):
        return [f"{labels_path.name}:$.labels: expected list"]

    labeled_items = {}
    for entry in labels:
        if not isinstance(entry, dict):
            errors.append(f"{labels_path.name}:$.labels: expected mapping entries")
            continue
        item_id = str(entry.get("item_id", ""))
        labeled_items[item_id] = entry
        dimension = entry.get("dimension")
        if dimension and known_dimension_ids and str(dimension) not in known_dimension_ids:
            errors.append(
                f"{labels_path.name}:$.labels[{item_id}].dimension: unknown primary dimension '{dimension}'"
            )

    for cluster_path in sorted(clusters_dir.glob("*.yaml")):
        try:
            cluster = load_yaml(cluster_path)
        except (yaml.YAMLError, OSError) as exc:
            errors.append(f"{cluster_path.name}:$: failed to load yaml: {exc}")
            continue

        if not isinstance(cluster, dict):
            errors.append(f"{cluster_path.name}:$: expected mapping")
            continue

        cluster_dimension = str(cluster.get("primary_dimension", ""))
        if cluster_dimension and known_dimension_ids and cluster_dimension not in known_dimension_ids:
            errors.append(
                f"{cluster_path.name}:$.primary_dimension: unknown primary dimension '{cluster_dimension}'"
            )

        for item in cluster.get("items", []):
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("item_id", ""))
            if item_id and item_id not in labeled_items:
                errors.append(
                    f"{labels_path.name}:$.labels: missing gold label for '{item_id}'"
                )

    return errors


def _validate_primary_dimension_reference(
    path: Path,
    known_dimension_ids: set[str],
) -> list[str]:
    if not known_dimension_ids:
        return []

    try:
        document = load_yaml(path)
    except (yaml.YAMLError, OSError) as exc:
        return [f"{path.name}:$: failed to load yaml: {exc}"]

    if not isinstance(document, dict):
        return [f"{path.name}:$: expected mapping"]

    primary_dimension = document.get("primary_dimension")
    if primary_dimension and str(primary_dimension) not in known_dimension_ids:
        return [
            f"{path.name}:$.primary_dimension: unknown primary dimension '{primary_dimension}'"
        ]

    return []


def validate_all(benchmark_root: Path) -> list[str]:
    errors: list[str] = []
    try:
        cluster_schema = load_json(benchmark_root / "schemas" / "sample_cluster.schema.json")
    except (json.JSONDecodeError, OSError) as exc:
        return [f"sample_cluster.schema.json:$: failed to load json schema: {exc}"]

    template_path = benchmark_root / "templates" / "sample_cluster_template.yaml"
    if template_path.exists():
        errors.extend(validate_yaml_against_schema(template_path, cluster_schema))

    taxonomy_schema_path = benchmark_root / "schemas" / "taxonomy.schema.json"
    taxonomy_schema: dict[str, Any] | None = None
    if taxonomy_schema_path.exists():
        try:
            taxonomy_schema = load_json(taxonomy_schema_path)
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"taxonomy.schema.json:$: failed to load json schema: {exc}")

    taxonomy_path = benchmark_root / "taxonomy" / "social_mind_dimensions.yaml"
    known_dimension_ids: set[str] = set()
    if taxonomy_path.exists():
        if taxonomy_schema is not None:
            errors.extend(validate_yaml_against_schema(taxonomy_path, taxonomy_schema))
        errors.extend(_validate_taxonomy_file(taxonomy_path))
        try:
            known_dimension_ids = _extract_dimension_ids(load_yaml(taxonomy_path))
        except (yaml.YAMLError, OSError):
            known_dimension_ids = set()

    if template_path.exists():
        errors.extend(_validate_primary_dimension_reference(template_path, known_dimension_ids))

    clusters_dir = benchmark_root / "pilot" / "clusters"
    if clusters_dir.exists():
        for cluster_path in sorted(clusters_dir.glob("*.yaml")):
            errors.extend(validate_yaml_against_schema(cluster_path, cluster_schema))
            errors.extend(_validate_primary_dimension_reference(cluster_path, known_dimension_ids))

    labels_path = benchmark_root / "pilot" / "labels" / "pilot_gold_labels.yaml"
    labels_schema_path = benchmark_root / "schemas" / "pilot_gold_labels.schema.json"
    if labels_path.exists() and labels_schema_path.exists():
        try:
            labels_schema = load_json(labels_schema_path)
            errors.extend(validate_yaml_against_schema(labels_path, labels_schema))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"pilot_gold_labels.schema.json:$: failed to load json schema: {exc}")

    if clusters_dir.exists() and labels_path.exists():
        errors.extend(_validate_label_coverage(clusters_dir, labels_path, known_dimension_ids))

    raw_response_schema_path = benchmark_root / "schemas" / "model_response.schema.json"
    if raw_response_schema_path.exists():
        try:
            raw_response_schema = load_json(raw_response_schema_path)
            raw_responses_dir = benchmark_root / "responses" / "raw"
            if raw_responses_dir.exists():
                for response_path in sorted(raw_responses_dir.glob("*.yaml")):
                    errors.extend(validate_yaml_against_schema(response_path, raw_response_schema))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"model_response.schema.json:$: failed to load json schema: {exc}")

    scored_response_schema_path = benchmark_root / "schemas" / "scored_response.schema.json"
    if scored_response_schema_path.exists():
        try:
            scored_response_schema = load_json(scored_response_schema_path)
            scored_responses_dir = benchmark_root / "responses" / "scored"
            if scored_responses_dir.exists():
                for response_path in sorted(scored_responses_dir.glob("*.yaml")):
                    errors.extend(validate_yaml_against_schema(response_path, scored_response_schema))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"scored_response.schema.json:$: failed to load json schema: {exc}")

    return errors


if __name__ == "__main__":
    validation_errors = validate_all(Path("benchmark"))
    if validation_errors:
        print("VALIDATION FAILED")
        for error in validation_errors:
            print(error)
        raise SystemExit(1)

    print("VALIDATION PASSED")
