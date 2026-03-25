#!/usr/bin/env python3
"""
Build Reel 2 (Teaser) and Reel 3 (Lifestyle) for Finca Cay Fingerle.
Generates voiceovers, music, processes video clips, and assembles final reels.
"""

import os
import sys
import json
import time
import struct
import subprocess
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Paths ──
BASE = Path("/Users/angelojuric/Documents/Cay Fingerle/Finca Cay Fingerle/social-media")
CLIPS = BASE / "clips_raw"
OUTPUT = BASE / "output"
TMP = BASE / "tmp_reels23"
TMP.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)

# ── API Keys ──
ELEVEN_KEY = "10435adb57d9183a835901bdafba5771cc1ac0f193686eb1fe0fb0f14224c9a4"
FAL_KEY = "bcfcfd01-4c85-4bc7-be5b-988a92ca5262:d46a4a43bf2da74351df2ffd3b7a8d28"

# ── Voice IDs ──
VOICE_DE = "Tn4bhLlhD26sndFn0Kgw"  # TommHH Radiovoice
VOICE_EN = "JBFqnCBsd6RMkjVDRZzb"  # George

# ── Fonts ──
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"

# ── Colors ──
GOLD = (201, 169, 110)      # #C9A96E
WHITE = (255, 255, 255)
BG_DARK = (44, 36, 32)
OVERLAY_BG = (0, 0, 0, 140)  # semi-transparent black


def run(cmd, desc=""):
    """Run a shell command, raise on error."""
    print(f"  [CMD] {desc or cmd[:80]}...")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [ERR] {r.stderr[:500]}")
        raise RuntimeError(f"Command failed: {desc}\n{r.stderr[:500]}")
    return r.stdout


# ═══════════════════════════════════════
# 1) VOICEOVER GENERATION (ElevenLabs)
# ═══════════════════════════════════════

def generate_voiceover(text: str, voice_id: str, out_path: Path, lang: str):
    """Generate voiceover via ElevenLabs TTS API."""
    if out_path.exists() and out_path.stat().st_size > 1000:
        print(f"  [SKIP] Voiceover exists: {out_path.name}")
        return

    print(f"  [TTS] Generating {lang} voiceover: {text[:50]}...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVEN_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.3,
            "similarity_boost": 0.85,
            "style": 0.8,
            "use_speaker_boost": True
        }
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    print(f"  [OK] Voiceover saved: {out_path.name} ({out_path.stat().st_size} bytes)")


# ═══════════════════════════════════════
# 2) MUSIC GENERATION (fal.ai Stable Audio)
# ═══════════════════════════════════════

def generate_music_fal(prompt: str, duration: float, out_path: Path):
    """Generate music via fal.ai Stable Audio."""
    if out_path.exists() and out_path.stat().st_size > 5000:
        print(f"  [SKIP] Music exists: {out_path.name}")
        return

    print(f"  [MUSIC] Generating: {prompt[:60]}...")

    # Submit request
    submit_url = "https://queue.fal.run/fal-ai/stable-audio"
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "seconds_total": duration,
        "steps": 100
    }
    resp = requests.post(submit_url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # If we got a request_id, poll for result
    if "request_id" in data:
        req_id = data["request_id"]
        print(f"  [MUSIC] Queued, request_id={req_id}, polling...")
        status_url = f"https://queue.fal.run/fal-ai/stable-audio/requests/{req_id}/status"
        result_url = f"https://queue.fal.run/fal-ai/stable-audio/requests/{req_id}"

        for attempt in range(120):
            time.sleep(3)
            st = requests.get(status_url, headers=headers, timeout=15)
            st_data = st.json()
            status = st_data.get("status", "UNKNOWN")
            if status == "COMPLETED":
                print(f"  [MUSIC] Completed, fetching result...")
                res = requests.get(result_url, headers=headers, timeout=30)
                data = res.json()
                break
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Music generation failed: {st_data}")
            if attempt % 10 == 0:
                print(f"  [MUSIC] Still waiting... ({status})")
        else:
            raise RuntimeError("Music generation timed out after 6 minutes")

    # Extract audio URL from result
    audio_url = None
    if "audio_file" in data:
        audio_url = data["audio_file"].get("url") if isinstance(data["audio_file"], dict) else data["audio_file"]
    elif "output" in data:
        out_data = data["output"]
        if isinstance(out_data, dict) and "audio_file" in out_data:
            af = out_data["audio_file"]
            audio_url = af.get("url") if isinstance(af, dict) else af

    # Try other common response formats
    if not audio_url:
        for key in ["audio", "url", "file"]:
            if key in data:
                val = data[key]
                audio_url = val.get("url") if isinstance(val, dict) else val
                if audio_url:
                    break

    if not audio_url:
        print(f"  [WARN] Response structure: {json.dumps(data, indent=2)[:500]}")
        raise RuntimeError("Could not extract audio URL from fal.ai response")

    # Download audio
    print(f"  [MUSIC] Downloading audio...")
    audio_resp = requests.get(audio_url, timeout=60)
    audio_resp.raise_for_status()
    out_path.write_bytes(audio_resp.content)
    print(f"  [OK] Music saved: {out_path.name} ({out_path.stat().st_size} bytes)")


# ═══════════════════════════════════════
# 3) VIDEO PROCESSING HELPERS
# ═══════════════════════════════════════

def crop_clip(src: Path, dst: Path, start: float, end: float, color_grade=True, blur=False):
    """Crop a clip to 9:16 (1080x1920) with optional color grading and blur."""
    if dst.exists() and dst.stat().st_size > 5000:
        print(f"  [SKIP] Clip exists: {dst.name}")
        return

    duration = end - start
    filters = []

    # Trim
    # Scale to height 1920 maintaining aspect, then crop center 1080
    filters.append("scale=-1:1920")
    filters.append("crop=1080:1920")

    if blur:
        filters.append("boxblur=2:1")

    if color_grade:
        # Warm Mediterranean color grade
        filters.append("eq=contrast=1.08:brightness=0.02:saturation=1.15")
        filters.append("curves=master='0/0 0.25/0.22 0.5/0.52 0.75/0.80 1/1'")

    vf = ",".join(filters)
    cmd = (
        f'ffmpeg -y -ss {start} -t {duration} -i "{src}" '
        f'-vf "{vf}" -c:v libx264 -preset fast -crf 18 -an -r 24 '
        f'"{dst}"'
    )
    run(cmd, f"Crop {src.name} -> {dst.name}")


def create_title_card(text: str, dst: Path, duration: float = 2.0,
                       font_size: int = 56, bg_color=BG_DARK, text_color=GOLD):
    """Create a title card (black/dark frame with centered text) as video."""
    if dst.exists() and dst.stat().st_size > 1000:
        print(f"  [SKIP] Title card exists: {dst.name}")
        return

    # Create image
    img = Image.new("RGB", (1080, 1920), bg_color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_BOLD, font_size)

    # Get text size and center it
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (1080 - tw) // 2
    y = (1920 - th) // 2

    draw.text((x, y), text, fill=text_color, font=font)

    img_path = dst.with_suffix(".png")
    img.save(str(img_path))

    # Convert to video
    cmd = (
        f'ffmpeg -y -loop 1 -i "{img_path}" -t {duration} '
        f'-vf "format=yuv420p" -c:v libx264 -preset fast -crf 18 -r 24 '
        f'"{dst}"'
    )
    run(cmd, f"Title card -> {dst.name}")


def add_text_overlay(src: Path, dst: Path, text: str, position="bottom",
                      font_size: int = 44, text_color=WHITE):
    """Burn text overlay onto a video clip using PIL frame-by-frame via pipe."""
    if dst.exists() and dst.stat().st_size > 5000:
        print(f"  [SKIP] Overlay exists: {dst.name}")
        return

    print(f"  [OVERLAY] Adding text '{text}' to {src.name}...")

    # Get clip info
    probe = subprocess.run(
        f'ffprobe -v error -show_entries stream=width,height,nb_frames,duration -of json "{src}"',
        shell=True, capture_output=True, text=True
    )
    info = json.loads(probe.stdout)["streams"][0]
    w, h = int(info["width"]), int(info["height"])
    dur = float(info.get("duration", "3"))
    total_frames = int(dur * 24)

    font = ImageFont.truetype(FONT_BOLD, font_size)

    # Create overlay image once
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Measure text
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Position
    pad_x, pad_y = 30, 15
    if position == "bottom":
        tx = (w - tw) // 2
        ty = h - th - 180
    elif position == "center":
        tx = (w - tw) // 2
        ty = (h - th) // 2
    else:
        tx = (w - tw) // 2
        ty = 200

    # Draw semi-transparent background bar
    bar_x0 = tx - pad_x
    bar_y0 = ty - pad_y
    bar_x1 = tx + tw + pad_x
    bar_y1 = ty + th + pad_y
    draw.rounded_rectangle([bar_x0, bar_y0, bar_x1, bar_y1], radius=12, fill=OVERLAY_BG)
    draw.text((tx, ty), text, fill=text_color, font=font)

    # Save overlay as PNG
    overlay_png = TMP / f"overlay_{dst.stem}.png"
    overlay.save(str(overlay_png))

    # Use FFmpeg overlay filter
    cmd = (
        f'ffmpeg -y -i "{src}" -i "{overlay_png}" '
        f'-filter_complex "[0:v][1:v]overlay=0:0" '
        f'-c:v libx264 -preset fast -crf 18 -an -r 24 '
        f'"{dst}"'
    )
    run(cmd, f"Overlay text on {dst.name}")


def get_duration(path: Path) -> float:
    """Get duration of a media file."""
    r = subprocess.run(
        f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{path}"',
        shell=True, capture_output=True, text=True
    )
    return float(r.stdout.strip())


def concat_with_crossfade(clips: list, out: Path, fade_dur: float = 0.4):
    """Concatenate clips with crossfade transitions using xfade filter."""
    if out.exists() and out.stat().st_size > 10000:
        print(f"  [SKIP] Concat exists: {out.name}")
        return

    if len(clips) == 1:
        run(f'cp "{clips[0]}" "{out}"', "Copy single clip")
        return

    # Get durations
    durations = [get_duration(c) for c in clips]
    print(f"  [CONCAT] {len(clips)} clips, durations: {[f'{d:.2f}s' for d in durations]}")

    # Build xfade filter chain
    inputs = " ".join(f'-i "{c}"' for c in clips)

    if len(clips) == 2:
        offset = durations[0] - fade_dur
        filter_str = f'[0:v][1:v]xfade=transition=fade:duration={fade_dur}:offset={offset},format=yuv420p'
        cmd = f'ffmpeg -y {inputs} -filter_complex "{filter_str}" -c:v libx264 -preset fast -crf 18 -r 24 "{out}"'
    else:
        # Chain xfades for multiple clips
        filter_parts = []
        current_offset = durations[0] - fade_dur

        # First xfade
        filter_parts.append(
            f'[0:v][1:v]xfade=transition=fade:duration={fade_dur}:offset={current_offset}[v01]'
        )

        for i in range(2, len(clips)):
            prev_label = f'v{str(i-2).zfill(1)}{str(i-1).zfill(1)}'
            # Accumulated duration minus fades already applied
            current_offset = current_offset + durations[i-1] - fade_dur
            if i < len(clips) - 1:
                next_label = f'v{str(i-1).zfill(1)}{str(i).zfill(1)}'
                filter_parts.append(
                    f'[{prev_label}][{i}:v]xfade=transition=fade:duration={fade_dur}:offset={current_offset}[{next_label}]'
                )
            else:
                filter_parts.append(
                    f'[{prev_label}][{i}:v]xfade=transition=fade:duration={fade_dur}:offset={current_offset},format=yuv420p'
                )

        filter_str = ";".join(filter_parts)
        cmd = f'ffmpeg -y {inputs} -filter_complex "{filter_str}" -c:v libx264 -preset fast -crf 18 -r 24 "{out}"'

    run(cmd, f"Crossfade concat -> {out.name}")


def mix_audio_video(video: Path, voiceover: Path, music: Path, out: Path,
                     video_dur: float, music_vol: float = 0.15, vo_vol: float = 1.0,
                     fade_out_music: float = 2.0):
    """Mix video with voiceover and background music."""
    if out.exists() and out.stat().st_size > 10000:
        print(f"  [SKIP] Final exists: {out.name}")
        return

    print(f"  [MIX] Combining audio for {out.name}...")

    # Audio filter: mix voiceover + music with volume control and fade out
    # Trim music to video duration, apply volume and fade out
    afilter = (
        f'[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={vo_vol}[vo];'
        f'[2:a]aformat=sample_rates=44100:channel_layouts=stereo,'
        f'atrim=0:{video_dur},volume={music_vol},'
        f'afade=t=out:st={video_dur - fade_out_music}:d={fade_out_music}[bg];'
        f'[vo][bg]amix=inputs=2:duration=longest:dropout_transition=2[aout]'
    )

    cmd = (
        f'ffmpeg -y -i "{video}" -i "{voiceover}" -i "{music}" '
        f'-filter_complex "{afilter}" -map 0:v -map "[aout]" '
        f'-c:v copy -c:a aac -b:a 192k -shortest '
        f'"{out}"'
    )
    run(cmd, f"Final mix -> {out.name}")


# ═══════════════════════════════════════
# MAIN BUILD
# ═══════════════════════════════════════

def main():
    print("=" * 60)
    print("  REEL PRODUCTION: Teaser + Lifestyle")
    print("=" * 60)

    # ─── Step 1: Generate all voiceovers ───
    print("\n[STEP 1] Generating Voiceovers...")

    vo_teaser_de = TMP / "vo_teaser_de.mp3"
    vo_teaser_en = TMP / "vo_teaser_en.mp3"
    vo_lifestyle_de = TMP / "vo_lifestyle_de.mp3"
    vo_lifestyle_en = TMP / "vo_lifestyle_en.mp3"

    generate_voiceover(
        "Manche Häuser... erzählen Jahrhunderte. Coming Soon.",
        VOICE_DE, vo_teaser_de, "DE"
    )
    generate_voiceover(
        "Some houses... tell centuries. Coming Soon.",
        VOICE_EN, vo_teaser_en, "EN"
    )
    generate_voiceover(
        "Stell dir vor... aufwachen, und das hier ist dein Blick. Kein Urlaub. Dein Zuhause. Deine Finca in Andratsch.",
        VOICE_DE, vo_lifestyle_de, "DE"
    )
    generate_voiceover(
        "Imagine... waking up, and this is your view. Not a holiday. Your home. Your finca in Andratsch.",
        VOICE_EN, vo_lifestyle_en, "EN"
    )

    # ─── Step 2: Generate Music ───
    print("\n[STEP 2] Generating Music...")

    music_teaser = TMP / "music_teaser.wav"
    music_lifestyle = TMP / "music_lifestyle.wav"

    generate_music_fal(
        "Mysterious ambient drone, minimal piano notes, suspenseful atmosphere, luxury teaser, no vocals, 15 seconds",
        15, music_teaser
    )
    generate_music_fal(
        "Warm Mediterranean acoustic guitar, feel-good sunny atmosphere, gentle and uplifting, luxury lifestyle, no vocals, 20 seconds",
        20, music_lifestyle
    )

    # ─── Step 3: Process Video Clips for TEASER ───
    print("\n[STEP 3] Processing Teaser Clips...")

    # Teaser Scene 1: clip_terrasse.mp4 (0.5s-3s) — NO text
    t1_terrasse = TMP / "t1_terrasse.mp4"
    crop_clip(CLIPS / "clip_terrasse.mp4", t1_terrasse, 0.5, 3.0)

    # Teaser Scene 2: test_01_facade.mp4 (0.5s-3s) — blurred
    t1_facade = TMP / "t1_facade.mp4"
    crop_clip(CLIPS / "test_01_facade.mp4", t1_facade, 0.5, 3.0, blur=True)

    # Teaser Scene 3: Black frame "Coming Soon" 2s
    t1_coming = TMP / "t1_coming_soon.mp4"
    create_title_card("Coming Soon", t1_coming, duration=2.0, font_size=64)

    # Teaser Scene 4: Black frame "Link in Bio" 2s
    t1_link = TMP / "t1_link_bio.mp4"
    create_title_card("Link in Bio", t1_link, duration=2.0, font_size=56)

    # ─── Step 4: Process Video Clips for LIFESTYLE ───
    print("\n[STEP 4] Processing Lifestyle Clips...")

    # Scene 1: clip_sunset_bedroom (0.3s-3.5s) — Text "Stell dir vor..."
    l_sunset_raw = TMP / "l_sunset_raw.mp4"
    l_sunset = TMP / "l_sunset.mp4"
    crop_clip(CLIPS / "clip_sunset_bedroom.mp4", l_sunset_raw, 0.3, 3.5)
    add_text_overlay(l_sunset_raw, l_sunset, "Stell dir vor...", position="bottom", font_size=46)

    # Scene 1 EN version
    l_sunset_en = TMP / "l_sunset_en.mp4"
    add_text_overlay(l_sunset_raw, l_sunset_en, "Imagine...", position="bottom", font_size=46)

    # Scene 2: clip_terrasse (0.5s-3s) — NO text
    l_terrasse = TMP / "l_terrasse.mp4"
    crop_clip(CLIPS / "clip_terrasse.mp4", l_terrasse, 0.5, 3.0)

    # Scene 3: test_03_garden (0.3s-3s) — NO text
    l_garden = TMP / "l_garden.mp4"
    crop_clip(CLIPS / "test_03_garden.mp4", l_garden, 0.3, 3.0)

    # Scene 4: clip_schlafzimmer (0.3s-3s) — Text "Dein Zuhause"
    l_schlaf_raw = TMP / "l_schlaf_raw.mp4"
    l_schlaf_de = TMP / "l_schlaf_de.mp4"
    crop_clip(CLIPS / "clip_schlafzimmer.mp4", l_schlaf_raw, 0.3, 3.0)
    add_text_overlay(l_schlaf_raw, l_schlaf_de, "Dein Zuhause", position="bottom", font_size=46)

    # Scene 4 EN
    l_schlaf_en = TMP / "l_schlaf_en.mp4"
    add_text_overlay(l_schlaf_raw, l_schlaf_en, "Your Home", position="bottom", font_size=46)

    # Scene 5: test_01_facade (0.5s-3.5s) — Text "Link in Bio"
    l_facade_raw = TMP / "l_facade_raw.mp4"
    l_facade = TMP / "l_facade.mp4"
    crop_clip(CLIPS / "test_01_facade.mp4", l_facade_raw, 0.5, 3.5)
    add_text_overlay(l_facade_raw, l_facade, "Link in Bio", position="bottom", font_size=46)

    # ─── Step 5: Assemble Teaser Reel ───
    print("\n[STEP 5] Assembling Teaser Reel...")

    teaser_video = TMP / "teaser_video.mp4"
    concat_with_crossfade(
        [t1_terrasse, t1_facade, t1_coming, t1_link],
        teaser_video, fade_dur=0.4
    )

    teaser_dur = get_duration(teaser_video)
    print(f"  Teaser video duration: {teaser_dur:.2f}s")

    # DE version
    mix_audio_video(
        teaser_video, vo_teaser_de, music_teaser,
        OUTPUT / "Reel_Teaser_DE_FINAL.mp4",
        teaser_dur, music_vol=0.18, vo_vol=1.0
    )

    # EN version
    mix_audio_video(
        teaser_video, vo_teaser_en, music_teaser,
        OUTPUT / "Reel_Teaser_EN_FINAL.mp4",
        teaser_dur, music_vol=0.18, vo_vol=1.0
    )

    # ─── Step 6: Assemble Lifestyle Reel ───
    print("\n[STEP 6] Assembling Lifestyle Reel...")

    # DE version
    lifestyle_video_de = TMP / "lifestyle_video_de.mp4"
    concat_with_crossfade(
        [l_sunset, l_terrasse, l_garden, l_schlaf_de, l_facade],
        lifestyle_video_de, fade_dur=0.4
    )

    lifestyle_dur_de = get_duration(lifestyle_video_de)
    print(f"  Lifestyle DE video duration: {lifestyle_dur_de:.2f}s")

    mix_audio_video(
        lifestyle_video_de, vo_lifestyle_de, music_lifestyle,
        OUTPUT / "Reel_Lifestyle_DE_FINAL.mp4",
        lifestyle_dur_de, music_vol=0.15, vo_vol=1.0
    )

    # EN version
    lifestyle_video_en = TMP / "lifestyle_video_en.mp4"
    concat_with_crossfade(
        [l_sunset_en, l_terrasse, l_garden, l_schlaf_en, l_facade],
        lifestyle_video_en, fade_dur=0.4
    )

    lifestyle_dur_en = get_duration(lifestyle_video_en)
    print(f"  Lifestyle EN video duration: {lifestyle_dur_en:.2f}s")

    mix_audio_video(
        lifestyle_video_en, vo_lifestyle_en, music_lifestyle,
        OUTPUT / "Reel_Lifestyle_EN_FINAL.mp4",
        lifestyle_dur_en, music_vol=0.15, vo_vol=1.0
    )

    # ─── Step 7: Verify ───
    print("\n[STEP 7] Verification...")
    finals = [
        "Reel_Teaser_DE_FINAL.mp4",
        "Reel_Teaser_EN_FINAL.mp4",
        "Reel_Lifestyle_DE_FINAL.mp4",
        "Reel_Lifestyle_EN_FINAL.mp4",
    ]
    all_ok = True
    for name in finals:
        p = OUTPUT / name
        if p.exists():
            sz = p.stat().st_size / (1024 * 1024)
            dur = get_duration(p)
            print(f"  [OK] {name}: {sz:.1f} MB, {dur:.1f}s")
        else:
            print(f"  [FAIL] {name}: MISSING!")
            all_ok = False

    if all_ok:
        print("\n" + "=" * 60)
        print("  ALLE 4 REELS ERFOLGREICH ERSTELLT!")
        print("=" * 60)
    else:
        print("\n  [WARN] Einige Dateien fehlen!")

    return all_ok


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
