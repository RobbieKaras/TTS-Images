# --- ✅ Install dependencies (stable, tested versions) ---
!pip install moviepy==1.0.3 Pillow==10.2.0 gTTS==2.5.1 openai-whisper==20231117 \
faster-whisper==1.0.3 typing-extensions==4.9.0 torch==2.2.2 torchaudio==2.2.2 \
numpy==1.26.4 tqdm==4.66.2 --upgrade --no-cache-dir

# --- Imports ---
import os
import json
import glob
from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import whisper

# --- Mount Google Drive ---
from google.colab import drive
drive.mount('/content/drive')

# --- Configuration ---
JSON_FOLDER = '/content/drive/MyDrive/SaintVideos/JSON'   # folder with monthly JSON files
IMAGE_FOLDER = '/content/drive/MyDrive/SaintVideos/images'  # saints images folder
OUTPUT_FOLDER = '/content/drive/MyDrive/SaintVideos/Output'  # where videos will be saved
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

img_width, img_height = 1080, 1920
font_size = 80
text_color = "white"
bg_color_rgba = (0, 0, 0, 0)
font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# --- Helper functions ---
def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)

# Load Whisper model once
print("Loading Whisper model...")
model = whisper.load_model("base")  # tiny/small for faster speed

# --- Process each JSON file in the folder ---
json_files = sorted(glob.glob(os.path.join(JSON_FOLDER, '*.json')))
for json_file in json_files:
    print(f"\nProcessing JSON file: {os.path.basename(json_file)}")
    with open(json_file, 'r') as f:
        data = json.load(f)

    for person in data:
        saint_name = person['name']
        description = person['description']
        person_id = person['person_id']
        prayer = person.get('prayer', "")

        safe_name = sanitize_filename(saint_name)
        video_path = os.path.join(OUTPUT_FOLDER, f"{safe_name}.mp4")

        # --- Skip if video already exists ---
        if os.path.exists(video_path):
            print(f"Video for {saint_name} already exists, skipping...")
            continue

        # --- Build TTS text (exclude saint name) ---
        if prayer.strip():
            full_text = f"{description} Prayer: {prayer}"
        else:
            full_text = description

        # --- Image path (support PNG, JPG, JPEG) ---
        IMAGE_PATH = None
        for ext in [".png", ".jpg", ".jpeg"]:
            test_path = os.path.join(IMAGE_FOLDER, f"{person_id}{ext}")
            if os.path.exists(test_path):
                IMAGE_PATH = test_path
                break
        if not IMAGE_PATH:
            print(f"Warning: Image not found for {person_id}, skipping this entry.")
            continue

        print(f"\n--- Generating video for {saint_name} ---")

        # --- Generate TTS audio ---
        audio_file_path = f"temp_narration.wav"
        tts = gTTS(text=full_text, lang='en', slow=False)
        tts.save(audio_file_path)
        audio_clip = AudioFileClip(audio_file_path)
        total_audio_duration = audio_clip.duration
        print(f"Total audio duration: {total_audio_duration:.2f} seconds")

        # --- Whisper transcription ---
        result = model.transcribe(audio_file_path, word_timestamps=True)
        whisper_words_data = []
        for segment in result['segments']:
            for word_info in segment['words']:
                whisper_words_data.append({
                    'word': word_info['word'].strip(),
                    'start': word_info['start'],
                    'end': word_info['end']
                })

        if not whisper_words_data:
            # fallback if Whisper fails
            words_for_fallback = full_text.split()
            num_words = len(words_for_fallback)
            avg_word_duration = total_audio_duration / max(num_words, 1)
            current_time = 0
            for word in words_for_fallback:
                whisper_words_data.append({
                    'word': word,
                    'start': current_time,
                    'end': current_time + avg_word_duration
                })
                current_time += avg_word_duration

        # --- Create visual word clips ---
        video_clips = []
        for i, word_info in enumerate(whisper_words_data):
            word = word_info['word']
            start_time = word_info['start']
            end_time = word_info['end']
            duration = max(end_time - start_time, 0.05)

            img = Image.new("RGBA", (img_width, img_height), bg_color_rgba)
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), word, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x_pos = (img_width - w) / 2
            y_pos = (img_height - h) / 2

            # --- Draw text with black border ---
            outline_range = 4  # thickness of border
            for ox in range(-outline_range, outline_range + 1):
                for oy in range(-outline_range, outline_range + 1):
                    draw.text((x_pos + ox, y_pos + oy), word, font=font, fill="black")

            # --- Draw main white text on top ---
            draw.text((x_pos, y_pos), word, font=font, fill=text_color)

            img_path = f"frame_{i}.png"
            img.save(img_path)

            clip = ImageClip(img_path).set_duration(duration).set_start(start_time).set_position("center")
            video_clips.append(clip)

        # --- Background / Saint image clip (full background) ---
        bg_clip = ImageClip(IMAGE_PATH).resize(height=img_height).set_duration(total_audio_duration)
        bg_clip = bg_clip.crop(
            x_center=bg_clip.w / 2,
            y_center=bg_clip.h / 2,
            width=img_width,
            height=img_height
        )
        video_clips.insert(0, bg_clip)

        # --- Compose final video ---
        final = CompositeVideoClip(video_clips).set_audio(audio_clip)
        final = final.set_duration(total_audio_duration)

        # --- Write video to Drive ---
        print(f"Writing video: {video_path}")
        final.write_videofile(video_path, fps=24, threads=4)

        # --- Clean up temporary files ---
        for f in os.listdir('.'):
            if f.startswith('frame_') and f.endswith('.png'):
                os.remove(f)
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

print("\nAll videos generated for all JSON files!")
