---
name: plan-my-day
description: Turn the open tasks on the todo board into a short, ordered plan for today.
---

# Plan my day

1. Call `list_tasks` with `status: "open"`.
2. If the user mentions work that is not on the board, `add_task` it first
   so the plan and the board agree.
3. Pick at most five tasks: every `high` task first, then `medium`, oldest
   (lowest id) first within each level. Leave `low` tasks out unless the
   list is otherwise short.
4. Present the plan as a numbered list with each task's id, so the user can
   say "done with 3" and you can `complete_task` it.
5. If more than five tasks qualified, say how many were left out and why.
