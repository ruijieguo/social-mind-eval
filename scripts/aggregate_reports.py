from __future__ import annotations

from collections import defaultdict
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

import yaml


TOP_DIMENSION_NAMES = {
    "1": "社会语境构型",
    "2": "多主体心智建模",
    "3": "社会机制理解",
    "4": "社会动态推演",
    "5": "规范与价值裁决",
    "6": "社会回应生成",
}

SECOND_DIMENSION_NAMES = {
    "1.1": "情境类型与互动阶段识别",
    "1.2": "角色关系与权力结构解析",
    "1.3": "公开性、受众与边界条件识别",
    "1.4": "语用锚点与表层偏离识别",
    "1.5": "事实约束与制度语境锚定",
    "2.1": "认知状态与知识边界建模",
    "2.2": "意图、动机与目标结构建模",
    "2.3": "情绪、情感与立场建模",
    "2.4": "信任、承诺与真实性建模",
    "2.5": "偏好、人格与元认知建模",
    "3.1": "面子、礼貌与印象管理机制",
    "3.2": "责任归因与解释机制",
    "3.3": "信任、操纵与博弈机制",
    "3.4": "身份、角色与规范激活机制",
    "3.5": "群体影响与结构约束机制",
    "3.6": "联盟、边界与群体关系机制",
    "4.1": "社会状态更新与时序演化",
    "4.2": "对话与协商路径推演",
    "4.3": "冲突、升级与去升级推演",
    "4.4": "群体与制度动态推演",
    "4.5": "因果、干预与反事实推演",
    "5.1": "规范识别与违背判断",
    "5.2": "公平、责任与程序正义裁决",
    "5.3": "诚实、忠诚与伤害控制裁决",
    "5.4": "权力、尊重与体面边界裁决",
    "5.5": "多元规范与跨文化裁决",
    "6.1": "受众适配与表达调节",
    "6.2": "支持、确认与边界表达",
    "6.3": "协商、说服与协调生成",
    "6.4": "冲突修复与信任重建生成",
    "6.5": "防御、纠偏与抗操纵生成",
}

DEFAULT_SCORED_RESPONSES_DIR = Path("benchmark/responses/scored")
DEFAULT_OUTPUT_PATH = Path("benchmark/reports/social_mind_profile.md")
DEFAULT_GOLD_LABELS_PATH = Path("benchmark/pilot/labels/pilot_gold_labels.yaml")


def load_scored_responses(scored_dir: Path) -> list[dict[str, Any]]:
    responses: list[dict[str, Any]] = []
    for path in sorted(scored_dir.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as handle:
            responses.append(yaml.safe_load(handle))
    return responses


def load_gold_labels(labels_path: Path) -> dict[str, dict[str, Any]]:
    with labels_path.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)

    labels = document.get("labels", []) if isinstance(document, dict) else []
    return {str(label["item_id"]): label for label in labels if isinstance(label, dict) and "item_id" in label}


def aggregate_scores_by_top_dimension(scored_responses: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for response in scored_responses:
        top_dimension = str(response["dimension"]).split(".", 1)[0]
        grouped[top_dimension].append(response)

    summary: dict[str, dict[str, Any]] = {}
    for dimension_id, responses in grouped.items():
        score_names = responses[0]["scores"].keys()
        avg_scores = {
            score_name: mean(response["scores"][score_name] for response in responses)
            for score_name in score_names
        }
        summary[dimension_id] = {
            "name": TOP_DIMENSION_NAMES.get(dimension_id, dimension_id),
            "count": len(responses),
            "avg_scores": avg_scores,
        }
    return summary


def aggregate_scores_by_second_dimension(scored_responses: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for response in scored_responses:
        parts = str(response["dimension"]).split(".")
        second_dimension = ".".join(parts[:2])
        grouped[second_dimension].append(response)

    summary: dict[str, dict[str, Any]] = {}
    for dimension_id, responses in grouped.items():
        score_names = responses[0]["scores"].keys()
        avg_scores = {
            score_name: mean(response["scores"][score_name] for response in responses)
            for score_name in score_names
        }
        summary[dimension_id] = {
            "name": SECOND_DIMENSION_NAMES.get(dimension_id, dimension_id),
            "count": len(responses),
            "avg_scores": avg_scores,
        }
    return summary


def render_profile_report(
    model_name: str,
    scored_responses: list[dict[str, Any]],
    gold_labels: dict[str, dict[str, Any]] | None = None,
) -> str:
    summary = aggregate_scores_by_top_dimension(scored_responses)
    second_level_summary = aggregate_scores_by_second_dimension(scored_responses)
    lines = [f"# Social Mind Evaluation Report: {model_name}", "", "## Top-Level Dimension Profile"]

    for dimension_id in sorted(summary.keys(), key=int):
        entry = summary[dimension_id]
        avg_scores = entry["avg_scores"]
        lines.append(
            f"- {dimension_id} {entry['name']}: count={entry['count']}, "
            f"state={avg_scores.get('state_correctness', 0):.2f}, "
            f"norm={avg_scores.get('normative_judgment', 0):.2f}, "
            f"response={avg_scores.get('response_quality', 0):.2f}"
        )

    lines.extend(["", "## Second-Level Dimension Profile"])
    for dimension_id in sorted(second_level_summary.keys(), key=lambda value: [int(part) for part in value.split(".")]):
        entry = second_level_summary[dimension_id]
        avg_scores = entry["avg_scores"]
        lines.append(
            f"- {dimension_id} {entry['name']}: count={entry['count']}, "
            f"state={avg_scores.get('state_correctness', 0):.2f}, "
            f"norm={avg_scores.get('normative_judgment', 0):.2f}, "
            f"response={avg_scores.get('response_quality', 0):.2f}"
        )

    lines.extend(["", "## Risk Signals"])
    low_norm_dimensions = [
        f"{dimension_id} {entry['name']}"
        for dimension_id, entry in summary.items()
        if entry["avg_scores"].get("normative_judgment", 1.0) < 0.5
    ]

    if low_norm_dimensions:
        for label in sorted(low_norm_dimensions):
            lines.append(f"- Elevated normative risk: {label}")
    else:
        lines.append("- No elevated normative risk signals detected in the current sample.")

    lines.extend(["", "## Failure Buckets by Second-Level Dimension"])
    bucketed_failures: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for response in scored_responses:
        if response["scores"].get("state_correctness", 1.0) < 0.5:
            second_dimension = ".".join(str(response["dimension"]).split(".")[:2])
            bucketed_failures[second_dimension].append(response)

    if bucketed_failures:
        for dimension_id in sorted(bucketed_failures.keys(), key=lambda value: [int(part) for part in value.split(".")]):
            responses = bucketed_failures[dimension_id]
            lines.append(
                f"- {dimension_id} {SECOND_DIMENSION_NAMES.get(dimension_id, dimension_id)}: count={len(responses)}"
            )
            if gold_labels:
                failure_counter: Counter[str] = Counter()
                for response in responses:
                    label = gold_labels.get(str(response["item_id"]))
                    if label:
                        for failure_mode in label.get("common_failure_mode", []):
                            failure_counter[failure_mode] += 1
                for failure_mode, count in failure_counter.most_common(2):
                    lines.append(f"  - {count}x {failure_mode}")
    else:
        lines.append("- No second-level failure buckets detected in the current sample.")

    lines.extend(["", "## Failure Patterns"])
    low_state_items = [
        response
        for response in scored_responses
        if response["scores"].get("state_correctness", 1.0) < 0.5
    ]
    if low_state_items:
        for response in low_state_items:
            item_id = str(response["item_id"])
            label = gold_labels.get(item_id) if gold_labels else None
            common_failure_mode = None
            missing_elements = None

            if label:
                failure_modes = label.get("common_failure_mode", [])
                if failure_modes:
                    common_failure_mode = failure_modes[0]
                minimum_required = label.get("minimum_required_elements", [])
                if minimum_required:
                    missing_elements = "; ".join(minimum_required[:2])

            line = f"- {item_id} ({response['dimension']}): low state correctness; review latent-state tracking."
            if missing_elements:
                line += f" Missing expected elements: {missing_elements}."
            if common_failure_mode:
                line += f" Common failure mode: {common_failure_mode}."
            lines.append(line)
    else:
        lines.append("- No major low-state-correctness failure patterns detected in the current sample.")

    return "\n".join(lines)


def main(write_to_file: bool = False) -> None:
    scored_responses = load_scored_responses(DEFAULT_SCORED_RESPONSES_DIR)
    if not scored_responses:
        report = "# Social Mind Evaluation Report: no-data\n\nNo scored responses found."
        if write_to_file:
            DEFAULT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            DEFAULT_OUTPUT_PATH.write_text(report + "\n", encoding="utf-8")
        print(report)
        return

    model_name = str(scored_responses[0].get("model_name", "unknown-model"))
    gold_labels = load_gold_labels(DEFAULT_GOLD_LABELS_PATH) if DEFAULT_GOLD_LABELS_PATH.exists() else None
    report = render_profile_report(model_name, scored_responses, gold_labels=gold_labels)
    if write_to_file:
        DEFAULT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_OUTPUT_PATH.write_text(report + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
