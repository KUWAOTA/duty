# Task Management

This vault uses `taskManagement/` as the daily task system.

## Structure

- `tasks/`: one markdown note per task
- `outputs/board.md`: generated board for Obsidian
- `outputs/next_prompt.txt`: generated short startup prompt
- `scripts/rebuild_task_board.py`: rebuild generated outputs
- `scripts/show_startup_brief.ps1`: print the current startup reminder

## Operating Rules

1. Add one note per task in `tasks/`.
2. Keep actionable work as checklist items.
3. Regenerate outputs after edits.
4. Read `outputs/board.md` when deciding what to do next.

## Commands

```powershell
python taskManagement/scripts/rebuild_task_board.py
powershell -ExecutionPolicy Bypass -File taskManagement/scripts/show_startup_brief.ps1
```

## Optional Startup Hook

If you want this message on Windows startup later, use `taskManagement/scripts/install_startup_brief.ps1`.
That installer writes a shortcut into the current user's Startup folder, so run it only when you want the behavior enabled.
