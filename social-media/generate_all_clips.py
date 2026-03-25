#!/usr/bin/env python3
"""Generate all video clips for 3 Reels"""

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

# All clips needed for 3 Reels
# Skipping interior double-height (looked fake), using safer exterior/detail shots
CLIPS = [
    # === REEL 2 "The Reveal" clips ===
    {
        'image': f'{BASE}/images/03-interior1.jpg',
        'prompt': 'Very subtle slow camera pan right across a Mediterranean stone terrace with wooden dining table, gentle wind moves a bougainvillea plant, warm sunlight creates shadows on stone wall, peaceful atmosphere, cinematic 4K',
        'name': 'clip_terrasse'
    },
    {
        'image': f'{BASE}/images/06-interior4.jpg',
        'prompt': 'Very subtle slow camera push forward into a rustic Mediterranean kitchen with traditional tiles and wooden cabinets, steam rising from a coffee cup on counter, warm morning light, cozy atmosphere, cinematic 4K',
        'name': 'clip_kueche'
    },
    {
        'image': f'{BASE}/images/09-view1.jpg',
        'prompt': 'Very subtle slow camera dolly right across an elegant bedroom with wooden ceiling beams, warm indirect lighting, curtains gently moving from breeze through open window, peaceful evening atmosphere, cinematic 4K',
        'name': 'clip_schlafzimmer'
    },
    {
        'image': f'{BASE}/images/13-detail1.jpg',
        'prompt': 'Very subtle slow camera pan across a modern Mediterranean bathroom with walk-in rain shower and natural stone details, water droplets on glass, warm light through small window, spa atmosphere, cinematic 4K',
        'name': 'clip_bad'
    },
    # === REEL 3 "Lifestyle" clips ===
    {
        'image': f'{BASE}/images/10-view2.jpg',
        'prompt': 'Very subtle slow camera push forward toward bedroom window revealing sunset landscape view over Mallorcan mountains, golden hour light fills the room with warm tones, peaceful evening mood, cinematic 4K',
        'name': 'clip_sunset_bedroom'
    },
    {
        'image': f'{BASE}/images/08-interior6.jpg',
        'prompt': 'Very subtle slow camera pan left across a comfortable Mediterranean bedroom with wooden wardrobe and balcony doors, light curtains gently swaying, warm afternoon light, relaxed atmosphere, cinematic 4K',
        'name': 'clip_bedroom2'
    },
]

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(f'  Log: {log["message"]}')

for clip in CLIPS:
    out_path = f'{CLIPS_DIR}/{clip["name"]}.mp4'
    if os.path.exists(out_path):
        print(f'\n=== Skipping {clip["name"]} (already exists) ===')
        continue

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
            print(f'  Downloading...')
            vid = requests.get(video_url)
            with open(out_path, 'wb') as f:
                f.write(vid.content)
            size_mb = len(vid.content) / 1024 / 1024
            print(f'  SAVED: {out_path} ({size_mb:.1f} MB)')
        else:
            print(f'  No video URL: {list(result.keys())}')
    except Exception as e:
        print(f'  ERROR: {e}')

print('\n=== All clips done! ===')
# List all clips
for f in sorted(os.listdir(CLIPS_DIR)):
    if f.endswith('.mp4'):
        size = os.path.getsize(f'{CLIPS_DIR}/{f}') / 1024 / 1024
        print(f'  {f} ({size:.1f} MB)')
