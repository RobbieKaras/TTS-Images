# Text-to-Speech Video Generator

This project began as a collaboration with the developers of the **Daily Divine** Android and iOS app.  
The goal was to create a simple, automated way to apply **text-to-speech narration** to an image — turning written descriptions into engaging, narrated videos.

The system works by using a **JSON file** that specifies:
- The **image name** (used to match with the corresponding picture), goes under "id"
- The **output video name**, goes under "title"
- The **description**, which becomes the **spoken narration** in the video, goes under "description"

**Example JSON (`data.json`):**
```json
[
  {
    "id": "001",
    "title": "Mount Everest",
    "description": "Mount Everest is Earth's highest mountain above sea level."
  }
]
```

Over time, the project has grown beyond its original purpose.  
This repository now includes multiple versions:

1. **General Version** — Works with any dataset or topic  
2. **Google Colab Version** — Uses Google Drive for easy cloud-based rendering  
3. **Saints (Daily Divine) Version** — The original build made for the app’s saint profiles  

***Scrolling Code:***

In each folder will be a version with the text scrolling instead of each word one at a time. The only thing you need to do differently is use that code instead of the original; everything else will be the same in the instructions. 

The **Daily Divine** team plans to begin uploading videos made with this system starting **January 1st**, and I will provide a link to their page when it is available.

---

## Setup Instructions

### 1. General Version (Local Use)

This version is for anyone who wants to run the project **on their own computer** (Windows, macOS, or Linux). It doesn’t require Colab or an internet connection once set up.

---

#### Step 1: Install Python
Before anything else, make sure **Python 3.8 or newer** is installed on your system.

- **Windows:** Download it from [python.org/downloads](https://www.python.org/downloads/).  
  During installation, **check the box that says “Add Python to PATH.”**
- **macOS/Linux:** Python is usually preinstalled. To verify, open a terminal and run:
  ```bash
  python --version
  ```
  or
  ```bash
  python3 --version
  ```

---

#### Step 2: Download the Project Files
Download everything from the **Local Example** folder in this repository and organize it like this on your computer:

```
project/
├── narrated_video_generator.py      # Main script
├── requirements.txt                 # Dependency list
├── JSON/
│   └── data.json                    # Your text-to-speech content
├── images/
│   ├── 001.png
│   └── 002.jpg
└── Output/                          # Videos will be saved here
```

---

####  Step 3: Format Your JSON File
Your JSON file contains the text that will be spoken and displayed in the video.

**Example (`data.json`):**
```json
[
  {
    "id": "001",
    "title": "Mount Everest",
    "description": "Mount Everest is Earth's highest mountain above sea level."
  }
]
```

- `id` → must match the image name (e.g., `001.png`)  
- `title` → name used for the video file  
- `description` → what the text-to-speech engine will read  

Here, you can add more lines to the JSON file or change the existing title and description

---

#### Step 4: Open Command Prompt or Terminal
Use your operating system’s terminal:
- **Windows:** Press `Win + R`, type `cmd`, and hit Enter.  
- **macOS/Linux:** Open the “Terminal” app.  

Then navigate to your project folder. Example:
```bash
cd Desktop/project
```

---

#### Step 5: Install the Dependencies
Once inside the project folder, install everything using:
```bash
pip install -r requirements.txt
```
This installs all the packages needed for the script to run properly.

---

#### Step 6: Run the Script
Now you’re ready to generate your videos!  
Run the following command:
```bash
python narrated_video_generator.py --json_folder JSON --image_folder images --output_folder Output
```

After a few moments, your finished videos will appear in the **Output** folder.

✅ *This version runs completely offline after installation.*  
✅ *Each entry in your JSON automatically becomes a narrated video.*

---

### 2. Google Colab Version

This version lets you create narrated videos **entirely in Google Colab**, with your files stored in **Google Drive**.  
You don’t need to install anything on your computer — just follow these simple steps.

---

#### Step 1: Open Google Drive and Create Folders

1. Go to [Google Drive](https://drive.google.com/).  
2. Inside **My Drive**, create a new folder called:
   ```
   TTS-Project
   ```
3. Inside the **TTS-Project** folder, create three subfolders:
   ```
   TTS-Project/
   ├── JSON/       ← where your .json files will go
   ├── Images/     ← where your .jpg or .png files will go
   └── Output/     ← where generated videos will be saved
   ```

Your Drive should look like this:
```
My Drive
└── TTS-Project
    ├── JSON
    ├── Images
    └── Output
```

---

#### 📄 Step 2: Add Your Files

1. Place your **JSON file(s)** inside the `JSON` folder.  
   Example `data.json`:
   ```json
   [
     {
       "id": "001",
       "title": "Mount Everest",
       "description": "Mount Everest is Earth's highest mountain above sea level."
     }
   ]
   ```

2. Upload your **images** to the `Images` folder.  
   Each image name should match the `"id"` in your JSON file:
   ```
   001.jpg
   002.png
   ```

---

#### Step 3: Open Google Colab

1. Visit [Google Colab](https://colab.research.google.com).  
2. Click **File → New Notebook**.  
3. Copy and paste the entire **Colab version** of the script from this repository into the first cell.  
   *(No changes needed — it already includes the correct pip installations at the top.)*

---


#### Step 4: Verify Your Folder Paths

The code already includes default paths:
```python
JSON_FOLDER = '/content/drive/MyDrive/TTS-Project/JSON'
IMAGE_FOLDER = '/content/drive/MyDrive/TTS-Project/Images'
OUTPUT_FOLDER = '/content/drive/MyDrive/TTS-Project/Output'
```

If you used the folder names above, **you don’t need to change anything**.  
If your folders have different names, update the paths accordingly.

---

#### Step 5: Run the Script

  
The script will automatically:
   - Install all required dependencies
   - Mount your Google Drive (Requires you to log into your Google account)
   - Read each JSON file in your Drive  
   - Match images by ID  
   - Generate videos with text-to-speech narration  
   - Save the finished videos to the `Output` folder in your Drive  

---

✅ Works with `.jpg`, `.jpeg`, and `.png`  
✅ Automatically loops through all JSON files in your `JSON` folder  
✅ Requires no code editing — just copy, paste, and run  

After a few minutes, check your Google Drive’s **Output** folder — your videos will appear there, ready to share or upload.

---

### 3. Saints Version (Daily Divine Original)

This was also run through Google Collab, so follow the same instructions but with the code from the Saints Example folder.

---

##  Dependencies

All versions use the same tested package versions:

```text
moviepy==1.0.3
Pillow==10.2.0
gTTS==2.5.1
openai-whisper==20231117
faster-whisper==1.0.3
typing-extensions==4.9.0
torch==2.2.2
torchaudio==2.2.2
numpy==1.26.4
tqdm==4.66.2
```

To install everything locally:
```bash
pip install -r requirements.txt
```

---

## 📄 License & Attribution

This project is open for educational and creative use.  
Original concept developed in collaboration with the **Daily Divine** app team.  
© 2025 Daily Divine & Contributors. All rights reserved.
