#!/usr/bin/env python3
"""Helper to call MCP tools via HTTP."""
import json
import sys
import urllib.request

MCP_URL = "http://8.140.220.95:8000/mcp/53a2610f7140ca28"

def call_tool(name: str, arguments: dict) -> dict:
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments}
    }).encode()
    req = urllib.request.Request(MCP_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())

if __name__ == "__main__":
    tool_name = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    result = call_tool(tool_name, args)
    print(json.dumps(result, indent=2, ensure_ascii=False)[:5000])
