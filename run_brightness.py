#!/usr/bin/env python3
"""Automate setting brightness to minimum on Android device via MCP."""
import requests, json, base64, time

URL = 'http://8.140.220.95:8000/mcp/53a2610f7140ca28'
SCREENSHOT_DIR = '/Users/zhp/projs/android_world_test'
screenshot_counter = [0]

def mcp_call(tool_name, arguments=None):
    if arguments is None:
        arguments = {}
    resp = requests.post(URL, json={
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/call',
        'params': {'name': tool_name, 'arguments': arguments}
    }, timeout=30)
    result = resp.json().get('result', {}).get('content', [])
    texts = []
    image_path = None
    for item in result:
        if item.get('type') == 'text':
            texts.append(item.get('text', ''))
        elif item.get('type') == 'image':
            img_data = base64.b64decode(item.get('data', ''))
            screenshot_counter[0] += 1
            path = f'{SCREENSHOT_DIR}/scr_{screenshot_counter[0]:02d}.jpg'
            with open(path, 'wb') as f:
                f.write(img_data)
            image_path = path
            texts.append(f'IMAGE_SAVED:{path}')
    return '\n'.join(texts), image_path

def step(desc, tool, args=None):
    print(f'\n=== {desc} ===')
    result, img = mcp_call(tool, args)
    print(result[:500])
    return result, img

# Step 1: Press home
step('Press Home', 'press_home')
time.sleep(1)

# Step 2: Take screenshot to confirm home
step('Screenshot - Home', 'get_screenshot', {'quality': 15})

# Step 3: Open Settings
step('Open Settings', 'open_app', {'package_name': 'com.android.settings'})
time.sleep(2)

# Step 4: Screenshot settings
step('Screenshot - Settings', 'get_screenshot', {'quality': 15})

# Step 5: Click Display
step('Click Display', 'ai_click', {'text': 'Display'})
time.sleep(2)

# Step 6: Screenshot display settings
step('Screenshot - Display', 'get_screenshot', {'quality': 15})

print('\n\n=== PHASE 1 COMPLETE - Check screenshots ===')
