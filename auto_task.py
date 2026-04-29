#!/usr/bin/env python3
"""Automate TurnOnWifiAndOpenApp task via MCP."""

import urllib.request
import json
import base64
import sys
import time

MCP_URL = 'http://8.140.220.95:8000/mcp/53a2610f7140ca28'

def mcp_call(tool_name, arguments=None):
    if arguments is None:
        arguments = {}
    payload = json.dumps({
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/call',
        'params': {'name': tool_name, 'arguments': arguments}
    }).encode()
    req = urllib.request.Request(MCP_URL, data=payload, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read().decode())
    return result

def save_screenshot(result, filename):
    """Extract base64 image from MCP result and save to file."""
    try:
        content = result.get('result', {}).get('content', [])
        for item in content:
            if item.get('type') == 'image':
                img_data = base64.b64decode(item['data'])
                with open(filename, 'wb') as f:
                    f.write(img_data)
                print(f"Screenshot saved to {filename}")
                return filename
            elif item.get('type') == 'text':
                print(f"Text: {item['text'][:200]}")
    except Exception as e:
        print(f"Error saving screenshot: {e}")
        print(f"Raw result keys: {result.keys() if isinstance(result, dict) else type(result)}")
    return None

def print_text_result(result):
    try:
        content = result.get('result', {}).get('content', [])
        for item in content:
            if item.get('type') == 'text':
                print(f"Text: {item['text'][:500]}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Raw: {json.dumps(result)[:500]}")

if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'press_home'

    if action == 'press_home':
        r = mcp_call('press_home')
        print_text_result(r)
    elif action == 'screenshot':
        fname = sys.argv[2] if len(sys.argv) > 2 else '/tmp/screen.jpg'
        r = mcp_call('get_screenshot', {'quality': 15})
        save_screenshot(r, fname)
    elif action == 'open_settings':
        r = mcp_call('open_app', {'app': 'com.android.settings'})
        print_text_result(r)
    elif action == 'ai_click':
        text = sys.argv[2] if len(sys.argv) > 2 else ''
        icon = sys.argv[3] if len(sys.argv) > 3 else ''
        args = {}
        if text:
            args['text'] = text
        if icon:
            args['icon'] = icon
        r = mcp_call('ai_click', args)
        print_text_result(r)
    elif action == 'open_app':
        app = sys.argv[2]
        r = mcp_call('open_app', {'app': app})
        print_text_result(r)
    elif action == 'swipe':
        direction = sys.argv[2] if len(sys.argv) > 2 else 'up'
        r = mcp_call('swipe', {'direction': direction})
        print_text_result(r)
    elif action == 'get_xml':
        r = mcp_call('get_screen_xml')
        print_text_result(r)
    elif action == 'click_node':
        innerid = sys.argv[2]
        r = mcp_call('click_node', {'innerid': innerid})
        print_text_result(r)
    elif action == 'find_nodes':
        query = sys.argv[2]
        r = mcp_call('find_nodes', {'query': query})
        print_text_result(r)
    elif action == 'press_back':
        r = mcp_call('press_back')
        print_text_result(r)
    elif action == 'click':
        x = int(sys.argv[2])
        y = int(sys.argv[3])
        r = mcp_call('click', {'x': x, 'y': y})
        print_text_result(r)
    elif action == 'wait':
        r = mcp_call('wait_stable_screen')
        print_text_result(r)
    else:
        print(f"Unknown action: {action}")
