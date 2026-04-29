import requests, json, base64, time, sys

URL = 'http://8.140.220.95:8000/mcp/53a2610f7140ca28'

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
    for item in result:
        if item.get('type') == 'text':
            texts.append(item.get('text', ''))
        elif item.get('type') == 'image':
            # Save image
            img_data = base64.b64decode(item.get('data', ''))
            path = f'/Users/zhp/projs/android_world_test/screenshot_{int(time.time())}.jpg'
            with open(path, 'wb') as f:
                f.write(img_data)
            texts.append(f'IMAGE_SAVED:{path}')
    return '\n'.join(texts)

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else 'press_home'

    if action == 'press_home':
        print(mcp_call('press_home'))
    elif action == 'screenshot':
        quality = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        print(mcp_call('get_screenshot', {'quality': quality}))
    elif action == 'open_settings':
        print(mcp_call('open_app', {'package_name': 'com.android.settings'}))
    elif action == 'ai_click':
        kwargs = {}
        if len(sys.argv) > 2:
            kwargs['text'] = sys.argv[2]
        if len(sys.argv) > 3:
            kwargs['icon'] = sys.argv[3]
        print(mcp_call('ai_click', kwargs))
    elif action == 'ai_set_text':
        print(mcp_call('ai_set_text', {'element': sys.argv[2], 'text': sys.argv[3]}))
    elif action == 'swipe':
        direction = sys.argv[2] if len(sys.argv) > 2 else 'up'
        print(mcp_call('swipe', {'direction': direction}))
    elif action == 'get_xml':
        print(mcp_call('get_screen_xml'))
    elif action == 'click':
        x = int(sys.argv[2])
        y = int(sys.argv[3])
        print(mcp_call('click', {'x': x, 'y': y}))
    elif action == 'find_nodes':
        print(mcp_call('find_nodes', json.loads(sys.argv[2])))
    elif action == 'click_node':
        print(mcp_call('click_node', {'innerid': int(sys.argv[2])}))
    elif action == 'press_back':
        print(mcp_call('press_back'))

if __name__ == '__main__':
    main()
