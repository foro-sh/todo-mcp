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
| `reopen_task(id)` | Mark a task as not done |
| `delete_task(id)` | Delete a task |

It also exposes two resources: `tasks://board`, the current board rendered as
markdown, and `ui://todo/list`, the interactive view described below.

## The interactive view

Every todo tool carries `_meta.ui.resourceUri` pointing at `ui://todo/list`,
per the [MCP Apps extension][apps]. A host that supports the extension fetches
that resource — `view.html`, served as `text/html;profile=mcp-app` — and
renders it in a sandboxed iframe beside the tool result: a checkbox list you
can tick to complete and untick to reopen.

The view talks back over `postMessage` using
[`@modelcontextprotocol/ext-apps`][sdk]: `callServerTool` to mutate the list,
`updateModelContext` to tell the model what is on screen, and `ontoolresult`
to re-render when the model changes the list itself. Because that SDK loads
from a CDN, the resource declares `unpkg.com` under `_meta.ui.csp` — hosts
build the iframe's Content-Security-Policy from that, and an undeclared origin
means a blank view.

Hosts without the extension are unaffected: they ignore the metadata and show
the plain tool results.

[apps]: https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/
[sdk]: https://github.com/modelcontextprotocol/ext-apps

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
