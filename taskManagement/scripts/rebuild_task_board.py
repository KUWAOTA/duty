from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"
OUTPUTS_DIR = ROOT / "outputs"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
CHECKBOX_RE = re.compile(r"^- \[( |x)\] (.+)$")

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
CLOSED_STATUSES = {"done", "cancelled"}


@dataclass
class Task:
    path: Path
    title: str
    status: str
    priority: str
    due: str
    estimate: str
    project: str
    next_action: str
    open_steps: int


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    data: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data, text[match.end() :]


def first_heading(body: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled task"


def parse_checklist(body: str) -> tuple[str, int]:
    unchecked = []
    for line in body.splitlines():
        match = CHECKBOX_RE.match(line.strip())
        if not match:
            continue
        checked, text = match.groups()
        if checked == " ":
            unchecked.append(text.strip())
    next_action = unchecked[0] if unchecked else "No remaining checklist items"
    return next_action, len(unchecked)


def load_tasks() -> list[Task]:
    tasks: list[Task] = []
    for path in sorted(TASKS_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(raw)
        title = frontmatter.get("title") or first_heading(body)
        status = (frontmatter.get("status") or "active").lower()
        if status in CLOSED_STATUSES:
            continue
        priority = (frontmatter.get("priority") or "medium").lower()
        due = frontmatter.get("due") or "-"
        estimate = frontmatter.get("estimate") or "-"
        project = frontmatter.get("project") or "-"
        next_action, open_steps = parse_checklist(body)
        tasks.append(
            Task(
                path=path,
                title=title,
                status=status,
                priority=priority,
                due=due,
                estimate=estimate,
                project=project,
                next_action=next_action,
                open_steps=open_steps,
            )
        )
    return tasks


def task_sort_key(task: Task) -> tuple[int, str, str]:
    priority_rank = PRIORITY_ORDER.get(task.priority, 9)
    due_rank = task.due if task.due != "-" else "9999-12-31"
    return priority_rank, due_rank, task.title


def format_board(tasks: list[Task]) -> str:
    today = date.today().isoformat()
    lines = [
        "# Task Board",
        "",
        f"更新日: {today}",
        "",
        "## 今やること",
        "",
    ]

    if not tasks:
        lines.append("- アクティブなタスクはありません")
    else:
        for index, task in enumerate(tasks[:5], start=1):
            lines.append(
                f"{index}. {task.title} | 優先度: {task.priority} | 期限: {task.due} | "
                f"工数: {task.estimate} | 次の一歩: {task.next_action}"
            )

    lines.extend(["", "## アクティブ一覧", ""])

    if not tasks:
        lines.append("- なし")
    else:
        for task in tasks:
            rel_path = task.path.relative_to(ROOT).as_posix()
            lines.append(
                f"- {task.title} | 状態: {task.status} | 優先度: {task.priority} | "
                f"期限: {task.due} | 工数: {task.estimate} | 未完了手順: {task.open_steps} | "
                f"プロジェクト: {task.project} | ノート: [[{rel_path[:-3]}]]"
            )

    return "\n".join(lines) + "\n"


def format_prompt(tasks: list[Task]) -> str:
    if not tasks:
        return "今日の未処理タスクはありません。必要なら新しいタスクを追加してください。\n"

    top = tasks[0]
    return (
        "PC起動時メッセージ\n"
        f"最優先: {top.title}\n"
        f"次の一歩: {top.next_action}\n"
        f"目安: {top.estimate}\n"
        f"期限: {top.due}\n"
        "終わったら taskManagement/outputs/board.md を見直してください。\n"
    )


def main() -> None:
    tasks = sorted(load_tasks(), key=task_sort_key)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUTS_DIR / "board.md").write_text(format_board(tasks), encoding="utf-8")
    (OUTPUTS_DIR / "next_prompt.txt").write_text(format_prompt(tasks), encoding="utf-8")
    print(f"Rebuilt task board with {len(tasks)} active task(s).")


if __name__ == "__main__":
    main()
