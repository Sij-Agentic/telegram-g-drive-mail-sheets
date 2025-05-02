# core/session.py

import os
import sys
from typing import Optional, Any, List, Dict
from mcp import ClientSession
from mcp.client.sse import sse_client


class MCP:
    """
    Lightweight wrapper for one-time MCP tool calls using SSE transport.
    Each call connects to the SSE server and terminates cleanly.
    """

    def __init__(
        self,
        server_url: str = "http://127.0.0.1:8000/sse",
    ):
        self.server_url = server_url

    async def list_tools(self):
        async with sse_client(self.server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                return tools_result.tools

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        async with sse_client(self.server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool(tool_name, arguments=arguments)


class MultiMCP:
    """
    Stateless version: discovers tools from multiple MCP servers, but reconnects per tool call.
    Each call_tool() uses a fresh session based on tool-to-server mapping.
    """

    def __init__(self, server_configs: List[dict]):
        self.server_configs = server_configs
        self.tool_map: Dict[str, Dict[str, Any]] = {}  # tool_name → {config, tool}

    async def initialize(self):
        print("in MultiMCP initialize")
        for config in self.server_configs:
            try:
                server_url = config["url"]
                print(f"→ Scanning tools from: {server_url}")
                async with sse_client(server_url) as (read, write):
                    print("Connection established, creating session...")
                    try:
                        async with ClientSession(read, write) as session:
                            print("[agent] Session created, initializing...")
                            await session.initialize()
                            print("[agent] MCP session initialized")
                            tools = await session.list_tools()
                            print(f"→ Tools received: {[tool.name for tool in tools.tools]}")
                            for tool in tools.tools:
                                self.tool_map[tool.name] = {
                                    "config": config,
                                    "tool": tool
                                }
                    except Exception as se:
                        print(f"❌ Session error: {se}")
            except Exception as e:
                print(f"❌ Error initializing MCP server {config['url']}: {e}")

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        if tool_name not in self.tool_map:
            raise ValueError(f"Tool {tool_name} not found in any server.")
        config = self.tool_map[tool_name]["config"]
        server_url = config["url"]
        async with sse_client(server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool(tool_name, arguments=arguments)

    def get_all_tools(self):
        return [tool["tool"] for tool in self.tool_map.values()]

    async def shutdown(self):
        pass  # no persistent sessions to close