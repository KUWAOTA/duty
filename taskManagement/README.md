# Task Management

## 会話での使い方

「次なにやればいい？」でボードを再生成し、実行可能な用事を期限順・優先度順に案内します。新しい用事や進捗は会話から各タスクに反映します。

旧 `task/` の `tasks`・`master`・`daily`・`input`・`output`・`prompt` はここへ統合しました。`output/` は既存資料、`outputs/` は自動生成ボードです。

`needs_review` は過去の記録の現状確認待ち、`waiting` は外部待ちです。完了と推定せず、現在実行する候補からは外しています。旧週間予定は `master/schedule.md` に保存しています。

原付探しは2026-10-09期限、暫定3日おき。`next_review` 当日以降に候補へ戻ります。確認報告時にログを残し、報告日＋`repeat_days` と期限の早い方へ次回日を更新します。自動通知は設定していません。

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
