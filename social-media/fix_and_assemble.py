#!/usr/bin/env python3
"""Fix video: proper 9:16 crop, crossfades, generate music+voiceover via fal.ai, assemble final Reel"""

import os
import subprocess
import fal_client
import requests
import json
import time

os.environ['FAL_KEY'] = 'bcfcfd01-4c85-4bc7-be5b-988a92ca5262:d46a4a43bf2da74351df2ffd3b7a8d28'

BASE = '/Users/angelojuric/Documents/Cay Fingerle/Finca Cay Fingerle/social-media'
CLIPS = f'{BASE}/clips_raw'
WORK = f'{BASE}/work'
AUDIO = f'{BASE}/audio'
OUTPUT = f'{BASE}/output'

for d in [WORK, AUDIO, OUTPUT]:
    os.makedirs(d, exist_ok=True)

# ============================================================
# STEP 1: Crop clips to 9:16 (center crop, no black bars)
# ============================================================
print('='*60)
print('STEP 1: Cropping clips to 9:16 (no black bars)')
print('='*60)

# Scene list: (source_clip, start_sec, duration, text_overlay_or_None)
SCENES = [
    ('test_01_facade.mp4',     0.0, 3.5, 'ANDRATX, MALLORCA'),
    ('test_03_garden.mp4',     0.3, 3.0, 'Lavendel. Oliven. Stein.'),
    ('clip_terrasse.mp4',      0.3, 2.5, None),
    ('clip_kueche.mp4',        0.3, 2.5, None),
    ('clip_schlafzimmer.mp4',  0.3, 3.0, '3 Schlafzimmer'),
    ('clip_bad.mp4',           0.3, 2.0, None),
    ('clip_sunset_bedroom.mp4',0.3, 3.0, None),
    ('test_01_facade.mp4',     1.0, 3.5, '1.800.000 €'),
]

from PIL import Image, ImageDraw, ImageFont

def get_font(size):
    for p in ['/System/Library/Fonts/Helvetica.ttc', '/Library/Fonts/Arial.ttf']:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

def create_text_overlay(text, w=1080, h=1920):
    """Create transparent PNG with text bar at bottom"""
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = get_font(46)

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x = (w - tw) // 2
    y = h - 300

    # Semi-transparent bar
    draw.rectangle([0, y-25, w, y+th+25], fill=(44, 36, 32, 180))
    # Gold text
    draw.text((x, y), text, font=font, fill=(201, 169, 110, 255))

    path = f'{WORK}/overlay_{text[:10].replace(" ","_")}.png'
    img.save(path)
    return path

def create_cta_frame():
    """Create end card"""
    img = Image.new('RGB', (1080, 1920), (44, 36, 32))
    draw = ImageDraw.Draw(img)

    fl = get_font(58)
    fs = get_font(26)
    ft = get_font(22)

    # Tag
    tag = 'PRIVATVERKAUF'
    bb = draw.textbbox((0,0), tag, font=ft)
    draw.text(((1080-(bb[2]-bb[0]))//2, 700), tag, font=ft, fill=(201,169,110))

    # Title
    title = 'Ihre Finca wartet'
    bb = draw.textbbox((0,0), title, font=fl)
    draw.text(((1080-(bb[2]-bb[0]))//2, 760), title, font=fl, fill=(254,252,249))

    # Line
    draw.rectangle([460, 850, 620, 852], fill=(201,169,110))

    # Details
    for i, line in enumerate(['172 m² · 3 Schlafzimmer · 2 Bäder', '5 Min. zu Fuß ins Dorf Andratx', '', 'arquitecto@c-df.com', '+34 670 06 87 74']):
        if line:
            bb = draw.textbbox((0,0), line, font=fs)
            draw.text(((1080-(bb[2]-bb[0]))//2, 880+i*40), line, font=fs, fill=(254,252,249,180) if i<2 else (201,169,110))

    # CTA Button
    draw.rounded_rectangle([350, 1100, 730, 1155], radius=4, fill=(196,117,75))
    cta = 'LINK IN BIO'
    bb = draw.textbbox((0,0), cta, font=ft)
    draw.text(((1080-(bb[2]-bb[0]))//2, 1115), cta, font=ft, fill=(254,252,249))

    path = f'{WORK}/cta_frame.png'
    img.save(path)
    return path

cropped_clips = []

for i, (clip_file, start, dur, text) in enumerate(SCENES):
    src = f'{CLIPS}/{clip_file}'
    out = f'{WORK}/crop_{i:02d}.mp4'

    if not os.path.exists(src):
        print(f'  SKIP: {clip_file} not found')
        continue

    # Crop to 9:16 center (from landscape to portrait)
    # Source is ~1764x1176 (3:2). Target 1080x1920.
    # Strategy: scale height to 1920, then center-crop width to 1080
    crop_filter = 'scale=-1:1920,crop=1080:1920:(iw-1080)/2:0'

    cmd = [
        'ffmpeg', '-y', '-ss', str(start), '-i', src, '-t', str(dur),
        '-vf', f'{crop_filter},fps=30',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', out
    ]
    subprocess.run(cmd, capture_output=True)

    # Add text overlay if needed
    if text:
        overlay_png = create_text_overlay(text)
        out_text = f'{WORK}/crop_{i:02d}_txt.mp4'
        cmd2 = [
            'ffmpeg', '-y', '-i', out, '-i', overlay_png,
            '-filter_complex', '[0][1]overlay=0:0',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', out_text
        ]
        subprocess.run(cmd2, capture_output=True)
        cropped_clips.append(out_text)
        print(f'  Scene {i}: {clip_file} ({dur}s) + "{text}"')
    else:
        cropped_clips.append(out)
        print(f'  Scene {i}: {clip_file} ({dur}s)')

# Add CTA card
cta_png = create_cta_frame()
cta_mp4 = f'{WORK}/crop_99_cta.mp4'
subprocess.run([
    'ffmpeg', '-y', '-loop', '1', '-i', cta_png, '-t', '3.5',
    '-vf', 'fps=30', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
    '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', cta_mp4
], capture_output=True)
cropped_clips.append(cta_mp4)
print(f'  CTA card (3.5s)')

# ============================================================
# STEP 2: Color grade
# ============================================================
print(f'\n{"="*60}')
print('STEP 2: Color grading (warm Mediterranean look)')
print('='*60)

graded = []
for i, clip in enumerate(cropped_clips):
    out = f'{WORK}/grade_{i:02d}.mp4'
    subprocess.run([
        'ffmpeg', '-y', '-i', clip,
        '-vf', 'eq=brightness=0.02:contrast=1.08:saturation=1.15,colorbalance=rs=0.03:gs=-0.01:bs=-0.03',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', out
    ], capture_output=True)
    graded.append(out)
    print(f'  Graded {i}')

# ============================================================
# STEP 3: Concat with crossfades
# ============================================================
print(f'\n{"="*60}')
print('STEP 3: Concatenating with crossfade transitions')
print('='*60)

# Build xfade chain for smooth transitions
# Each transition is 0.5s crossfade
if len(graded) < 2:
    print('  Not enough clips!')
else:
    # For complex xfade chains, build iteratively
    current = graded[0]
    offset = 0

    # Get duration of first clip
    probe = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', current],
        capture_output=True, text=True
    )
    current_dur = float(probe.stdout.strip())

    for i in range(1, len(graded)):
        next_clip = graded[i]
        out = f'{WORK}/xfade_{i:02d}.mp4'
        fade_dur = 0.4

        # offset = duration of current minus fade
        offset = current_dur - fade_dur

        cmd = [
            'ffmpeg', '-y', '-i', current, '-i', next_clip,
            '-filter_complex', f'[0][1]xfade=transition=fade:duration={fade_dur}:offset={offset},format=yuv420p',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-an', '-movflags', '+faststart', out
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            current = out
            # Get new duration
            probe = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', current],
                capture_output=True, text=True
            )
            current_dur = float(probe.stdout.strip())
            print(f'  Crossfade {i}: OK (total: {current_dur:.1f}s)')
        else:
            print(f'  Crossfade {i}: FAILED, falling back to concat')
            print(f'    Error: {result.stderr[:150]}')
            # Fallback: simple concat
            concat_file = f'{WORK}/concat.txt'
            with open(concat_file, 'w') as f:
                for c in graded:
                    f.write(f"file '{c}'\n")
            subprocess.run([
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file,
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', out
            ], capture_output=True)
            current = out
            break

    video_no_audio = f'{OUTPUT}/reel_reveal_video.mp4'
    subprocess.run(['cp', current, video_no_audio])
    print(f'\n  Video saved: {video_no_audio}')

    # Final duration
    probe = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video_no_audio],
        capture_output=True, text=True
    )
    final_dur = float(probe.stdout.strip())
    print(f'  Duration: {final_dur:.1f}s')

# ============================================================
# STEP 4: Generate voiceover via fal.ai
# ============================================================
print(f'\n{"="*60}')
print('STEP 4: Generating German voiceover via fal.ai')
print('='*60)

voiceover_text = """Im Herzen von Andratx, eingebettet in die Berge Mallorcas, steht ein Haus aus einer anderen Zeit. Naturstein, jahrhundertealt. Doppelte Deckenhöhe. Ein Kamin, der Geschichten kennt. Drei Schlafzimmer. Zwei Bäder. Fünf Minuten zu Fuß ins Dorf. Ein Stück mallorquinische Seele."""

try:
    result = fal_client.subscribe(
        'fal-ai/f5-tts',
        arguments={
            'gen_text': voiceover_text,
            'ref_audio_url': 'https://cdn.themetavoice.xyz/speakers/bria.mp3',
            'model_type': 'F5-TTS',
        },
        with_logs=True
    )
    audio_url = result.get('audio_url', {}).get('url', '') if isinstance(result.get('audio_url'), dict) else result.get('audio_url', '')
    if audio_url:
        print(f'  Voiceover generated! Downloading...')
        audio_data = requests.get(audio_url)
        vo_path = f'{AUDIO}/voiceover_de.wav'
        with open(vo_path, 'wb') as f:
            f.write(audio_data.content)
        print(f'  Saved: {vo_path}')
    else:
        print(f'  No audio URL. Result keys: {list(result.keys())}')
        print(f'  Result: {json.dumps(result)[:300]}')
        vo_path = None
except Exception as e:
    print(f'  Voiceover error: {e}')
    vo_path = None

# ============================================================
# STEP 5: Generate background music via fal.ai
# ============================================================
print(f'\n{"="*60}')
print('STEP 5: Generating background music via fal.ai')
print('='*60)

try:
    result = fal_client.subscribe(
        'fal-ai/stable-audio',
        arguments={
            'prompt': 'Elegant Mediterranean acoustic guitar, warm cinematic atmosphere, luxury real estate promotional video, gentle piano, emotional, 30 seconds, no vocals',
            'seconds_total': 35,
        },
        with_logs=True
    )
    music_url = result.get('audio_file', {}).get('url', '') if isinstance(result.get('audio_file'), dict) else result.get('audio_file', '')
    if music_url:
        print(f'  Music generated! Downloading...')
        music_data = requests.get(music_url)
        music_path = f'{AUDIO}/music_bg.wav'
        with open(music_path, 'wb') as f:
            f.write(music_data.content)
        print(f'  Saved: {music_path}')
    else:
        print(f'  No music URL. Result: {json.dumps(result)[:300]}')
        music_path = None
except Exception as e:
    print(f'  Music error: {e}')
    music_path = None

# ============================================================
# STEP 6: Mix audio + video
# ============================================================
print(f'\n{"="*60}')
print('STEP 6: Final assembly (video + audio)')
print('='*60)

final_output = f'{OUTPUT}/Reel_The_Reveal_DE_FINAL.mp4'

if vo_path and music_path and os.path.exists(vo_path) and os.path.exists(music_path):
    # Mix VO + Music, then combine with video
    mixed_audio = f'{AUDIO}/mixed_master.wav'
    subprocess.run([
        'ffmpeg', '-y',
        '-i', vo_path, '-i', music_path,
        '-filter_complex',
        f'[0]adelay=2000|2000,volume=1.0[vo];[1]volume=0.25,afade=t=out:st={final_dur-2}:d=2[mu];[vo][mu]amix=inputs=2:duration=shortest',
        '-ar', '44100', mixed_audio
    ], capture_output=True)

    subprocess.run([
        'ffmpeg', '-y',
        '-i', video_no_audio, '-i', mixed_audio,
        '-t', str(final_dur),
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart', final_output
    ], capture_output=True)
    print(f'  Final with VO + Music: {final_output}')

elif music_path and os.path.exists(music_path):
    # Music only
    subprocess.run([
        'ffmpeg', '-y',
        '-i', video_no_audio, '-i', music_path,
        '-t', str(final_dur),
        '-filter_complex', f'[1]volume=0.5,afade=t=in:d=1,afade=t=out:st={final_dur-2}:d=2[a]',
        '-map', '0:v', '-map', '[a]',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart', final_output
    ], capture_output=True)
    print(f'  Final with Music only: {final_output}')

elif vo_path and os.path.exists(vo_path):
    # VO only
    subprocess.run([
        'ffmpeg', '-y',
        '-i', video_no_audio, '-i', vo_path,
        '-t', str(final_dur),
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart', final_output
    ], capture_output=True)
    print(f'  Final with VO only: {final_output}')
else:
    # No audio at all
    subprocess.run(['cp', video_no_audio, final_output])
    print(f'  Final without audio: {final_output}')

# Verify
probe = subprocess.run(
    ['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,width,height,duration', '-of', 'json', final_output],
    capture_output=True, text=True
)
print(f'\n  Final file info: {probe.stdout[:300]}')
print(f'\n{"="*60}')
print(f'DONE! Final Reel: {final_output}')
print('='*60)
