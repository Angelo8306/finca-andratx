#!/usr/bin/env python3
"""Generate test video clips using official fal-client"""

import os
import fal_client
import base64
import requests

os.environ['FAL_KEY'] = 'bcfcfd01-4c85-4bc7-be5b-988a92ca5262:d46a4a43bf2da74351df2ffd3b7a8d28'

BASE = '/Users/angelojuric/Documents/Cay Fingerle/Finca Cay Fingerle'
CLIPS_DIR = f'{BASE}/social-media/clips_raw'
os.makedirs(CLIPS_DIR, exist_ok=True)

def image_to_data_url(path):
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    return f'data:image/jpeg;base64,{data}'

CLIPS = [
    {
        'image': f'{BASE}/images/01-facade.jpg',
        'prompt': 'Slow cinematic camera push forward through blooming almond trees toward a beautiful Mallorcan stone house, gentle breeze moves branches, warm golden hour sunlight, birds flying, Mediterranean countryside, cinematic 4K',
        'name': 'test_01_facade'
    },
    {
        'image': f'{BASE}/images/05-interior3.jpg',
        'prompt': 'Slow cinematic camera tilt upward revealing double-height ceiling with wooden beams in renovated Mallorcan finca, warm ambient light through windows, dust particles in light, elegant Mediterranean interior, cinematic 4K',
        'name': 'test_02_interior'
    },
    {
        'image': f'{BASE}/images/02-exterior.jpg',
        'prompt': 'Slow steady camera dolly forward along stone garden path lined with lavender and olive trees toward Mediterranean stone house, butterflies around flowers, warm afternoon light, cinematic 4K',
        'name': 'test_03_garden'
    }
]

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(f'  Log: {log["message"]}')

for clip in CLIPS:
    print(f'\n=== Generating: {clip["name"]} ===')
    img_url = image_to_data_url(clip['image'])

    try:
        result = fal_client.subscribe(
            'fal-ai/kling-video/v2.1/pro/image-to-video',
            arguments={
                'prompt': clip['prompt'],
                'image_url': img_url,
                'duration': '5',
                'aspect_ratio': '9:16'
            },
            with_logs=True,
            on_queue_update=on_queue_update
        )

        video_url = result.get('video', {}).get('url', '')
        if video_url:
            print(f'  Downloading video...')
            vid = requests.get(video_url)
            out_path = f'{CLIPS_DIR}/{clip["name"]}.mp4'
            with open(out_path, 'wb') as f:
                f.write(vid.content)
            size_mb = len(vid.content) / 1024 / 1024
            print(f'  SAVED: {out_path} ({size_mb:.1f} MB)')
        else:
            print(f'  No video URL in result: {list(result.keys())}')

    except Exception as e:
        print(f'  ERROR: {e}')

print('\n=== All done! ===')
print('Check clips in:', CLIPS_DIR)
