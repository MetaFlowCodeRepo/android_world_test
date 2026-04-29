#!/usr/bin/env python3
"""Run ContactsNewContactDraft task step by step."""
import json
import sys
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
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())

def get_text(result):
    """Extract text from MCP result."""
    contents = result.get('result', {}).get('content', [])
    for c in contents:
        if c.get('type') == 'text':
            return c.get('text', '')
    return ''

def save_screenshot(result, filename):
    """Save screenshot from MCP result to file."""
    contents = result.get('result', {}).get('content', [])
    for c in contents:
        if c.get('type') == 'image':
            data = c.get('data', '')
            with open(filename, 'wb') as f:
                f.write(base64.b64decode(data))
            print(f"Screenshot saved to {filename}")
            return filename
    # If text result, just print it
    print(f"No image in result: {get_text(result)[:300]}")
    return None

def step(msg):
    print(f"\n{'='*50}")
    print(f"STEP: {msg}")
    print(f"{'='*50}")

if len(sys.argv) > 1:
    start_step = int(sys.argv[1])
else:
    start_step = 1

if start_step <= 1:
    step("1. Press home")
    r = call_tool("press_home")
    print(get_text(r)[:200])
    time.sleep(1)

if start_step <= 2:
    step("2. Screenshot to confirm home")
    r = call_tool("get_screenshot", {"quality": 15})
    save_screenshot(r, "/Users/zhp/projs/android_world_test/screenshots/step2_home.jpg")

if start_step <= 3:
    step("3. Open Contacts app")
    r = call_tool("open_app", {"package_name": "com.google.android.contacts"})
    print(get_text(r)[:200])
    time.sleep(2)

if start_step <= 4:
    step("4. Screenshot contacts app")
    r = call_tool("get_screenshot", {"quality": 15})
    save_screenshot(r, "/Users/zhp/projs/android_world_test/screenshots/step4_contacts.jpg")

if start_step <= 5:
    step("5. Click create new contact (+ button or 'Create new contact')")
    r = call_tool("ai_click", {"text": "Create new contact"})
    print(get_text(r)[:300])
    time.sleep(2)

if start_step <= 6:
    step("6. Screenshot new contact form")
    r = call_tool("get_screenshot", {"quality": 15})
    save_screenshot(r, "/Users/zhp/projs/android_world_test/screenshots/step6_newcontact.jpg")

print("\n\nDone with initial steps. Check screenshots and continue.")
