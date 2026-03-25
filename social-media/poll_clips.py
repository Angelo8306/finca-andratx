#!/usr/bin/env python3
"""Poll for submitted fal.ai jobs and download results"""

import os
import requests
import time
import json

FAL_KEY = 'bcfcfd01-4c85-4bc7-be5b-988a92ca5262:d46a4a43bf2da74351df2ffd3b7a8d28'
BASE = '/Users/angelojuric/Documents/Cay Fingerle/Finca Cay Fingerle'
CLIPS_DIR = f'{BASE}/social-media/clips_raw'

JOBS = [
    ('019d266a-066a-7bd0-a1fd-8a3d3d2e9394', 'test_01_facade'),
    ('019d266a-12c8-7bd2-947b-31f1161bccfb', 'test_02_interior'),
    ('019d266a-1e9c-7a01-8a5c-0a19bb2ea28a', 'test_03_garden'),
]

API_BASE = 'https://queue.fal.run/fal-ai/kling-video/v2.1/pro/image-to-video'
headers = {'Authorization': f'Key {FAL_KEY}'}

os.makedirs(CLIPS_DIR, exist_ok=True)

for req_id, name in JOBS:
    print(f'\n--- Checking: {name} ({req_id}) ---')

    # Check status
    status_url = f'{API_BASE}/requests/{req_id}/status'
    try:
        resp = requests.get(status_url, headers=headers)
        print(f'  Status HTTP: {resp.status_code}')
        raw = resp.text[:500]
        print(f'  Raw response: {raw}')

        try:
            data = resp.json()
            status = data.get('status', 'UNKNOWN')
            print(f'  Status: {status}')
        except:
            print(f'  Could not parse JSON, trying result endpoint directly...')
    except Exception as e:
        print(f'  Error checking status: {e}')

    # Try to get result directly
    result_url = f'{API_BASE}/requests/{req_id}'
    try:
        resp2 = requests.get(result_url, headers=headers)
        print(f'  Result HTTP: {resp2.status_code}')

        if resp2.status_code == 200:
            try:
                result = resp2.json()
                video_url = result.get('video', {}).get('url', '')
                if video_url:
                    print(f'  Video URL found! Downloading...')
                    vid = requests.get(video_url)
                    out_path = f'{CLIPS_DIR}/{name}.mp4'
                    with open(out_path, 'wb') as f:
                        f.write(vid.content)
                    size_mb = len(vid.content) / 1024 / 1024
                    print(f'  SAVED: {out_path} ({size_mb:.1f} MB)')
                else:
                    print(f'  No video URL yet. Keys: {list(result.keys())}')
                    if 'detail' in result:
                        print(f'  Detail: {result["detail"][:200]}')
            except Exception as e:
                print(f'  Result parse error: {e}')
                print(f'  Raw: {resp2.text[:300]}')
        else:
            print(f'  Result not ready: {resp2.text[:200]}')
    except Exception as e:
        print(f'  Error getting result: {e}')

print('\n=== Done checking all jobs ===')
