#!/usr/bin/env python3
"""Helper to call MCP tools on device."""
import requests
import json
import sys
import base64

MCP_URL = "http://8.140.220.95:8000/mcp/53a2610f7140ca28"

def call_tool(name, arguments=None):
    if arguments is None:
        arguments = {}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": name,
            "arguments": arguments
        }
    }
    resp = requests.post(MCP_URL, json=payload, timeout=60)
    return resp.json()

def save_screenshot(result, path="/Users/zhp/projs/android_world_test/screen.jpg"):
    """Extract base64 image from result and save to file."""
    try:
        content = result.get("result", {}).get("content", [])
        for item in content:
            if item.get("type") == "image":
                img_data = base64.b64decode(item["data"])
                with open(path, "wb") as f:
                    f.write(img_data)
                print(f"Screenshot saved to {path}")
                return path
        # If no image type, check for text with base64
        for item in content:
            if item.get("type") == "text" and len(item.get("text", "")) > 1000:
                img_data = base64.b64decode(item["text"])
                with open(path, "wb") as f:
                    f.write(img_data)
                print(f"Screenshot saved to {path}")
                return path
        print("No image found in result")
        print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
    except Exception as e:
        print(f"Error: {e}")
        print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "help"

    if action == "home":
        r = call_tool("press_home")
        print(json.dumps(r, indent=2, ensure_ascii=False)[:500])
    elif action == "screenshot":
        r = call_tool("get_screenshot", {"quality": 15})
        save_screenshot(r)
    elif action == "open_app":
        pkg = sys.argv[2]
        r = call_tool("open_app", {"package_name": pkg})
        print(json.dumps(r, indent=2, ensure_ascii=False)[:500])
    elif action == "ai_click":
        kwargs = json.loads(sys.argv[2])
        r = call_tool("ai_click", kwargs)
        print(json.dumps(r, indent=2, ensure_ascii=False)[:1000])
    elif action == "ai_set_text":
        kwargs = json.loads(sys.argv[2])
        r = call_tool("ai_set_text", kwargs)
        print(json.dumps(r, indent=2, ensure_ascii=False)[:1000])
    elif action == "swipe":
        kwargs = json.loads(sys.argv[2])
        r = call_tool("swipe", kwargs)
        print(json.dumps(r, indent=2, ensure_ascii=False)[:500])
    elif action == "get_xml":
        r = call_tool("get_screen_xml")
        print(json.dumps(r, indent=2, ensure_ascii=False)[:5000])
    elif action == "press_back":
        r = call_tool("press_back")
        print(json.dumps(r, indent=2, ensure_ascii=False)[:500])
    elif action == "click":
        x, y = int(sys.argv[2]), int(sys.argv[3])
        r = call_tool("click", {"x": x, "y": y})
        print(json.dumps(r, indent=2, ensure_ascii=False)[:500])
    elif action == "find_nodes":
        kwargs = json.loads(sys.argv[2])
        r = call_tool("find_nodes", kwargs)
        print(json.dumps(r, indent=2, ensure_ascii=False)[:5000])
    elif action == "wait_stable":
        r = call_tool("wait_stable_screen")
        print(json.dumps(r, indent=2, ensure_ascii=False)[:500])
    elif action == "tool":
        name = sys.argv[2]
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        r = call_tool(name, args)
        print(json.dumps(r, indent=2, ensure_ascii=False)[:5000])
    else:
        print("Usage: python3 mcp_helper.py [home|screenshot|open_app|ai_click|swipe|get_xml|press_back|click|find_nodes|wait_stable|tool]")
