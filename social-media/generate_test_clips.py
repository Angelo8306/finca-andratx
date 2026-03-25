#!/usr/bin/env python3
"""Generate 3 test video clips from Finca photos via fal.ai (Kling 3.0)"""

import os
import base64
import requests
import time
import json
import sys

FAL_KEY = os.environ.get('FAL_KEY', 'bcfcfd01-4c85-4bc7-be5b-988a92ca5262:d46a4a43bf2da74351df2ffd3b7a8d28')
BASE = '/Users/angelojuric/Documents/Cay Fingerle/Finca Cay Fingerle'
CLIPS_DIR = f'{BASE}/social-media/clips_raw'

# 3 best photos for test clips
TEST_CLIPS = [
    {
        'image': f'{BASE}/images/01-facade.jpg',
        'prompt': 'Slow cinematic camera push forward through blooming almond trees toward a beautiful Mallorcan stone house, gentle breeze moves tree branches, warm golden hour sunlight, birds flying overhead, Mediterranean countryside atmosphere, shot on ARRI Alexa, shallow depth of field, cinematic 4K',
        'name': 'test_01_facade'
    },
    {
        'image': f'{BASE}/images/05-interior3.jpg',
        'prompt': 'Slow cinematic camera tilt upward revealing double-height stone ceiling with wooden beams in a renovated Mallorcan finca interior, warm ambient light streaming through windows, dust particles floating in light beams, elegant Mediterranean interior design, shot on RED camera, cinematic 4K',
        'name': 'test_02_interior'
    },
    {
        'image': f'{BASE}/images/02-exterior.jpg',
        'prompt': 'Slow steady camera dolly forward along a stone garden path lined with blooming lavender and olive trees, leading to a Mediterranean stone house, butterflies and bees around flowers, warm afternoon light, gentle wind, cinematic depth of field, shot on ARRI Alexa, 4K',
        'name': 'test_03_garden'
    }
]

def image_to_base64_url(path):
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    return f'data:image/jpeg;base64,{data}'

def submit_job(image_path, prompt, name):
    """Submit async job to fal.ai Kling 3.0"""
    print(f'\n--- Submitting: {name} ---')

    img_url = image_to_base64_url(image_path)

    payload = {
        'prompt': prompt,
        'image_url': img_url,
        'duration': '5',
        'aspect_ratio': '9:16'  # Vertical for Reels
    }

    headers = {
        'Authorization': f'Key {FAL_KEY}',
        'Content-Type': 'application/json'
    }

    # Submit async
    resp = requests.post(
        'https://queue.fal.run/fal-ai/kling-video/v2.1/pro/image-to-video',
        json=payload,
        headers=headers
    )

    if resp.status_code != 200:
        print(f'  ERROR submitting {name}: {resp.status_code} - {resp.text[:200]}')
        return None

    result = resp.json()
    request_id = result.get('request_id')
    print(f'  Submitted! Request ID: {request_id}')
    return request_id

def poll_result(request_id, name, max_wait=600):
    """Poll for job completion"""
    headers = {'Authorization': f'Key {FAL_KEY}'}
    url = f'https://queue.fal.run/fal-ai/kling-video/v2.1/pro/image-to-video/requests/{request_id}/status'

    start = time.time()
    while time.time() - start < max_wait:
        resp = requests.get(url, headers=headers)
        data = resp.json()
        status = data.get('status', 'UNKNOWN')

        if status == 'COMPLETED':
            # Get the result
            result_url = f'https://queue.fal.run/fal-ai/kling-video/v2.1/pro/image-to-video/requests/{request_id}'
            result_resp = requests.get(result_url, headers=headers)
            result_data = result_resp.json()
            video_url = result_data.get('video', {}).get('url', '')
            if video_url:
                print(f'  {name} DONE! Downloading...')
                video_resp = requests.get(video_url)
                out_path = f'{CLIPS_DIR}/{name}.mp4'
                with open(out_path, 'wb') as f:
                    f.write(video_resp.content)
                size_mb = len(video_resp.content) / 1024 / 1024
                print(f'  Saved: {out_path} ({size_mb:.1f} MB)')
                return out_path
            else:
                print(f'  {name} completed but no video URL found: {json.dumps(result_data)[:200]}')
                return None
        elif status == 'FAILED':
            print(f'  {name} FAILED: {json.dumps(data)[:200]}')
            return None
        else:
            elapsed = int(time.time() - start)
            print(f'  {name}: {status} ({elapsed}s elapsed)...', end='\r')
            time.sleep(10)

    print(f'  {name}: TIMEOUT after {max_wait}s')
    return None

def main():
    print('=== Finca Andratx — Test-Clip Generation ===')
    print(f'Using Kling v2.1 Pro via fal.ai')
    print(f'Generating {len(TEST_CLIPS)} test clips (9:16 vertical for Reels)')

    os.makedirs(CLIPS_DIR, exist_ok=True)

    # Submit all jobs
    jobs = []
    for clip in TEST_CLIPS:
        req_id = submit_job(clip['image'], clip['prompt'], clip['name'])
        if req_id:
            jobs.append((req_id, clip['name']))
        time.sleep(2)  # Small delay between submissions

    print(f'\n=== {len(jobs)} jobs submitted. Polling for results... ===')
    print('(AI video generation takes 2-5 minutes per clip)\n')

    # Poll all jobs
    results = []
    for req_id, name in jobs:
        result = poll_result(req_id, name)
        if result:
            results.append(result)

    print(f'\n=== DONE: {len(results)}/{len(jobs)} clips generated ===')
    for r in results:
        print(f'  {r}')

if __name__ == '__main__':
    main()
