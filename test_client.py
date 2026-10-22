"""Connects to the running server over Streamable HTTP and exercises every tool."""
import asyncio
from mcp import ClientSession
try:
    from mcp.client.streamable_http import streamable_http_client
except ImportError:  # older 1.x SDKs
    from mcp.client.streamable_http import streamablehttp_client as streamable_http_client

TEXT = ("We will commence the assessment approximately at noon, and individuals "
        "who require additional assistance should obtain a form, which is available at the desk.")

async def main():
    async with streamable_http_client("http://localhost:8000/mcp") as streams:
        async with ClientSession(streams[0], streams[1]) as s:
            await s.initialize()
            print("TOOLS:", [t.name for t in (await s.list_tools()).tools])
            for name, args in [("readability_report", {"text": TEXT}),
                               ("simplify_for_dyslexia", {"text": TEXT}),
                               ("chunk_for_reading", {"text": TEXT}),
                               ("syllable_break", {"word": "assessment"})]:
                res = await s.call_tool(name, args)
                print(f"\n== {name} ==\n" + res.content[0].text)

asyncio.run(main())
