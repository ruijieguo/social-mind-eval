from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "render_taxonomy_report.py"
SPEC = importlib.util.spec_from_file_location("render_taxonomy_report", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

load_taxonomy = MODULE.load_taxonomy
render_markdown_summary = MODULE.render_markdown_summary


def test_taxonomy_has_six_top_level_dimensions():
    taxonomy_path = (
        Path(__file__).resolve().parents[1]
        / "benchmark"
        / "taxonomy"
        / "social_mind_dimensions.yaml"
    )
    taxonomy = load_taxonomy(taxonomy_path)
    first_dimension = taxonomy["dimensions"][0]

    assert len(taxonomy["dimensions"]) == 6
    assert first_dimension["id"] == "1"
    assert taxonomy["dimensions"][5]["id"] == "6"
    assert {"name", "core_question", "subdimensions"} <= first_dimension.keys()


def test_render_markdown_summary_uses_expected_markdown_structure():
    taxonomy_path = (
        Path(__file__).resolve().parents[1]
        / "benchmark"
        / "taxonomy"
        / "social_mind_dimensions.yaml"
    )

    summary = render_markdown_summary(taxonomy_path)

    assert summary.startswith("# social-mind-eval-taxonomy\n")
    assert "## 1. 社会语境构型" in summary
    assert "核心问题：这是什么局" in summary
    assert "- 1.1 情境类型与互动阶段识别 (T1)" in summary
    assert "## 6. 社会回应生成" in summary
    assert "核心问题：具体怎么说" in summary


def test_taxonomy_includes_full_spec_key_dimensions():
    taxonomy_path = ROOT / "benchmark" / "taxonomy" / "social_mind_dimensions.yaml"
    taxonomy = load_taxonomy(taxonomy_path)

    capability_ids = {
        capability["id"]
        for dimension in taxonomy["dimensions"]
        for subdimension in dimension["subdimensions"]
        for capability in subdimension["capabilities"]
    }

    assert "1.3.1" in capability_ids
    assert "2.4.6" in capability_ids
    assert "3.5.6" in capability_ids
    assert "4.4.5" in capability_ids
    assert "5.3.5" in capability_ids
    assert "6.5.5" in capability_ids
