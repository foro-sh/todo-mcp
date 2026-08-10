"""Todo MCP — the foro.sh example project.

A small stateful MCP server: tasks live in memory for the lifetime of the
container, so tool calls in one session are visible in the next. State resets
when the server restarts or redeploys (see README).
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.apps import AppConfig, ResourceCSP, app_config_to_meta_dict
from pydantic import Field

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

# Every parameter without a default carries an `examples` entry, so a client
# that pre-fills a call from the schema — foro.sh's Playground does — starts
# from something worth running rather than a bare `""` / `0`. Parameters with a
# default need none: the default is already the example.
TaskTitle = Annotated[str, Field(examples=["Buy milk"])]
TaskId = Annotated[int, Field(examples=[1])]


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

# MCP Apps (https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/):
# a tool points at a `ui://` resource, the host renders that resource in a
# sandboxed iframe next to the tool result. `todo_app` goes on the tools;
# the csp/permissions half of the config belongs on the resource itself.
TODO_UI = "ui://todo/list"
todo_app = AppConfig(resource_uri=TODO_UI)

# view.html pulls the MCP Apps SDK off a CDN. The host builds the iframe's
# Content-Security-Policy from this declaration, so an undeclared origin means
# a blocked script and a blank view.
UI_RESOURCE_META = {
    "ui": app_config_to_meta_dict(
        AppConfig(csp=ResourceCSP(resource_domains=["https://unpkg.com"]))
    )
}


@mcp.resource(TODO_UI, meta=UI_RESOURCE_META)
def todo_view() -> str:
    """The interactive todo list, rendered by the host in an iframe."""
    # `ui://` resources default to the mime type MCP Apps expects
    # (text/html;profile=mcp-app), so it needs no `mime_type=`.
    return (Path(__file__).parent / "view.html").read_text()


def _get(task_id: int) -> Task:
    task = store.tasks.get(task_id)
    if task is None:
        raise ValueError(f"No task with id {task_id}")
    return task


@mcp.tool(app=todo_app)
def add_task(title: TaskTitle, priority: Priority = "medium") -> Task:
    """Add a task to the list and return it."""
    task = Task(id=store.next_id, title=title, priority=priority)
    store.tasks[task.id] = task
    store.next_id += 1
    return task


@mcp.tool(app=todo_app)
def list_tasks(status: Status = "all") -> list[Task]:
    """List tasks, optionally filtered to open or done ones."""
    tasks = list(store.tasks.values())
    if status == "open":
        return [t for t in tasks if not t.done]
    if status == "done":
        return [t for t in tasks if t.done]
    return tasks


@mcp.tool(app=todo_app)
def complete_task(id: TaskId) -> Task:
    """Mark a task as done and return it."""
    task = _get(id)
    task.done = True
    return task


@mcp.tool(app=todo_app)
def reopen_task(id: TaskId) -> Task:
    """Mark a task as not done and return it."""
    task = _get(id)
    task.done = False
    return task


@mcp.tool(app=todo_app)
def delete_task(id: TaskId) -> None:
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
