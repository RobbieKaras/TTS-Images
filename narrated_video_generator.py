"""
Narrated Video Generator
------------------------
Create vertical videos with narration and word-by-word text animation
from JSON data and corresponding images.

Usage:
    python narrated_video_generator.py \
        --json_folder ./JSON \
        --image_folder ./images \
        --output_folder ./Output
"""

import os
import json
import glob
import argparse
from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import whisper

# ------------------ Arguments ------------------
parser = argparse.ArgumentParser(description="Generate narrated videos from JSON data.")
parser.add_argument("--json_folder", required=True, help="Folder containing JSON files.")
parser.add_argument("--image_folder", required=True, help="Folder containing images.")
parser.add_argument("--output_folder", required=True, help="Folder where videos are saved.")
parser.add_argument("--voice_lang", default="en", help="Language code for TTS (default: en).")
parser.add_argument("--font_path", default="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", help="Font path for text.")
args = parser.parse_args()

JSON_FOLDER = args.json_folder
IMAGE_FOLDER = args.image_folder
OUTPUT_FOLDER = args.output_folder
LANG = args.voice_lang
FONT_PATH = args.font_path

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ------------------ Settings ------------------
IMG_WIDTH, IMG_HEIGHT = 1080, 1920
FONT_SIZE = 80
TEXT_COLOR = "white"
BG_COLOR = (0, 0, 0, 0)

# ------------------ Helpers ------------------
def sanitize_filename(name):
    """Remove unsafe characters for filenames."""
    return "".join(c if c.isalnum() else "_" for c in name)

print("🎧 Loading Whisper model...")
model = whisper.load_model("base")

# ------------------ Main Loop ------------------
json_files = sorted(glob.glob(os.path.join(JSON_FOLDER, "*.json")))
if not json_files:
    print(f"No JSON files found in {JSON_FOLDER}")
    exit()

for json_file in json_files:
    print(f"\n📁 Processing file: {os.path.basename(json_file)}")
    with open(json_file, "r") as f:
        data = json.load(f)

    for entry in data:
        title = entry.get("title", "Untitled")
        description = entry.get("description", "")
        entry_id = entry.get("id", sanitize_filename(title))

        if not description.strip():
            print(f"⚠️ Skipping '{title}' (no description).")
            continue

        video_filename = f"{sanitize_filename(title)}.mp4"
        video_path = os.path.join(OUTPUT_FOLDER, video_filename)

        if os.path.exists(video_path):
            print(f"✅ '{video_filename}' already exists — skipping.")
            continue

        # --- Find matching image (PNG, JPG, or JPEG) ---
        possible_exts = [".png", ".jpg", ".jpeg"]
        image_path = None
        for ext in possible_exts:
            test_path = os.path.join(IMAGE_FOLDER, f"{entry_id}{ext}")
            if os.path.exists(test_path):
                image_path = test_path
                break

        if image_path is None:
            print(f"⚠️ No image found for ID '{entry_id}', skipping.")
            continue

        print(f"🎬 Creating video for: {title}")

        # ---------- Narration ----------
        audio_path = "temp_audio.wav"
        tts = gTTS(text=description, lang=LANG, slow=False)
        tts.save(audio_path)
        audio_clip = AudioFileClip(audio_path)
        total_dur = audio_clip.duration

        # ---------- Whisper word timing ----------
        result = model.transcribe(audio_path, word_timestamps=True)
        words = []
        for seg in result["segments"]:
            for w in seg["words"]:
                words.append({
                    "word": w["word"].strip(),
                    "start": w["start"],
                    "end": w["end"]
                })

        # Fallback timing if Whisper fails
        if not words:
            split_words = description.split()
            avg = total_dur / len(split_words)
            t = 0
            for w in split_words:
                words.append({"word": w, "start": t, "end": t + avg})
                t += avg

        # ---------- Generate text frames ----------
        video_clips = []
        for i, w in enumerate(words):
            word = w["word"]
            start, end = w["start"], w["end"]
            dur = max(end - start, 0.05)

            img = Image.new("RGBA", (IMG_WIDTH, IMG_HEIGHT), BG_COLOR)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

            bbox = draw.textbbox((0, 0), word, font=font)
            w_text, h_text = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x, y = (IMG_WIDTH - w_text) / 2, (IMG_HEIGHT - h_text) / 2

            # Black outline
            outline = 4
            for ox in range(-outline, outline + 1):
                for oy in range(-outline, outline + 1):
                    draw.text((x + ox, y + oy), word, font=font, fill="black")

            # Main white text
            draw.text((x, y), word, font=font, fill=TEXT_COLOR)

            frame_path = f"frame_{i}.png"
            img.save(frame_path)

            clip = ImageClip(frame_path).set_duration(dur).set_start(start).set_position("center")
            video_clips.append(clip)

        # ---------- Background image ----------
        bg = ImageClip(image_path).resize(height=IMG_HEIGHT).set_duration(total_dur)
        bg = bg.crop(x_center=bg.w / 2, y_center=bg.h / 2, width=IMG_WIDTH, height=IMG_HEIGHT)
        video_clips.insert(0, bg)

        # ---------- Final Composition ----------
        final = CompositeVideoClip(video_clips).set_audio(audio_clip).set_duration(total_dur)
        final.write_videofile(video_path, fps=24, threads=4, codec="libx264")

        # Cleanup
        for f in os.listdir("."):
            if f.startswith("frame_") and f.endswith(".png"):
                os.remove(f)
        os.remove(audio_path)

print("\n✅ All videos generated successfully!")
