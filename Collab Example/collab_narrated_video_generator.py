# --- ✅ Install dependencies (stable tested versions) ---
!pip install moviepy==1.0.3 Pillow==10.2.0 gTTS==2.5.1 openai-whisper==20231117 \
faster-whisper==1.0.3 typing-extensions==4.9.0 torch==2.2.2 torchaudio==2.2.2 \
numpy==1.26.4 tqdm==4.66.2 --upgrade --no-cache-dir

# --- Imports ---
import os, json, glob
from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import whisper

# --- Mount Google Drive ---
from google.colab import drive
drive.mount('/content/drive')

# --- Configuration (update these after mounting Drive) ---
JSON_FOLDER = '/content/drive/MyDrive/TTS-Project/JSON'      # Folder with JSON files
IMAGE_FOLDER = '/content/drive/MyDrive/TTS-Project/Images'   # Folder with JPG/PNG images
OUTPUT_FOLDER = '/content/drive/MyDrive/TTS-Project/Output'  # Output folder for videos
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Display settings ---
img_width, img_height = 1080, 1920
font_size = 80
font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
text_color = "white"

# --- Helper functions ---
def sanitize_filename(name):
    return "".join(c if c.isalnum() else "_" for c in name)

# --- Load Whisper model once ---
print("Loading Whisper model...")
model = whisper.load_model("base")

# --- Process each JSON file ---
json_files = sorted(glob.glob(os.path.join(JSON_FOLDER, '*.json')))
for json_file in json_files:
    print(f"\nProcessing JSON file: {os.path.basename(json_file)}")
    with open(json_file, 'r') as f:
        data = json.load(f)

    for item in data:
        name = item.get('name', 'Unknown')
        description = item.get('description', '')
        item_id = item.get('person_id', item.get('id', name))

        safe_name = sanitize_filename(name)
        video_path = os.path.join(OUTPUT_FOLDER, f"{safe_name}.mp4")

        # Skip existing
        if os.path.exists(video_path):
            print(f"Video for {name} already exists — skipping.")
            continue

        full_text = description

        # Find image (.jpg or .png)
        image_path = None
        for ext in ['.jpg', '.jpeg', '.png']:
            candidate = os.path.join(IMAGE_FOLDER, f"{item_id}{ext}")
            if os.path.exists(candidate):
                image_path = candidate
                break
        if not image_path:
            print(f"⚠️ Image not found for {item_id}, skipping.")
            continue

        print(f"🎬 Generating video for: {name}")

        # --- TTS ---
        tts = gTTS(text=full_text, lang='en')
        audio_file = "temp_audio.wav"
        tts.save(audio_file)
        audio_clip = AudioFileClip(audio_file)
        total_duration = audio_clip.duration

        # --- Transcription for timing ---
        result = model.transcribe(audio_file, word_timestamps=True)
        words_data = []
        for segment in result['segments']:
            for word in segment['words']:
                words_data.append({
                    'word': word['word'].strip(),
                    'start': word['start'],
                    'end': word['end']
                })

        if not words_data:
            words = full_text.split()
            avg = total_duration / max(len(words), 1)
            cur = 0
            for w in words:
                words_data.append({'word': w, 'start': cur, 'end': cur + avg})
                cur += avg

        # --- Create word clips ---
        word_clips = []
        for i, w in enumerate(words_data):
            word = w['word']
            start, end = w['start'], w['end']
            dur = max(end - start, 0.05)

            img = Image.new("RGBA", (img_width, img_height), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()

            # Outline text (black border)
            bbox = draw.textbbox((0,0), word, font=font)
            w_text = bbox[2] - bbox[0]
            h_text = bbox[3] - bbox[1]
            x = (img_width - w_text) / 2
            y = (img_height - h_text) / 2

            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    draw.text((x+dx, y+dy), word, font=font, fill="black")
            draw.text((x, y), word, font=font, fill=text_color)

            img_path = f"frame_{i}.png"
            img.save(img_path)
            clip = ImageClip(img_path).set_duration(dur).set_start(start)
            word_clips.append(clip)

        # --- Background image ---
        bg_clip = ImageClip(image_path).resize(height=img_height).set_duration(total_duration)
        bg_clip = bg_clip.crop(x_center=bg_clip.w/2, y_center=bg_clip.h/2, width=img_width, height=img_height)

        # --- Final video ---
        final = CompositeVideoClip([bg_clip] + word_clips)
        final = final.set_audio(audio_clip).set_duration(total_duration)
        final.write_videofile(video_path, fps=24, threads=4, codec='libx264')

        # --- Cleanup ---
        audio_clip.close()
        os.remove(audio_file)
        for f in os.listdir('.'):
            if f.startswith('frame_') and f.endswith('.png'):
                os.remove(f)

print("\n✅ All videos generated successfully!")
