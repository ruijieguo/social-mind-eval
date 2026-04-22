from pathlib import Path

import yaml


DEFAULT_TAXONOMY_PATH = Path("benchmark/taxonomy/social_mind_dimensions.yaml")


def load_taxonomy(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def render_markdown_summary(path: Path) -> str:
    taxonomy = load_taxonomy(path)
    lines = [f"# {taxonomy['name']}", ""]

    for dimension in taxonomy["dimensions"]:
        lines.append(f"## {dimension['id']}. {dimension['name']}")
        lines.append(f"核心问题：{dimension['core_question']}")
        for subdimension in dimension["subdimensions"]:
            lines.append(
                f"- {subdimension['id']} {subdimension['name']} ({subdimension['task_family']})"
            )
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    print(render_markdown_summary(DEFAULT_TAXONOMY_PATH))


if __name__ == "__main__":
    main()
