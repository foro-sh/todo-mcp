"""Check the skills extension: declared, listed over HTTP, files readable.

    uv run test_skills.py
"""

import asyncio
import hashlib

import httpx
from fastmcp import Client

from server import HTTP_MIDDLEWARE, SKILLS_EXTENSION, mcp


async def main() -> None:
    async with Client(mcp) as client:
        caps = client.initialize_result.capabilities
        assert SKILLS_EXTENSION in (caps.model_extra or {})["extensions"], caps
        assert caps.resources is not None

        app = mcp.http_app(middleware=HTTP_MIDDLEWARE)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://t") as http:
            res = await http.post(
                "/mcp",
                json={"jsonrpc": "2.0", "id": 7, "method": "skills/list", "params": {}},
                headers={"accept": "application/json, text/event-stream"},
            )
        body = res.json()
        assert body["id"] == 7, body
        skills = {s["frontmatter"]["name"]: s for s in body["result"]["skills"]}
        assert set(skills) == {"plan-my-day", "triage-tasks"}, skills

        for name, skill in skills.items():
            # The spec: the URI's skill folder matches the frontmatter name.
            assert skill["uri"] == f"skill://{name}/SKILL.md"
            assert skill["frontmatter"]["description"]
            for file in skill["resources"]:
                text = (await client.read_resource(file["uri"]))[0].text
                data = text.encode()
                assert file["size"] == len(data), file
                assert file["digest"] == "sha256:" + hashlib.sha256(data).hexdigest(), file

        assert len(skills["triage-tasks"]["resources"]) == 2

    print("ok")


if __name__ == "__main__":
    asyncio.run(main())
