from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "aggregate_reports.py"
SPEC = importlib.util.spec_from_file_location("aggregate_reports", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

aggregate_scores_by_top_dimension = MODULE.aggregate_scores_by_top_dimension
aggregate_scores_by_second_dimension = MODULE.aggregate_scores_by_second_dimension
load_scored_responses = MODULE.load_scored_responses
load_gold_labels = MODULE.load_gold_labels
render_profile_report = MODULE.render_profile_report


def test_aggregate_scores_by_top_dimension_groups_scores_correctly():
    scored_responses = [
        {
            "item_id": "ITEM_1",
            "model_name": "demo-model",
            "dimension": "5.4.3",
            "scores": {
                "state_correctness": 1.0,
                "normative_judgment": 0.5,
                "response_quality": 0.5,
            },
        },
        {
            "item_id": "ITEM_2",
            "model_name": "demo-model",
            "dimension": "5.3.5",
            "scores": {
                "state_correctness": 0.5,
                "normative_judgment": 1.0,
                "response_quality": 0.5,
            },
        },
        {
            "item_id": "ITEM_3",
            "model_name": "demo-model",
            "dimension": "6.5.5",
            "scores": {
                "state_correctness": 0.5,
                "normative_judgment": 0.5,
                "response_quality": 1.0,
            },
        },
    ]

    summary = aggregate_scores_by_top_dimension(scored_responses)

    assert summary["5"]["count"] == 2
    assert summary["6"]["count"] == 1
    assert summary["5"]["avg_scores"]["normative_judgment"] == 0.75
    assert summary["6"]["avg_scores"]["response_quality"] == 1.0


def test_render_profile_report_outputs_dimension_profile_sections():
    scored_responses = [
        {
            "item_id": "ITEM_1",
            "model_name": "demo-model",
            "dimension": "4.3.2",
            "scores": {
                "state_correctness": 0.5,
                "normative_judgment": 0.0,
                "response_quality": 0.5,
            },
        },
        {
            "item_id": "ITEM_2",
            "model_name": "demo-model",
            "dimension": "5.4.3",
            "scores": {
                "state_correctness": 1.0,
                "normative_judgment": 1.0,
                "response_quality": 0.5,
            },
        },
    ]

    report = render_profile_report("demo-model", scored_responses)

    assert report.startswith("# Social Mind Evaluation Report: demo-model")
    assert "## Top-Level Dimension Profile" in report
    assert "- 4 社会动态推演" in report
    assert "- 5 规范与价值裁决" in report
    assert "## Risk Signals" in report


def test_load_scored_responses_reads_yaml_files_from_directory(tmp_path: Path):
    scored_dir = tmp_path / "scored"
    scored_dir.mkdir()
    (scored_dir / "response_a.yaml").write_text(
        """
item_id: ITEM_1
model_name: demo-model
dimension: 5.4.3
response_text: Example response
scores:
  state_correctness: 1.0
  normative_judgment: 0.5
  response_quality: 0.5
""".strip()
        + "\n",
        encoding="utf-8",
    )

    responses = load_scored_responses(scored_dir)

    assert len(responses) == 1
    assert responses[0]["item_id"] == "ITEM_1"
    assert responses[0]["scores"]["normative_judgment"] == 0.5


def test_main_writes_report_from_scored_response_directory(tmp_path: Path, monkeypatch, capsys):
    scored_dir = tmp_path / "scored"
    scored_dir.mkdir()
    (scored_dir / "response_a.yaml").write_text(
        """
item_id: ITEM_1
model_name: demo-model
dimension: 6.5.5
response_text: Example response
scores:
  state_correctness: 0.5
  normative_judgment: 0.5
  response_quality: 1.0
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(MODULE, "DEFAULT_SCORED_RESPONSES_DIR", scored_dir)
    MODULE.main()
    output = capsys.readouterr().out

    assert output.startswith("# Social Mind Evaluation Report: demo-model")
    assert "6 社会回应生成" in output


def test_aggregate_scores_by_second_dimension_groups_scores_correctly():
    scored_responses = [
        {
            "item_id": "ITEM_1",
            "model_name": "demo-model",
            "dimension": "5.4.3",
            "scores": {
                "state_correctness": 1.0,
                "normative_judgment": 0.5,
                "response_quality": 0.5,
            },
        },
        {
            "item_id": "ITEM_2",
            "model_name": "demo-model",
            "dimension": "5.4.1",
            "scores": {
                "state_correctness": 0.5,
                "normative_judgment": 1.0,
                "response_quality": 0.5,
            },
        },
        {
            "item_id": "ITEM_3",
            "model_name": "demo-model",
            "dimension": "6.5.5",
            "scores": {
                "state_correctness": 0.5,
                "normative_judgment": 0.5,
                "response_quality": 1.0,
            },
        },
    ]

    summary = aggregate_scores_by_second_dimension(scored_responses)

    assert summary["5.4"]["count"] == 2
    assert summary["6.5"]["count"] == 1
    assert summary["5.4"]["avg_scores"]["state_correctness"] == 0.75


def test_render_profile_report_includes_second_level_profile_and_failure_summary():
    scored_responses = [
        {
            "item_id": "ITEM_1",
            "model_name": "demo-model",
            "dimension": "4.3.2",
            "response_text": "Generic answer",
            "scores": {
                "state_correctness": 0.0,
                "normative_judgment": 0.0,
                "response_quality": 0.5,
            },
        },
        {
            "item_id": "ITEM_2",
            "model_name": "demo-model",
            "dimension": "5.4.3",
            "response_text": "Boundary-aware answer",
            "scores": {
                "state_correctness": 1.0,
                "normative_judgment": 1.0,
                "response_quality": 0.5,
            },
        },
    ]

    report = render_profile_report("demo-model", scored_responses)

    assert "## Second-Level Dimension Profile" in report
    assert "- 4.3 冲突、升级与去升级推演" in report
    assert "## Failure Patterns" in report
    assert "4.3.2" in report


def test_main_can_write_report_to_output_file(tmp_path: Path, monkeypatch):
    scored_dir = tmp_path / "scored"
    scored_dir.mkdir()
    output_path = tmp_path / "report.md"
    (scored_dir / "response_a.yaml").write_text(
        """
item_id: ITEM_1
model_name: demo-model
dimension: 5.4.3
response_text: Example response
scores:
  state_correctness: 1.0
  normative_judgment: 1.0
  response_quality: 0.5
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(MODULE, "DEFAULT_SCORED_RESPONSES_DIR", scored_dir)
    monkeypatch.setattr(MODULE, "DEFAULT_OUTPUT_PATH", output_path)
    MODULE.main(write_to_file=True)

    written = output_path.read_text(encoding="utf-8")
    assert written.startswith("# Social Mind Evaluation Report: demo-model")
    assert "## Top-Level Dimension Profile" in written


def test_load_gold_labels_reads_label_index(tmp_path: Path):
    labels_path = tmp_path / "pilot_gold_labels.yaml"
    labels_path.write_text(
        """
labels:
  - item_id: ITEM_1
    dimension: 4.3.2
    task_type: T3
    minimum_required_elements:
      - identify two escalation paths
    common_failure_mode:
      - predicts only generic worsening
""".strip()
        + "\n",
        encoding="utf-8",
    )

    label_index = load_gold_labels(labels_path)

    assert "ITEM_1" in label_index
    assert label_index["ITEM_1"]["dimension"] == "4.3.2"


def test_render_profile_report_includes_label_informed_failure_reasons():
    scored_responses = [
        {
            "item_id": "ITEM_1",
            "model_name": "demo-model",
            "dimension": "4.3.2",
            "response_text": "This will get worse.",
            "scores": {
                "state_correctness": 0.0,
                "normative_judgment": 0.0,
                "response_quality": 0.5,
            },
        }
    ]
    gold_labels = {
        "ITEM_1": {
            "item_id": "ITEM_1",
            "dimension": "4.3.2",
            "task_type": "T3",
            "minimum_required_elements": [
                "identify two distinct likely escalation paths",
                "include alliance formation or reputation hardening",
            ],
            "common_failure_mode": [
                "predicts only a generic worsening of tone without specifying path structure"
            ],
        }
    }

    report = render_profile_report("demo-model", scored_responses, gold_labels=gold_labels)

    assert "## Failure Patterns" in report
    assert "Missing expected elements" in report
    assert "predicts only a generic worsening of tone without specifying path structure" in report


def test_render_profile_report_includes_second_level_failure_buckets():
    scored_responses = [
        {
            "item_id": "ITEM_1",
            "model_name": "demo-model",
            "dimension": "4.3.2",
            "response_text": "This will get worse.",
            "scores": {
                "state_correctness": 0.0,
                "normative_judgment": 0.0,
                "response_quality": 0.5,
            },
        },
        {
            "item_id": "ITEM_2",
            "model_name": "demo-model",
            "dimension": "4.3.3",
            "response_text": "Try to calm them down.",
            "scores": {
                "state_correctness": 0.0,
                "normative_judgment": 0.5,
                "response_quality": 0.5,
            },
        },
    ]
    gold_labels = {
        "ITEM_1": {
            "item_id": "ITEM_1",
            "dimension": "4.3.2",
            "task_type": "T3",
            "minimum_required_elements": ["identify two distinct escalation paths"],
            "common_failure_mode": ["predicts only a generic worsening of tone without specifying path structure"],
        },
        "ITEM_2": {
            "item_id": "ITEM_2",
            "dimension": "4.3.3",
            "task_type": "T3",
            "minimum_required_elements": ["identify a realistic de-escalation window"],
            "common_failure_mode": ["jumps to advice without locating the window of intervention"],
        },
    }

    report = render_profile_report("demo-model", scored_responses, gold_labels=gold_labels)

    assert "## Failure Buckets by Second-Level Dimension" in report
    assert "- 4.3 冲突、升级与去升级推演" in report
    assert "count=2" in report
    assert "generic worsening of tone" in report
