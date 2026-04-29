#!/usr/bin/env python3
"""Open dialer app on Android device via MCP."""
import json
import urllib.request
import base64
import os
import time

MCP_URL = "http://8.140.220.95:8000/mcp/53a2610f7140ca28"

def call_tool(name, arguments=None):
    if arguments is None:
        arguments = {}
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments}
    }).encode()
    req = urllib.request.Request(MCP_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())

def save_screenshot(result, filename):
    """Extract base64 image from MCP result and save to file."""
    if "result" in result and "content" in result["result"]:
        for item in result["result"]["content"]:
            if item.get("type") == "image":
                img_data = base64.b64decode(item["data"])
                path = os.path.join("/Users/zhp/projs/android_world_test/run_results", filename)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as f:
                    f.write(img_data)
                print(f"Screenshot saved: {path}")
                return path
            elif item.get("type") == "text":
                print(f"Text result: {item['text'][:500]}")
    return None

# Step 1: Press home
print("Step 1: Press home...")
r = call_tool("press_home")
print(f"press_home result: {json.dumps(r, ensure_ascii=False)[:300]}")
time.sleep(1)

# Step 2: Open dialer app
print("\nStep 2: Open dialer app...")
r = call_tool("open_app", {"app_name": "dialer"})
print(f"open_app result: {json.dumps(r, ensure_ascii=False)[:300]}")
time.sleep(2)

# Step 3: Take screenshot to verify
print("\nStep 3: Taking screenshot...")
r = call_tool("get_screenshot", {"quality": 15})
path = save_screenshot(r, "dialer_opened.jpg")
if not path:
    print(f"Screenshot raw: {json.dumps(r, ensure_ascii=False)[:500]}")

print("\nDone!")
