#!/usr/bin/env python3
"""Navigate to Settings > About Phone and take screenshot."""
import json
import time
import base64
import urllib.request

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
    content = result.get("result", {}).get("content", [])
    for item in content:
        if item.get("type") == "image":
            img_data = base64.b64decode(item["data"])
            with open(filename, "wb") as f:
                f.write(img_data)
            print(f"Screenshot saved to {filename}")
            return filename
        elif item.get("type") == "text":
            print(f"Text response: {item['text'][:500]}")
    return None

# Step 1: Press home
print("=== Step 1: Press Home ===")
call_tool("press_home")
time.sleep(1)

# Step 2: Take screenshot to confirm home screen
print("=== Step 2: Screenshot home ===")
result = call_tool("get_screenshot", {"quality": 15})
save_screenshot(result, "/Users/zhp/projs/android_world_test/screen_home.jpg")

# Step 3: Open Settings app
print("=== Step 3: Open Settings ===")
call_tool("open_app", {"package_name": "com.android.settings"})
time.sleep(2)

# Step 4: Screenshot settings
print("=== Step 4: Screenshot Settings ===")
result = call_tool("get_screenshot", {"quality": 15})
save_screenshot(result, "/Users/zhp/projs/android_world_test/screen_settings.jpg")

# Step 5: Scroll down to find About Phone
print("=== Step 5: Scroll down in Settings ===")
call_tool("swipe", {"direction": "up", "distance": "long"})
time.sleep(1)
call_tool("swipe", {"direction": "up", "distance": "long"})
time.sleep(1)
call_tool("swipe", {"direction": "up", "distance": "long"})
time.sleep(1)

# Step 6: Screenshot after scrolling
print("=== Step 6: Screenshot after scroll ===")
result = call_tool("get_screenshot", {"quality": 15})
save_screenshot(result, "/Users/zhp/projs/android_world_test/screen_settings_bottom.jpg")

# Step 7: Click About Phone
print("=== Step 7: Click About Phone ===")
call_tool("ai_click", {"text": "About phone"})
time.sleep(2)

# Step 8: Screenshot About Phone page
print("=== Step 8: Screenshot About Phone ===")
result = call_tool("get_screenshot", {"quality": 15})
save_screenshot(result, "/Users/zhp/projs/android_world_test/screen_about_phone.jpg")

print("\n=== Done! ===")
