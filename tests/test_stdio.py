"""The server must answer initialize and tools/list over stdio with no Diffbot token.

A token is required only when a tool is called. This is the check a container
health probe runs: boot the process, initialize, and list tools.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "diffbot_mcp_server.py"

# Every tool registered in diffbot_mcp.server. The server has twelve.
EXPECTED_TOOLS = {
    "extract",
    "search_web",
    "search_news",
    "search_organizations",
    "search_people",
    "search_places",
    "search_deals",
    "crawl",
    "resolve_entities",
    "dql",
    "dql_ontology",
    "dql_probe",
}

READ_ONLY = {
    "read_only_hint": True,
    "destructive_hint": False,
    "idempotent_hint": True,
    "open_world_hint": True,
}

# start spends credits and is not idempotent; delete removes the job and its pages.
CRAWL = {
    "read_only_hint": False,
    "destructive_hint": True,
    "idempotent_hint": False,
    "open_world_hint": True,
}


def test_stdio_lists_tools_without_a_token():
    asyncio.run(_stdio_lists_tools_without_a_token())


async def _stdio_lists_tools_without_a_token():
    # The stdio client inherits HOME. Point it at an empty directory so a
    # developer credential file cannot satisfy resolve_token.
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryFile(mode="w+") as errlog:
        params = StdioServerParameters(
            command=sys.executable,
            args=[str(SERVER)],
            cwd=str(ROOT),
            env={
                "HOME": home,
                "PATH": os.environ.get("PATH", ""),
                "DIFFBOT_TOKEN": "",
                "DIFFBOT_API_TOKEN": "",
                "DIFFBOT_OAUTH_ISSUER": "",
            },
        )
        async with stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                init = await asyncio.wait_for(session.initialize(), timeout=30)
                assert init.server_info.name == "Diffbot MCP Server"

                listed = await asyncio.wait_for(session.list_tools(), timeout=30)
                names = [tool.name for tool in listed.tools]
                assert names == [
                    "extract",
                    "search_web",
                    "search_news",
                    "search_organizations",
                    "search_people",
                    "search_places",
                    "search_deals",
                    "crawl",
                    "resolve_entities",
                    "dql",
                    "dql_ontology",
                    "dql_probe",
                ]
                assert set(names) == EXPECTED_TOOLS

                for tool in listed.tools:
                    assert tool.description
                    hints = tool.annotations.model_dump() if tool.annotations else {}
                    expected = CRAWL if tool.name == "crawl" else READ_ONLY
                    for key, value in expected.items():
                        assert hints.get(key) is value, f"{tool.name} {key}={hints.get(key)!r}"

                result = await asyncio.wait_for(
                    session.call_tool("dql", {"query": 'type:Organization name:"Diffbot"'}),
                    timeout=30,
                )
                assert result.is_error
                text = result.content[0].text if result.content else ""
                assert "No Diffbot token" in text
