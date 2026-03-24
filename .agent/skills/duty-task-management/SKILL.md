---
name: duty-task-management
description: Manage daily tasks inside the duty Obsidian vault, surface what to do next, update the local task board, or prepare a startup reminder message. Use when asked to recall pending tasks, register a new task, reprioritize work, or refresh the board in this vault.
---

# Duty Task Management

Use the local `taskManagement` directory as the single task system for this vault.

## Follow This Workflow

1. Read `taskManagement/README.md` for the current layout if needed.
2. Add or edit one note per task under `taskManagement/tasks/`.
3. Keep frontmatter small and explicit:
   - `title`
   - `status`
   - `priority`
   - `due`
   - `estimate`
   - `project`
4. Put the concrete execution steps in markdown checklists inside the task note.
5. Run `python taskManagement/scripts/rebuild_task_board.py` after changes.
6. For a startup-facing reminder, run `powershell -ExecutionPolicy Bypass -File taskManagement/scripts/show_startup_brief.ps1`.

## Conventions

- Treat `status: active` as actionable.
- Treat `status: waiting` as blocked but still visible.
- Treat `status: done` and `status: cancelled` as closed.
- Use the first unchecked checklist item as the next action whenever possible.
- Do not hand-edit `taskManagement/outputs/board.md` or `taskManagement/outputs/next_prompt.txt`; regenerate them.

## Response Pattern

When asked what to do now, answer from `taskManagement/outputs/board.md` first.
When asked to add a task, create or update a note in `taskManagement/tasks/` and regenerate outputs.
