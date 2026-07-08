# todo-mcp

The [foro.sh](https://foro.sh) example project: a small, stateful todo-list
MCP server. Every new foro.sh workspace gets a deployed copy, so there is a
live MCP endpoint to poke at before deploying anything of your own.

## Tools

| Tool | Description |
| --- | --- |
| `add_task(title, priority)` | Add a task (`low` / `medium` / `high`, default `medium`) |
| `list_tasks(status)` | List tasks (`all` / `open` / `done`, default `all`) |
| `complete_task(id)` | Mark a task as done |
| `delete_task(id)` | Delete a task |

It also exposes one resource, `tasks://board` — the current board rendered as
markdown.

## State

Tasks live in the server's memory. That is the point of the example: a tool
call in one session mutates state the next call sees, because the container
keeps running between calls. The ceiling is just as real: state resets
whenever the server restarts or redeploys. For anything that must survive a
restart, back your server with a database or external store.

## Run it locally

```sh
uv run server.py
```

The server speaks MCP over streamable HTTP at `http://localhost:8000/mcp`
(set `MCP_PORT` to change the port).

## Deploy it

This repo carries a `foro.yaml`, so it deploys on foro.sh as-is: sign in,
pick this repo, deploy.
