#!/usr/bin/env python3
import json
import sys
import urllib.request
import base64
import os

URL = "http://8.140.220.95:8000/mcp/53a2610f7140ca28"

def call_tool(name, args=None):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": name, "arguments": args or {}}
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=60)
    result = json.loads(resp.read())
    return result.get("result", {})

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 do_mcp.py <tool_name> [json_args]")
        sys.exit(1)

    tool = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    result = call_tool(tool, args)
    contents = result.get("content", [])

    for item in contents:
        if item.get("type") == "text":
            print(item["text"][:2000])
        elif item.get("type") == "image":
            img_data = base64.b64decode(item["data"])
            path = "/Users/zhp/projs/android_world_test/screen.jpg"
            with open(path, "wb") as f:
                f.write(img_data)
            print(f"Screenshot saved to {path} ({len(img_data)} bytes)")

if __name__ == "__main__":
    main()
