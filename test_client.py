import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["test_server.py"],
        env=None
    )

    print("Connecting to server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Session initialized.")
            
            result = await session.call_tool("echo", arguments={"message": "Hello"})
            print(f"Result: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run())
