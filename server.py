"""Todo MCP — the foro.sh example project.

A small stateful MCP server: tasks live in memory for the lifetime of the
container, so tool calls in one session are visible in the next. State resets
when the server restarts or redeploys (see README).
"""

import os
from dataclasses import dataclass, field
from typing import Literal

from fastmcp import FastMCP

mcp = FastMCP(
    "todo-mcp",
    instructions=(
        "A todo list that lives in this server's memory. Add tasks, list "
        "them, complete them, delete them — state persists between calls "
        "until the server restarts."
    ),
)

Priority = Literal["low", "medium", "high"]
Status = Literal["all", "open", "done"]


@dataclass
class Task:
    id: int
    title: str
    priority: Priority
    done: bool = False


@dataclass
class Store:
    tasks: dict[int, Task] = field(default_factory=dict)
    next_id: int = 1


store = Store()


def _get(task_id: int) -> Task:
    task = store.tasks.get(task_id)
    if task is None:
        raise ValueError(f"No task with id {task_id}")
    return task


@mcp.tool
def add_task(title: str, priority: Priority = "medium") -> Task:
    """Add a task to the list and return it."""
    task = Task(id=store.next_id, title=title, priority=priority)
    store.tasks[task.id] = task
    store.next_id += 1
    return task


@mcp.tool
def list_tasks(status: Status = "all") -> list[Task]:
    """List tasks, optionally filtered to open or done ones."""
    tasks = list(store.tasks.values())
    if status == "open":
        return [t for t in tasks if not t.done]
    if status == "done":
        return [t for t in tasks if t.done]
    return tasks


@mcp.tool
def complete_task(id: int) -> Task:
    """Mark a task as done and return it."""
    task = _get(id)
    task.done = True
    return task


@mcp.tool
def delete_task(id: int) -> None:
    """Delete a task from the list."""
    _get(id)
    del store.tasks[id]


@mcp.resource("tasks://board")
def board() -> str:
    """The current task board, rendered as markdown."""
    if not store.tasks:
        return "# Task board\n\n_No tasks yet — try the `add_task` tool._"
    lines = ["# Task board", ""]
    for task in store.tasks.values():
        box = "x" if task.done else " "
        lines.append(f"- [{box}] #{task.id} {task.title} ({task.priority})")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.environ.get("MCP_PORT", "8000")),
        # FastMCP's host/origin protection guards local dev servers against
        # DNS rebinding by rejecting Hosts it doesn't expect (HTTP 421). On
        # foro.sh the server sits behind a reverse proxy and requests arrive
        # with the public hostname, so this must be off — access control is
        # the platform's bearer token instead.
        host_origin_protection=False,
    )
