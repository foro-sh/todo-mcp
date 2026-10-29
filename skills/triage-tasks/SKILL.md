---
name: triage-tasks
description: Clean up the todo board - close finished work, merge duplicates and re-rank priorities with this server's tools.
---

# Triage the task board

Use this when the list has grown messy: stale tasks, duplicates, or
everything marked `high`.

1. Call `list_tasks` with `status: "open"` to see what is still pending.
2. Ask the user which of those are already done, then `complete_task` each.
3. Look for duplicates (the same task worded twice). Keep the clearest
   title and `delete_task` the rest. Confirm before deleting.
4. Re-rank what is left using [priority-rubric.md](priority-rubric.md).
   This server has no update tool, so to change a priority, `add_task` the
   task again with the new priority and `delete_task` the old one.
5. Finish with `list_tasks` and summarise the board in a few lines.

Never delete a task the user has not confirmed. State lives in the
server's memory, so a deleted task cannot be recovered.
