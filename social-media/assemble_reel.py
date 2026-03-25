#!/usr/bin/env python3
"""Assemble 'The Reveal' Reel from AI-generated clips with text overlays"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont
import shutil

BASE = '/Users/angelojuric/Documents/Cay Fingerle/Finca Cay Fingerle/social-media'
CLIPS = f'{BASE}/clips_raw'
NORM = f'{BASE}/clips_normalized'
OUTPUT = f'{BASE}/output'
os.makedirs(NORM, exist_ok=True)
os.makedirs(OUTPUT, exist_ok=True)

# === REEL EDIT: "The Reveal" (30 sec) ===
# Fast cuts, 2-3 sec each, with text overlays

SCENES = [
    # (clip_file, start_sec, duration_sec, text_overlay)
    ('test_01_facade.mp4', 0, 1.5, None),  # Black intro with fade-in
    ('test_01_facade.mp4', 0.5, 3.5, 'ANDRATX, MALLORCA'),
    ('test_03_garden.mp4', 0.5, 3.0, 'Lavendel. Oliven. Stein.'),
    ('clip_terrasse.mp4', 0.5, 3.0, None),
    ('clip_kueche.mp4', 0.5, 2.5, None),
    ('clip_schlafzimmer.mp4', 0.5, 3.0, '3 Schlafzimmer'),
    ('clip_bad.mp4', 0.5, 2.5, None),
    ('clip_sunset_bedroom.mp4', 0.5, 3.0, None),
    ('test_01_facade.mp4', 1.0, 3.5, '1.800.000 \u20ac'),
    # Final: black with CTA
]

def normalize_clip(input_path, output_path, start, duration):
    """Normalize clip to 1080x1920 (9:16) 30fps"""
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(start),
        '-i', input_path,
        '-t', str(duration),
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,fps=30',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-an',  # no audio for now
        '-movflags', '+faststart',
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    return output_path

def create_text_frame(text, width=1080, height=1920, font_size=48):
    """Create a text overlay PNG using Pillow"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Try system fonts
    font = None
    for font_path in [
        '/System/Library/Fonts/Helvetica.ttc',
        '/System/Library/Fonts/SFNSDisplay.ttf',
        '/Library/Fonts/Arial.ttf',
    ]:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue

    if not font:
        font = ImageFont.load_default()

    # Calculate text position (bottom third with padding)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (width - text_w) // 2
    y = height - 350  # Bottom area

    # Draw background bar
    bar_padding = 30
    draw.rectangle(
        [0, y - bar_padding, width, y + text_h + bar_padding],
        fill=(44, 36, 32, 200)
    )

    # Draw text with gold color
    draw.text((x, y), text, font=font, fill=(201, 169, 110, 255))

    return img

def overlay_text_on_clip(clip_path, text, output_path):
    """Overlay text on clip using Pillow frame-by-frame approach via FFmpeg"""
    # Create overlay image
    overlay_path = f'{NORM}/overlay_temp.png'
    overlay = create_text_frame(text, font_size=52)
    overlay.save(overlay_path)

    # Use FFmpeg to overlay the PNG on the video
    cmd = [
        'ffmpeg', '-y',
        '-i', clip_path,
        '-i', overlay_path,
        '-filter_complex', '[0][1]overlay=0:0:format=auto',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-an', '-movflags', '+faststart',
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    return output_path

def create_black_title(text, duration=2.0, output_path=None):
    """Create a black frame with centered text"""
    img = Image.new('RGB', (1080, 1920), (44, 36, 32))
    draw = ImageDraw.Draw(img)

    font = None
    for font_path in [
        '/System/Library/Fonts/Helvetica.ttc',
        '/Library/Fonts/Arial.ttf',
    ]:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, 56)
                break
            except:
                continue

    if not font:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (1080 - text_w) // 2
    y = (1920 - text_h) // 2

    draw.text((x, y), text, font=font, fill=(201, 169, 110))

    frame_path = f'{NORM}/title_frame.png'
    img.save(frame_path)

    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', frame_path,
        '-t', str(duration),
        '-vf', 'fps=30',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-an', '-movflags', '+faststart',
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    return output_path

def create_cta_card(output_path, duration=3.0):
    """Create final CTA card"""
    img = Image.new('RGB', (1080, 1920), (44, 36, 32))
    draw = ImageDraw.Draw(img)

    font_large = None
    font_small = None
    for font_path in [
        '/System/Library/Fonts/Helvetica.ttc',
        '/Library/Fonts/Arial.ttf',
    ]:
        if os.path.exists(font_path):
            try:
                font_large = ImageFont.truetype(font_path, 64)
                font_small = ImageFont.truetype(font_path, 28)
                break
            except:
                continue

    # Title
    title = "Ihre Finca wartet"
    bbox = draw.textbbox((0, 0), title, font=font_large)
    x = (1080 - (bbox[2] - bbox[0])) // 2
    draw.text((x, 750), title, font=font_large, fill=(254, 252, 249))

    # Divider
    draw.rectangle([440, 840, 640, 842], fill=(201, 169, 110))

    # Details
    details = "172 m\u00b2 \u00b7 3 Schlafzimmer \u00b7 2 B\u00e4der"
    bbox2 = draw.textbbox((0, 0), details, font=font_small)
    x2 = (1080 - (bbox2[2] - bbox2[0])) // 2
    draw.text((x2, 880), details, font=font_small, fill=(254, 252, 249, 150))

    # CTA button
    draw.rounded_rectangle([340, 980, 740, 1040], radius=4, fill=(196, 117, 75))
    cta_text = "LINK IN BIO"
    bbox3 = draw.textbbox((0, 0), cta_text, font=font_small)
    x3 = (1080 - (bbox3[2] - bbox3[0])) // 2
    draw.text((x3, 992), cta_text, font=font_small, fill=(254, 252, 249))

    frame_path = f'{NORM}/cta_frame.png'
    img.save(frame_path)

    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', frame_path,
        '-t', str(duration),
        '-vf', 'fps=30',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-an', '-movflags', '+faststart',
        output_path
    ]
    subprocess.run(cmd, capture_output=True)

print('=== Assembling Reel: "The Reveal" ===\n')

# Step 1: Normalize all clips
print('Step 1: Normalizing clips...')
normalized_clips = []
for i, (clip_file, start, dur, text) in enumerate(SCENES):
    src = f'{CLIPS}/{clip_file}'
    norm_path = f'{NORM}/scene_{i:02d}.mp4'

    if not os.path.exists(src):
        print(f'  WARNING: {clip_file} not found, skipping')
        continue

    print(f'  Normalizing scene {i}: {clip_file} ({dur}s)')
    normalize_clip(src, norm_path, start, dur)

    # Add text overlay if needed
    if text:
        text_path = f'{NORM}/scene_{i:02d}_text.mp4'
        print(f'  Adding text: "{text}"')
        overlay_text_on_clip(norm_path, text, text_path)
        normalized_clips.append(text_path)
    else:
        normalized_clips.append(norm_path)

# Add CTA card at the end
print('  Creating CTA card...')
cta_path = f'{NORM}/scene_99_cta.mp4'
create_cta_card(cta_path, duration=3.0)
normalized_clips.append(cta_path)

# Step 2: Color grade all clips
print('\nStep 2: Color grading...')
graded_clips = []
for i, clip in enumerate(normalized_clips):
    graded_path = f'{NORM}/graded_{i:02d}.mp4'
    cmd = [
        'ffmpeg', '-y', '-i', clip,
        '-vf', 'eq=brightness=0.02:contrast=1.08:saturation=1.15,colorbalance=rs=0.04:gs=-0.01:bs=-0.04',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-an', '-movflags', '+faststart',
        graded_path
    ]
    subprocess.run(cmd, capture_output=True)
    graded_clips.append(graded_path)
    print(f'  Graded clip {i}')

# Step 3: Concatenate with crossfades
print('\nStep 3: Concatenating clips...')
# Write concat file
concat_file = f'{NORM}/concat.txt'
with open(concat_file, 'w') as f:
    for clip in graded_clips:
        f.write(f"file '{clip}'\n")

# Simple concat (crossfades with many clips is complex in FFmpeg)
output_no_audio = f'{OUTPUT}/reel_reveal_no_audio.mp4'
cmd = [
    'ffmpeg', '-y',
    '-f', 'concat', '-safe', '0',
    '-i', concat_file,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
    '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart',
    output_no_audio
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f'  Concat error: {result.stderr[:300]}')
else:
    print(f'  Concatenated OK')

# Step 4: Check duration
probe = subprocess.run(
    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', output_no_audio],
    capture_output=True, text=True
)
duration = float(probe.stdout.strip()) if probe.stdout.strip() else 0
print(f'\nFinal video duration: {duration:.1f} seconds')

# Copy as final output (without music for now)
final = f'{OUTPUT}/Reel_The_Reveal_DE.mp4'
shutil.copy(output_no_audio, final)

print(f'\n=== DONE! ===')
print(f'Output: {final}')
print(f'Duration: {duration:.1f}s')
print(f'\nNote: This version has no audio. Add music in CapCut or ask for ElevenLabs voiceover.')
