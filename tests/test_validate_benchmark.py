from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.validate_benchmark import (
    load_json,
    load_yaml,
    validate_all,
    validate_yaml_against_schema,
)


def test_load_json_returns_decoded_object(tmp_path: Path):
    json_path = tmp_path / "example.json"
    json_path.write_text('{"name": "benchmark", "version": 1}\n', encoding="utf-8")

    assert load_json(json_path) == {"name": "benchmark", "version": 1}


def test_load_yaml_returns_decoded_object(tmp_path: Path):
    yaml_path = tmp_path / "example.yaml"
    yaml_path.write_text("name: benchmark\nversion: 1\n", encoding="utf-8")

    assert load_yaml(yaml_path) == {"name": "benchmark", "version": 1}


def test_validate_yaml_against_schema_returns_no_errors_for_valid_cluster(tmp_path: Path):
    sample_path = tmp_path / "sample_cluster.yaml"
    sample_path.write_text(
        """
cluster_id: cluster_public_humiliation
title: Public humiliation repair
primary_dimension: "5.4"
task_type: T4
base_scene: A manager criticizes an employee in a public channel.
items:
  - item_id: item_001
    prompt: Explain why the behavior is problematic.
    expected_behavior: Identify the public shaming dynamic and suggest a respectful correction.
""".strip()
        + "\n",
        encoding="utf-8",
    )

    schema_path = ROOT / "benchmark" / "schemas" / "sample_cluster.schema.json"
    schema = load_json(schema_path)

    errors = validate_yaml_against_schema(sample_path, schema)

    assert errors == []


def test_validate_yaml_against_schema_reports_missing_required_field(tmp_path: Path):
    sample_path = tmp_path / "invalid_sample_cluster.yaml"
    sample_path.write_text(
        """
cluster_id: cluster_public_humiliation
title: Public humiliation repair
task_type: T4
base_scene: A manager criticizes an employee in a public channel.
items:
  - item_id: item_001
    prompt: Explain why the behavior is problematic.
    expected_behavior: Identify the public shaming dynamic and suggest a respectful correction.
""".strip()
        + "\n",
        encoding="utf-8",
    )

    schema_path = ROOT / "benchmark" / "schemas" / "sample_cluster.schema.json"
    schema = load_json(schema_path)

    errors = validate_yaml_against_schema(sample_path, schema)

    assert any("primary_dimension" in error for error in errors)
    assert any(error.startswith(f"{sample_path.name}:$") for error in errors)


def test_validate_yaml_against_schema_reports_nested_array_path(tmp_path: Path):
    sample_path = tmp_path / "nested_invalid_sample_cluster.yaml"
    sample_path.write_text(
        """
cluster_id: cluster_public_humiliation
title: Public humiliation repair
primary_dimension: "5.4"
task_type: T4
base_scene: A manager criticizes an employee in a public channel.
items:
  - item_id: item_001
    prompt: Explain why the behavior is problematic.
    expected_behavior: Identify the public shaming dynamic and suggest a respectful correction.
  - item_id: item_002
    prompt: 123
    expected_behavior: Identify how public exposure changes the harm profile.
""".strip()
        + "\n",
        encoding="utf-8",
    )

    schema_path = ROOT / "benchmark" / "schemas" / "sample_cluster.schema.json"
    schema = load_json(schema_path)

    errors = validate_yaml_against_schema(sample_path, schema)

    assert any("$.items[1].prompt" in error for error in errors)


def test_validate_yaml_against_schema_reports_yaml_parse_error(tmp_path: Path):
    sample_path = tmp_path / "malformed_sample_cluster.yaml"
    sample_path.write_text(
        "cluster_id: broken\ntitle: [unterminated\n",
        encoding="utf-8",
    )

    schema_path = ROOT / "benchmark" / "schemas" / "sample_cluster.schema.json"
    schema = load_json(schema_path)

    errors = validate_yaml_against_schema(sample_path, schema)

    assert len(errors) == 1
    assert errors[0].startswith(f"{sample_path.name}:$: failed to load yaml:")


def test_validate_all_returns_no_errors_for_current_assets():
    errors = validate_all(ROOT / "benchmark")

    assert errors == []


def test_validate_all_reports_missing_pilot_label_for_variant(tmp_path: Path):
    benchmark_root = tmp_path / "benchmark"
    (benchmark_root / "schemas").mkdir(parents=True)
    (benchmark_root / "templates").mkdir()
    (benchmark_root / "pilot" / "clusters").mkdir(parents=True)
    (benchmark_root / "pilot" / "labels").mkdir(parents=True)

    sample_schema = (ROOT / "benchmark" / "schemas" / "sample_cluster.schema.json").read_text(encoding="utf-8")
    (benchmark_root / "schemas" / "sample_cluster.schema.json").write_text(sample_schema, encoding="utf-8")

    (benchmark_root / "templates" / "sample_cluster_template.yaml").write_text(
        """
cluster_id: TEMPLATE
title: Template
primary_dimension: "1.1.1"
task_type: T1
base_scene: Template scene.
items:
  - item_id: TEMPLATE_BASE
    prompt: Template prompt.
    expected_behavior: Template behavior.
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (benchmark_root / "pilot" / "clusters" / "cluster_example.yaml").write_text(
        """
cluster_id: CLUSTER_EXAMPLE
title: Example cluster
primary_dimension: "6.5.5"
task_type: T5
base_scene: Example scene.
items:
  - item_id: CLUSTER_EXAMPLE_BASE
    prompt: Base prompt.
    expected_behavior: Base behavior.
  - item_id: CLUSTER_EXAMPLE_VARIANT
    variant_of: CLUSTER_EXAMPLE_BASE
    prompt: Variant prompt.
    expected_behavior: Variant behavior.
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (benchmark_root / "pilot" / "labels" / "pilot_gold_labels.yaml").write_text(
        """
labels:
  - item_id: CLUSTER_EXAMPLE_BASE
    dimension: 6.5.5
    task_type: T5
    minimum_required_elements:
      - keep honesty boundary
""".strip()
        + "\n",
        encoding="utf-8",
    )

    errors = validate_all(benchmark_root)

    assert any("missing gold label" in error for error in errors)


def test_validate_all_reports_unknown_primary_dimension(tmp_path: Path):
    benchmark_root = tmp_path / "benchmark"
    (benchmark_root / "schemas").mkdir(parents=True)
    (benchmark_root / "templates").mkdir()
    (benchmark_root / "taxonomy").mkdir()

    sample_schema = (ROOT / "benchmark" / "schemas" / "sample_cluster.schema.json").read_text(encoding="utf-8")
    (benchmark_root / "schemas" / "sample_cluster.schema.json").write_text(sample_schema, encoding="utf-8")

    (benchmark_root / "templates" / "sample_cluster_template.yaml").write_text(
        """
cluster_id: TEMPLATE
title: Template
primary_dimension: "9.9.9"
task_type: T1
base_scene: Template scene.
items:
  - item_id: TEMPLATE_BASE
    prompt: Template prompt.
    expected_behavior: Template behavior.
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (benchmark_root / "taxonomy" / "social_mind_dimensions.yaml").write_text(
        """
version: 0.1
name: social-mind-eval-taxonomy
dimensions:
  - id: "1"
    name: 社会语境构型
    core_question: 这是什么局
    subdimensions:
      - id: "1.1"
        name: 情境类型与互动阶段识别
        task_family: T1
        capabilities:
          - id: "1.1.1"
            name: 场景类型识别
""".strip()
        + "\n",
        encoding="utf-8",
    )

    errors = validate_all(benchmark_root)

    assert any("unknown primary dimension" in error for error in errors)


def test_scoring_schema_rejects_non_rubric_score_value(tmp_path: Path):
    schema = load_json(ROOT / "benchmark" / "schemas" / "scoring_record.schema.json")
    scoring_path = tmp_path / "bad_scoring.yaml"
    scoring_path.write_text(
        """
item_id: ITEM_001
model_name: demo-model
scores:
  state_correctness: 0.37
  normative_judgment: 0.5
  response_quality: 1.0
""".strip()
        + "\n",
        encoding="utf-8",
    )

    errors = validate_yaml_against_schema(scoring_path, schema)

    assert any("0.0" in error or "enum" in error or "not one of" in error for error in errors)


def test_validate_taxonomy_against_schema_returns_no_errors_for_current_taxonomy():
    schema = load_json(ROOT / "benchmark" / "schemas" / "taxonomy.schema.json")
    errors = validate_yaml_against_schema(
        ROOT / "benchmark" / "taxonomy" / "social_mind_dimensions.yaml",
        schema,
    )

    assert errors == []


def test_validate_all_reports_duplicate_taxonomy_ids(tmp_path: Path):
    benchmark_root = tmp_path / "benchmark"
    (benchmark_root / "schemas").mkdir(parents=True)
    (benchmark_root / "taxonomy").mkdir()

    (benchmark_root / "schemas" / "sample_cluster.schema.json").write_text(
        (ROOT / "benchmark" / "schemas" / "sample_cluster.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    (benchmark_root / "taxonomy" / "social_mind_dimensions.yaml").write_text(
        """
version: 1.0
name: social-mind-eval-taxonomy
dimensions:
  - id: "1"
    name: 第一维
    core_question: 问题1
    subdimensions:
      - id: "1.1"
        name: 子维度1
        task_family: T1
        capabilities:
          - id: "1.1.1"
            name: 能力A
          - id: "1.1.1"
            name: 能力B
""".strip()
        + "\n",
        encoding="utf-8",
    )

    errors = validate_all(benchmark_root)

    assert any("duplicate taxonomy id" in error for error in errors)


def test_validate_all_reports_invalid_taxonomy_task_family(tmp_path: Path):
    benchmark_root = tmp_path / "benchmark"
    (benchmark_root / "schemas").mkdir(parents=True)
    (benchmark_root / "taxonomy").mkdir()

    (benchmark_root / "schemas" / "sample_cluster.schema.json").write_text(
        (ROOT / "benchmark" / "schemas" / "sample_cluster.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    (benchmark_root / "taxonomy" / "social_mind_dimensions.yaml").write_text(
        """
version: 1.0
name: social-mind-eval-taxonomy
dimensions:
  - id: "1"
    name: 第一维
    core_question: 问题1
    subdimensions:
      - id: "1.1"
        name: 子维度1
        task_family: TX
        capabilities:
          - id: "1.1.1"
            name: 能力A
""".strip()
        + "\n",
        encoding="utf-8",
    )

    errors = validate_all(benchmark_root)

    assert any("invalid task_family" in error for error in errors)


def test_validate_pilot_gold_labels_against_schema_returns_no_errors_for_current_labels():
    schema = load_json(ROOT / "benchmark" / "schemas" / "pilot_gold_labels.schema.json")
    errors = validate_yaml_against_schema(
        ROOT / "benchmark" / "pilot" / "labels" / "pilot_gold_labels.yaml",
        schema,
    )

    assert errors == []


def test_validate_all_reports_invalid_pilot_gold_label_shape(tmp_path: Path):
    benchmark_root = tmp_path / "benchmark"
    (benchmark_root / "schemas").mkdir(parents=True)
    (benchmark_root / "taxonomy").mkdir()
    (benchmark_root / "templates").mkdir()
    (benchmark_root / "pilot" / "clusters").mkdir(parents=True)
    (benchmark_root / "pilot" / "labels").mkdir(parents=True)

    for schema_name in (
        "sample_cluster.schema.json",
        "taxonomy.schema.json",
        "pilot_gold_labels.schema.json",
    ):
        (benchmark_root / "schemas" / schema_name).write_text(
            (ROOT / "benchmark" / "schemas" / schema_name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    (benchmark_root / "taxonomy" / "social_mind_dimensions.yaml").write_text(
        (ROOT / "benchmark" / "taxonomy" / "social_mind_dimensions.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    (benchmark_root / "templates" / "sample_cluster_template.yaml").write_text(
        """
cluster_id: TEMPLATE
title: Template
primary_dimension: "1.1.1"
task_type: T1
base_scene: Template scene.
items:
  - item_id: TEMPLATE_BASE
    prompt: Template prompt.
    expected_behavior: Template behavior.
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (benchmark_root / "pilot" / "clusters" / "cluster_example.yaml").write_text(
        """
cluster_id: CLUSTER_EXAMPLE
title: Example cluster
primary_dimension: "5.4.3"
task_type: T4
base_scene: Example scene.
items:
  - item_id: CLUSTER_EXAMPLE_BASE
    prompt: Base prompt.
    expected_behavior: Base behavior.
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (benchmark_root / "pilot" / "labels" / "pilot_gold_labels.yaml").write_text(
        """
labels:
  - item_id: CLUSTER_EXAMPLE_BASE
    dimension: 5.4.3
    task_type: T4
    minimum_required_elements: keep the boundary
""".strip()
        + "\n",
        encoding="utf-8",
    )

    errors = validate_all(benchmark_root)

    assert any("pilot_gold_labels.yaml" in error for error in errors)
    assert any("minimum_required_elements" in error for error in errors)


def test_model_response_and_scored_response_schemas_load():
    model_response_schema = load_json(ROOT / "benchmark" / "schemas" / "model_response.schema.json")
    scored_response_schema = load_json(ROOT / "benchmark" / "schemas" / "scored_response.schema.json")

    assert model_response_schema["title"] == "Model Response"
    assert scored_response_schema["title"] == "Scored Response"


def test_validate_all_reports_invalid_model_response_shape(tmp_path: Path):
    benchmark_root = tmp_path / "benchmark"
    (benchmark_root / "schemas").mkdir(parents=True)
    (benchmark_root / "responses" / "raw").mkdir(parents=True)

    for schema_name in ("sample_cluster.schema.json", "model_response.schema.json", "scored_response.schema.json"):
        (benchmark_root / "schemas" / schema_name).write_text(
            (ROOT / "benchmark" / "schemas" / schema_name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    (benchmark_root / "responses" / "raw" / "bad_response.yaml").write_text(
        """
item_id: ITEM_001
model_name: demo-model
response_text:
  - should_be_string_not_list
""".strip()
        + "\n",
        encoding="utf-8",
    )

    errors = validate_all(benchmark_root)

    assert any("bad_response.yaml" in error for error in errors)
    assert any("response_text" in error for error in errors)
