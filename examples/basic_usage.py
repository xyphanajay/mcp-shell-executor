#!/usr/bin/env python3
"""
Basic usage examples for MCP Shell Executor
"""

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def demo_shell_executor():
    """Demonstrate basic shell executor functionality"""
    
    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["../server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            print("=== MCP Shell Executor Demo ===")
            
            # List available tools
            tools = await session.list_tools()
            print(f"\nAvailable tools: {[tool.name for tool in tools.tools]}")
            
            # List available resources
            resources = await session.list_resources()
            print(f"Available resources: {[res.uri for res in resources.resources]}")
            
            # Example 1: Simple command
            print("\n--- Example 1: Simple Command ---")
            result = await session.call_tool(
                "run_bash_command",
                arguments={"command": "echo 'Hello from MCP Shell Executor!'"}
            )
            print(result.content[0].text)
            
            # Example 2: Command with working directory
            print("\n--- Example 2: Command with Working Directory ---")
            result = await session.call_tool(
                "run_bash_command",
                arguments={
                    "command": "pwd && ls -la",
                    "working_directory": "/tmp"
                }
            )
            print(result.content[0].text)
            
            # Example 3: Multi-line script
            print("\n--- Example 3: Multi-line Script ---")
            script = """#!/bin/bash
echo "System Information:"
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Uptime: $(uptime)"
"""
            result = await session.call_tool(
                "run_bash_script",
                arguments={"script_content": script}
            )
            print(result.content[0].text)
            
            # Example 4: Get system info resource
            print("\n--- Example 4: System Information Resource ---")
            content, mime_type = await session.read_resource("system://info")
            print(content)
            
            # Example 5: Get current directory resource
            print("\n--- Example 5: Current Directory Resource ---")
            content, mime_type = await session.read_resource("pwd://current")
            print(content)


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_shell_executor())
