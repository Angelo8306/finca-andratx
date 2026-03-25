#!/usr/bin/env python3
"""
Finca Son Mone — Blockbuster Reels Generator v2
Erzeugt 6 Reels (3 DE + 3 EN) mit ElevenLabs Voiceover, fal.ai Musik,
Pillow Text-Overlays und FFmpeg Video-Compositing.
"""

import os
import sys
import json
import time
import struct
import subprocess
import tempfile
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ─── CONFIG ────────────────────────────────────────────────────────────
BASE = Path("/Users/angelojuric/Documents/Cay Fingerle/Finca Cay Fingerle/social-media")
CLIPS_DIR = BASE / "clips_raw"
OUTPUT_DIR = BASE / "output"
TEMP_DIR = BASE / "temp_production"

ELEVENLABS_KEY = "10435adb57d9183a835901bdafba5771cc1ac0f193686eb1fe0fb0f14224c9a4"
FAL_KEY = "bcfcfd01-4c85-4bc7-be5b-988a92ca5262:d46a4a43bf2da74351df2ffd3b7a8d28"

VOICE_DE = "Tn4bhLlhD26sndFn0Kgw"  # TommHH Radiovoice
VOICE_EN = "JBFqnCBsd6RMkjVDRZzb"  # George
VOICE_MODEL = "eleven_multilingual_v2"
VOICE_SETTINGS = {
    "stability": 0.3,
    "similarity_boost": 0.85,
    "style": 0.8,
    "use_speaker_boost": True
}

# Video settings
WIDTH, HEIGHT = 1080, 1920
FPS = 24
CROP_FILTER = "scale=-1:1920,crop=1080:1920:(iw-1080)/2:0"
COLOR_GRADE = "eq=brightness=0.02:contrast=1.08:saturation=1.15"
CROSSFADE_DUR = 0.4

# Text overlay colors
GOLD = "#C9A96E"
DARK_BG = (44, 36, 32, 180)  # #2C2420 with alpha

# ─── REEL DEFINITIONS ─────────────────────────────────────────────────

REELS = {
    "Teaser": {
        "duration_target": 15,
        "clips": ["test_03_garden", "clip_bad", "clip_schlafzimmer", "clip_kueche",
                  "test_01_facade"],
        "clip_durations": [2.0, 2.0, 2.0, 2.0, 3.0],  # ~11s video, rest fills with last
        "vo_de": "Einhundertfünfundzwanzig Jahre alt. Siebenunddreißig Jahre restauriert. Von einem Architekten... für einen Liebhaber. Son Mone. Andratsch. Coming Soon.",
        "vo_en": "One hundred and twenty-five years old. Thirty-seven years restored. By an architect... for a connoisseur. Son Mone. Andratsch. Coming Soon.",
        "music_prompt": "Dark cinematic trailer, deep bass, tension building, luxury brand reveal, dramatic, 15 seconds, no vocals",
        "music_duration": 15,
        "text_overlays": [
            {"text": "SON MONE", "start": 10.0, "duration": 4.0, "position": "center",
             "size": 72, "subtitle": "ANDRATX  ·  MALLORCA"},
        ],
        "cta_overlay": {"text": "COMING SOON", "start": 12.5, "duration": 2.5},
    },
    "Reveal": {
        "duration_target": 32,
        "clips": ["test_01_facade", "test_03_garden", "clip_terrasse", "clip_kueche",
                  "clip_schlafzimmer", "clip_bad", "clip_sunset_bedroom",
                  "test_01_facade"],
        "clip_durations": [3.5, 3.5, 4.0, 3.5, 3.5, 3.5, 4.0, 4.5],
        "vo_de": "Als Architekt kaufte ich eine Ruine. Einhundertfünfundzwanzig Jahre alt. Vom Landgut Son Mone. Mein Credo... so viel Originalzustand wie möglich. Sandstein. Antike Holzbalken. Eine Eingangstür aus Olivenholz. Siebenunddreißig Jahre später... ist es mehr als ein Haus. Es ist ein Vermächtnis. Son Mone. Andratsch. Eins Komma acht Millionen.",
        "vo_en": "As an architect, I bought a ruin. One hundred and twenty-five years old. From the estate of Son Mone. My creed... preserve as much of the original as possible. Sandstone. Antique wooden beams. An entrance door made of olive wood. Thirty-seven years later... it's more than a house. It's a legacy. Son Mone. Andratsch. One point eight million.",
        "music_prompt": "Cinematic emotional piano and strings, documentary film score, building intensity, luxury architecture, 35 seconds, no vocals",
        "music_duration": 35,
        "text_overlays": [
            {"text": "37 JAHRE RESTAURIERT", "start": 1.5, "duration": 3.0, "position": "lower",
             "size": 48},
            {"text": "SON MONE", "start": 25.0, "duration": 5.0, "position": "center",
             "size": 72, "subtitle": "ANDRATX  ·  MALLORCA"},
        ],
        "cta_overlay": {"text": "€ 1.800.000", "start": 28.0, "duration": 4.0},
    },
    "Lifestyle": {
        "duration_target": 22,
        "clips": ["clip_sunset_bedroom", "clip_terrasse", "test_03_garden",
                  "clip_bedroom2", "test_01_facade"],
        "clip_durations": [4.0, 4.5, 4.0, 4.0, 4.5],
        "vo_de": "Stell dir vor... aufwachen zwischen Mandelbäumen. Kaffee auf hundertvierunddreißig Quadratmetern Terrasse. Sonnenuntergang über der Tramuntana. Kein Hotel. Dein Zuhause. Son Mone.",
        "vo_en": "Imagine... waking up among almond trees. Coffee on one hundred and thirty-four square metres of terrace. Sunset over the Tramuntana. Not a hotel. Your home. Son Mone.",
        "music_prompt": "Warm Mediterranean acoustic guitar, golden hour sunset feeling, gentle uplifting, luxury lifestyle, 25 seconds, no vocals",
        "music_duration": 25,
        "text_overlays": [
            {"text": "DEIN ZUHAUSE", "start": 16.0, "duration": 4.0, "position": "center",
             "size": 64, "subtitle": "SON MONE  ·  ANDRATX"},
        ],
        "cta_overlay": {"text": "LINK IN BIO", "start": 18.5, "duration": 3.5},
    },
}

# EN text overlay replacements
EN_TEXT_MAP = {
    "37 JAHRE RESTAURIERT": "37 YEARS RESTORED",
    "DEIN ZUHAUSE": "YOUR HOME",
    "COMING SOON": "COMING SOON",
    "LINK IN BIO": "LINK IN BIO",
    "€ 1.800.000": "€ 1,800,000",
    "SON MONE": "SON MONE",
    "ANDRATX  ·  MALLORCA": "ANDRATX  ·  MALLORCA",
    "SON MONE  ·  ANDRATX": "SON MONE  ·  ANDRATX",
}


def ensure_dirs():
    OUTPUT_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    for sub in ["voiceover", "music", "clips_cropped", "overlays", "segments"]:
        (TEMP_DIR / sub).mkdir(exist_ok=True)


# ─── ELEVENLABS TTS ───────────────────────────────────────────────────

def generate_voiceover(text: str, voice_id: str, output_path: Path) -> Path:
    """Generate voiceover using ElevenLabs API."""
    if output_path.exists() and output_path.stat().st_size > 1000:
        print(f"  [CACHE] Voiceover exists: {output_path.name}")
        return output_path

    print(f"  [TTS] Generating: {output_path.name} ...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "model_id": VOICE_MODEL,
        "voice_settings": VOICE_SETTINGS
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        print(f"  [ERROR] ElevenLabs {resp.status_code}: {resp.text[:200]}")
        raise Exception(f"ElevenLabs API error: {resp.status_code}")

    output_path.write_bytes(resp.content)
    print(f"  [OK] Voiceover saved ({len(resp.content)//1024}KB)")
    return output_path


# ─── FAL.AI MUSIC ─────────────────────────────────────────────────────

def generate_music(prompt: str, duration: float, output_path: Path) -> Path:
    """Generate music using fal.ai Stable Audio."""
    if output_path.exists() and output_path.stat().st_size > 5000:
        print(f"  [CACHE] Music exists: {output_path.name}")
        return output_path

    print(f"  [MUSIC] Generating: {output_path.name} ({duration}s) ...")

    # Submit job
    url = "https://queue.fal.run/fal-ai/stable-audio"
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "seconds_total": duration,
        "steps": 100
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"  [ERROR] fal.ai submit {resp.status_code}: {resp.text[:300]}")
        raise Exception(f"fal.ai submit error: {resp.status_code}")

    result = resp.json()

    # Check if we got a queue response
    if "request_id" in result:
        request_id = result["request_id"]
        status_url = f"https://queue.fal.run/fal-ai/stable-audio/requests/{request_id}/status"
        result_url = f"https://queue.fal.run/fal-ai/stable-audio/requests/{request_id}"

        print(f"  [QUEUE] Waiting for music generation (request: {request_id[:12]}...) ...")
        for attempt in range(120):
            time.sleep(3)
            status_resp = requests.get(status_url, headers=headers, timeout=15)
            if status_resp.status_code == 200:
                status_data = status_resp.json()
                status = status_data.get("status", "UNKNOWN")
                if status == "COMPLETED":
                    # Get result
                    res_resp = requests.get(result_url, headers=headers, timeout=30)
                    if res_resp.status_code == 200:
                        result = res_resp.json()
                        break
                elif status in ("FAILED", "CANCELLED"):
                    raise Exception(f"fal.ai music generation failed: {status}")
            if attempt % 10 == 9:
                print(f"  [WAIT] Still generating... ({(attempt+1)*3}s)")
        else:
            raise Exception("fal.ai music generation timeout (360s)")

    # Extract audio URL
    audio_url = None
    if "audio_file" in result:
        audio_url = result["audio_file"].get("url")
    elif "audio" in result:
        if isinstance(result["audio"], dict):
            audio_url = result["audio"].get("url")
        else:
            audio_url = result["audio"]

    if not audio_url:
        print(f"  [DEBUG] fal.ai result keys: {list(result.keys())}")
        print(f"  [DEBUG] fal.ai result: {json.dumps(result)[:500]}")
        raise Exception("No audio URL in fal.ai response")

    # Download audio
    print(f"  [DOWNLOAD] Fetching audio ...")
    audio_resp = requests.get(audio_url, timeout=60)
    output_path.write_bytes(audio_resp.content)
    print(f"  [OK] Music saved ({len(audio_resp.content)//1024}KB)")
    return output_path


# ─── VIDEO PROCESSING ─────────────────────────────────────────────────

def crop_clip(clip_name: str) -> Path:
    """Crop a clip to 1080x1920 vertical format with color grading."""
    src = CLIPS_DIR / f"{clip_name}.mp4"
    dst = TEMP_DIR / "clips_cropped" / f"{clip_name}_cropped.mp4"

    if dst.exists() and dst.stat().st_size > 10000:
        return dst

    print(f"  [CROP] {clip_name} ...")
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-vf", f"{CROP_FILTER},{COLOR_GRADE}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-an", "-r", str(FPS),
        str(dst)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return dst


def get_duration(filepath: Path) -> float:
    """Get media file duration in seconds."""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "csv=p=0", str(filepath)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def trim_clip(src: Path, duration: float, output: Path) -> Path:
    """Trim a clip to exact duration."""
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-an", "-r", str(FPS),
        str(output)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output


# ─── TEXT OVERLAYS WITH PILLOW ────────────────────────────────────────

def find_font(size: int):
    """Find a suitable font, preferring bold/semibold."""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFCompact.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Futura.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def create_text_overlay_frame(text: str, subtitle: str = None,
                               position: str = "center", size: int = 64) -> Path:
    """Create a transparent PNG overlay with gold text on dark banner."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font = find_font(size)
    sub_font = find_font(max(24, size // 2))

    # Measure text
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    sub_h = 0
    if subtitle:
        sbbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        sub_h = sbbox[3] - sbbox[1] + 20

    total_h = th + sub_h + 60  # padding
    banner_w = max(tw, 600) + 80

    # Position
    if position == "center":
        y = HEIGHT // 2 - total_h // 2
    elif position == "lower":
        y = int(HEIGHT * 0.72)
    else:
        y = int(HEIGHT * 0.15)

    x = (WIDTH - banner_w) // 2

    # Draw dark banner
    banner = Image.new("RGBA", (banner_w, total_h), DARK_BG)
    img.paste(banner, (x, y), banner)

    # Draw gold text centered
    tx = (WIDTH - tw) // 2
    ty = y + 25
    draw.text((tx, ty), text, fill=GOLD, font=font)

    # Draw subtitle if present
    if subtitle:
        sbbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        stw = sbbox[2] - sbbox[0]
        stx = (WIDTH - stw) // 2
        sty = ty + th + 15
        draw.text((stx, sty), subtitle, fill=GOLD, font=sub_font)

    out = TEMP_DIR / "overlays" / f"overlay_{text[:15].replace(' ','_')}_{size}.png"
    img.save(str(out))
    return out


def create_cta_frame(text: str) -> Path:
    """Create CTA overlay at bottom."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font = find_font(42)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    banner_w = tw + 80
    banner_h = th + 40
    x = (WIDTH - banner_w) // 2
    y = HEIGHT - 280

    banner = Image.new("RGBA", (banner_w, banner_h), DARK_BG)
    img.paste(banner, (x, y), banner)

    tx = (WIDTH - tw) // 2
    ty = y + 17
    draw.text((tx, ty), text, fill=GOLD, font=font)

    out = TEMP_DIR / "overlays" / f"cta_{text[:15].replace(' ','_')}.png"
    img.save(str(out))
    return out


# ─── REEL ASSEMBLY ────────────────────────────────────────────────────

def build_reel(reel_name: str, lang: str):
    """Build a complete reel for given language."""
    reel = REELS[reel_name]
    lang_suffix = "DE" if lang == "de" else "EN"
    print(f"\n{'='*60}")
    print(f"BUILDING: Reel_{reel_name}_{lang_suffix}_FINAL.mp4")
    print(f"{'='*60}")

    vo_key = f"vo_{lang}"
    vo_text = reel[vo_key]
    voice_id = VOICE_DE if lang == "de" else VOICE_EN

    # 1. Generate voiceover
    vo_path = TEMP_DIR / "voiceover" / f"vo_{reel_name}_{lang}.mp3"
    generate_voiceover(vo_text, voice_id, vo_path)
    vo_duration = get_duration(vo_path)
    print(f"  [INFO] Voiceover duration: {vo_duration:.1f}s")

    # 2. Generate music (shared between DE/EN)
    music_path = TEMP_DIR / "music" / f"music_{reel_name}.wav"
    generate_music(reel["music_prompt"], reel["music_duration"], music_path)

    # 3. Crop all clips
    cropped_clips = []
    for clip_name in reel["clips"]:
        cropped = crop_clip(clip_name)
        cropped_clips.append(cropped)

    # 4. Determine target duration (use voiceover duration + small buffer)
    target_dur = max(vo_duration + 1.5, reel["duration_target"])
    print(f"  [INFO] Target duration: {target_dur:.1f}s")

    # 5. Create trimmed segments
    segment_paths = []
    clip_durations = reel["clip_durations"]
    # Scale durations to match target
    total_clip_dur = sum(clip_durations)
    scale = target_dur / total_clip_dur if total_clip_dur > 0 else 1.0

    for i, (cropped, dur) in enumerate(zip(cropped_clips, clip_durations)):
        seg_dur = dur * scale
        seg_path = TEMP_DIR / "segments" / f"seg_{reel_name}_{lang}_{i:02d}.mp4"
        trim_clip(cropped, seg_dur, seg_path)
        segment_paths.append(seg_path)

    # 6. Concatenate with crossfades using complex filter
    print(f"  [VIDEO] Building video with crossfades ...")
    video_no_audio = TEMP_DIR / f"video_{reel_name}_{lang}_noaudio.mp4"

    if len(segment_paths) == 1:
        # Just copy
        subprocess.run(["cp", str(segment_paths[0]), str(video_no_audio)], check=True)
    else:
        # Build xfade filter chain
        n = len(segment_paths)
        inputs = []
        for sp in segment_paths:
            inputs.extend(["-i", str(sp)])

        # Calculate offsets
        seg_durs = []
        for sp in segment_paths:
            seg_durs.append(get_duration(sp))

        # Build filter
        filter_parts = []
        offset = seg_durs[0] - CROSSFADE_DUR

        # First xfade
        filter_parts.append(
            f"[0:v][1:v]xfade=transition=fade:duration={CROSSFADE_DUR}:offset={offset:.3f}[v01]"
        )
        current_dur = offset + seg_durs[1]  # Duration after first xfade

        prev_label = "v01"
        for i in range(2, n):
            offset = current_dur - CROSSFADE_DUR
            out_label = f"v{i:02d}"
            filter_parts.append(
                f"[{prev_label}][{i}:v]xfade=transition=fade:duration={CROSSFADE_DUR}:offset={offset:.3f}[{out_label}]"
            )
            current_dur = offset + seg_durs[i]
            prev_label = out_label

        filter_str = ";".join(filter_parts)

        cmd = ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", filter_str,
            "-map", f"[{prev_label}]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-r", str(FPS),
            str(video_no_audio)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [WARN] xfade failed, falling back to concat ...")
            print(f"  [DEBUG] {result.stderr[-500:]}")
            # Fallback: simple concat
            concat_file = TEMP_DIR / f"concat_{reel_name}_{lang}.txt"
            with open(concat_file, "w") as f:
                for sp in segment_paths:
                    f.write(f"file '{sp}'\n")
            cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-r", str(FPS),
                str(video_no_audio)
            ]
            subprocess.run(cmd, capture_output=True, check=True)

    video_dur = get_duration(video_no_audio)
    print(f"  [INFO] Video duration: {video_dur:.1f}s")

    # 7. Create text overlay images and apply via ffmpeg
    print(f"  [OVERLAY] Creating text overlays ...")
    overlay_inputs = []
    overlay_filters = []
    input_idx = 1  # 0 is video

    for ov in reel.get("text_overlays", []):
        text = ov["text"]
        subtitle = ov.get("subtitle")
        if lang == "en":
            text = EN_TEXT_MAP.get(text, text)
            if subtitle:
                subtitle = EN_TEXT_MAP.get(subtitle, subtitle)

        overlay_img = create_text_overlay_frame(
            text, subtitle, ov.get("position", "center"), ov.get("size", 64)
        )
        overlay_inputs.extend(["-i", str(overlay_img)])

        start = ov["start"]
        end = start + ov["duration"]
        overlay_filters.append(
            f"[tmp{input_idx-1}][{input_idx}:v]overlay=0:0:enable='between(t,{start},{end})'[tmp{input_idx}]"
        )
        input_idx += 1

    # CTA overlay
    cta = reel.get("cta_overlay")
    if cta:
        cta_text = cta["text"]
        if lang == "en":
            cta_text = EN_TEXT_MAP.get(cta_text, cta_text)
        cta_img = create_cta_frame(cta_text)
        overlay_inputs.extend(["-i", str(cta_img)])
        start = cta["start"]
        end = start + cta["duration"]
        overlay_filters.append(
            f"[tmp{input_idx-1}][{input_idx}:v]overlay=0:0:enable='between(t,{start},{end})'[tmp{input_idx}]"
        )
        input_idx += 1

    video_with_overlays = TEMP_DIR / f"video_{reel_name}_{lang}_overlays.mp4"

    if overlay_filters:
        # Chain: [0:v] -> [tmp0], then overlay chain
        full_filter = f"[0:v]copy[tmp0];" + ";".join(overlay_filters)
        final_label = f"tmp{input_idx-1}"

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_no_audio),
        ] + overlay_inputs + [
            "-filter_complex", full_filter,
            "-map", f"[{final_label}]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-r", str(FPS),
            str(video_with_overlays)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [WARN] Overlay failed: {result.stderr[-400:]}")
            print(f"  [WARN] Proceeding without overlays")
            video_with_overlays = video_no_audio
    else:
        video_with_overlays = video_no_audio

    # 8. Mix audio: voiceover + music
    print(f"  [AUDIO] Mixing voiceover + music ...")
    final_output = OUTPUT_DIR / f"Reel_{reel_name}_{lang_suffix}_FINAL.mp4"

    # Trim music to video duration, lower volume
    # VO at full volume, music at 0.15 volume, fade out music at end
    final_video_dur = get_duration(video_with_overlays)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_with_overlays),
        "-i", str(vo_path),
        "-i", str(music_path),
        "-filter_complex",
        f"[1:a]adelay=500|500,apad=whole_dur={final_video_dur}[vo];"
        f"[2:a]atrim=0:{final_video_dur},volume=0.12,afade=t=out:st={final_video_dur-2}:d=2[bg];"
        f"[vo][bg]amix=inputs=2:duration=shortest:dropout_transition=2,"
        f"atrim=0:{final_video_dur}[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-r", str(FPS),
        "-shortest",
        str(final_output)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ERROR] Final mix: {result.stderr[-500:]}")
        # Fallback: just video + voiceover
        print(f"  [FALLBACK] Trying video + voiceover only ...")
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_with_overlays),
            "-i", str(vo_path),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(final_output)
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    final_dur = get_duration(final_output)
    final_size = final_output.stat().st_size / (1024*1024)
    print(f"  [DONE] {final_output.name}: {final_dur:.1f}s, {final_size:.1f}MB")
    return final_output


# ─── MAIN ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("FINCA SON MONE — BLOCKBUSTER REELS GENERATOR v2")
    print("=" * 60)

    ensure_dirs()

    results = []
    for reel_name in ["Teaser", "Reveal", "Lifestyle"]:
        for lang in ["de", "en"]:
            try:
                out = build_reel(reel_name, lang)
                results.append((reel_name, lang, out, True))
            except Exception as e:
                print(f"\n  [FAILED] {reel_name} {lang}: {e}")
                import traceback
                traceback.print_exc()
                results.append((reel_name, lang, None, False))

    print("\n" + "=" * 60)
    print("ERGEBNIS:")
    print("=" * 60)
    for name, lang, path, ok in results:
        status = "OK" if ok else "FEHLER"
        lang_s = "DE" if lang == "de" else "EN"
        if ok and path:
            dur = get_duration(path)
            size = path.stat().st_size / (1024*1024)
            print(f"  [{status}] Reel_{name}_{lang_s}_FINAL.mp4 — {dur:.1f}s, {size:.1f}MB")
        else:
            print(f"  [{status}] Reel_{name}_{lang_s}_FINAL.mp4")

    success = sum(1 for _, _, _, ok in results if ok)
    print(f"\n{success}/6 Reels erfolgreich erstellt.")


if __name__ == "__main__":
    main()
