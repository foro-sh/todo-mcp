"""Check the MCP Apps wiring: tools point at the view, the view is served.

    uv run test_ui.py
"""

import asyncio
import re

from fastmcp import Client

from server import TODO_UI, mcp


async def main() -> None:
    async with Client(mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
        for name in ("add_task", "list_tasks", "complete_task", "reopen_task", "delete_task"):
            assert tools[name].meta["ui"]["resourceUri"] == TODO_UI, name

        # The view calls this on un-checking a box; it used to not exist.
        await client.call_tool("add_task", {"title": "Buy milk"})
        await client.call_tool("complete_task", {"id": 1})
        assert (await client.call_tool("reopen_task", {"id": 1})).data.done is False

        resource = next(r for r in await client.list_resources() if str(r.uri) == TODO_UI)
        assert resource.mimeType == "text/html;profile=mcp-app", resource.mimeType
        assert resource.meta["ui"]["csp"]["resourceDomains"] == ["https://unpkg.com"]

        html = (await client.read_resource(TODO_UI))[0].text
        assert "ext-apps" in html and "callServerTool" in html
        # Every tool the view calls by name must actually exist on the server.
        for name in re.findall(r'name: "(\w+)"', html) + ["complete_task", "reopen_task"]:
            assert name in tools, f"view.html calls missing tool {name}"

    print("ok")


if __name__ == "__main__":
    asyncio.run(main())
