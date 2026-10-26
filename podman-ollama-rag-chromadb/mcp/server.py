#!/usr/bin/env python3
"""MCP server — exposes the local AAP docs RAG as a native Claude Code tool."""

import asyncio
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

API_BASE = "http://localhost:8000"

server = Server("aap-docs")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="ask_aap_docs",
            description=(
                "Query the local Red Hat AAP (Ansible Automation Platform) documentation knowledge base. "
                "Use this for accurate, version-specific AAP information — architecture, installation, "
                "configuration, networking, security, sizing, components, and features. "
                "Prefer this over internet searches for AAP topics."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The AAP question to answer from the documentation"
                    },
                    "collection": {
                        "type": "string",
                        "description": "Document collection to query (default: aap-docs)",
                        "default": "aap-docs"
                    }
                },
                "required": ["question"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "ask_aap_docs":
        raise ValueError(f"Unknown tool: {name}")

    question = arguments["question"]
    collection = arguments.get("collection", "aap-docs")

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(
                f"{API_BASE}/ask",
                json={"question": question, "collection": collection, "k": 6}
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.ConnectError:
            return [TextContent(
                type="text",
                text="AAP RAG API is not running. Start it with: podman-compose up -d ragapi"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error querying AAP docs: {e}")]

    answer = data["answer"]
    sources = data.get("sources", [])
    source_lines = "\n".join(
        f"- {s['file']}, page {s['page']}" for s in sources
    )

    result = answer
    if source_lines:
        result += f"\n\n**Sources (AAP 2.7 official docs):**\n{source_lines}"

    return [TextContent(type="text", text=result)]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
