This is the official **README.md** for your project.

It is professional, detailed, and explains everything—from features to installation and deployment. Create a file named `README.md` in your root folder and paste this content.

---

# ⚡ AURA Studio | AI Video Automation Engine

**AURA (Automated Universal Recording Assistant)** is a professional-grade AI video production studio. It transforms a simple text topic into a fully edited, viral short-form video (Shorts/Reels/TikTok) in seconds.

It handles the entire pipeline: **Scriptwriting, Voiceover, Stock Footage Scouting, Video Editing, Subtitling, Background Music, and SEO Strategy.**

---

## 💎 Key Features

### 🧠 **1. AI Core (The Brain)**

* **Smart Scripting:** Uses **OpenAI GPT-4o** (with Euri AI backup) to write engaging, viral scripts.
* **Multi-Language Support:** Generates native content in **English, Hindi, Spanish, French, and German**.
* **Content Intelligence:** Automatically generates **Viral Titles, SEO Tags, Descriptions**, and **AI Thumbnail Concepts**.

### 🎬 **2. Professional Editing Suite**

* **Neural Voice Engine:** Ultra-realistic Text-to-Speech using Microsoft Edge Neural Voices (Nova, Alloy, Echo, Swara, etc.).
* **Smart Asset Scouting:** Fetches high-quality, vertical HD footage from **Pexels** based on context.
* **Jukebox Engine:** Automatically mixes background music based on mood (Chill, Phonk, Upbeat, etc.).
* **Branding:** Burns your **Channel Logo** and **Watermark** directly into the video.
* **Dynamic Subtitles:** Auto-generated captions perfectly synced with the voiceover.

### 🚀 **3. Cloud & Deployment Ready**

* **Streamlit UI:** A beautiful, responsive "Platinum" interface (Dark/Light modes).
* **Cross-Platform:** Works on Windows, Mac, and **Linux Cloud Servers** (Streamlit Cloud).
* **Mobile Optimized:** Generate videos from your phone via the web interface.

---

## 🛠️ Installation (Local)

Follow these steps to run AURA on your own machine.

### **1. Clone the Repository**

```bash
git clone https://github.com/YOUR_USERNAME/aura-studio.git
cd aura-studio

```

### **2. Install Dependencies**

Ensure you have Python 3.8+ installed.

```bash
pip install -r requirements.txt

```

### **3. Configure Environment Secrets**

Create a `.env` file in the root directory and add your API keys:

```ini
# Required for Script Generation
OPENAI_API_KEY="sk-..."
# Optional Backup Brain
EURIAI_API_KEY="sk-..."
# Required for Stock Footage
PEXELS_API_KEY="..."

```

### **4. Setup Music Library (Crucial Manual Step)**

The automated Jukebox needs MP3 files.

1. Go to `assets/music/` (Create the folder if missing).
2. Add MP3 files and rename them **exactly** as follows:
* `chill.mp3`
* `upbeat.mp3`
* `dramatic.mp3`
* `phonk.mp3`
* `corporate.mp3`



### **5. Run the Studio**

```bash
streamlit run src/app.py

```

Access the app at `http://localhost:8501`.

---

## ☁️ Deployment (Streamlit Cloud)

AURA is optimized for free deployment on Streamlit Community Cloud.

1. **Push your code to GitHub** (Ensure `.env` is ignored!).
2. Go to **[share.streamlit.io](https://share.streamlit.io/)** and click "New App".
3. Select your repository and set the main file to `src/app.py`.
4. **Important:** In the Streamlit Dashboard settings, go to **Secrets** and paste your API keys there (same format as `.env`).
5. **System Dependencies:** The included `packages.txt` file automatically installs `ffmpeg` and `imagemagick` on the server.

---

## 📂 Project Structure

```text
AURA_4.0/
├── assets/
│   └── music/           # Place your .mp3 files here
├── data/
│   ├── output/          # Generated videos save here
│   └── temp/            # Temporary downloads (cleaned auto)
├── src/
│   ├── modules/
│   │   ├── brain.py     # AI Scripting & Strategy Logic
│   │   ├── voice.py     # TTS Engine (Edge-TTS)
│   │   ├── assets.py    # Pexels Downloader & AI Image Gen
│   │   ├── editor.py    # MoviePy Video Assembler
│   │   └── utils.py     # Helper functions
│   ├── app.py           # Main Streamlit UI (Frontend)
│   └── config.py        # Configuration & Path Management
├── .env                 # API Keys (Local only)
├── .gitignore           # Git ignore rules
├── packages.txt         # Linux System Dependencies (ffmpeg)
├── requirements.txt     # Python Libraries
└── README.md            # Documentation

```

---

## 🧩 Usage Guide

1. **Dashboard:** Check system health and recent production stats.
2. **Creative Studio:**
* **Topic:** Enter any idea (e.g., "History of Bitcoin").
* **Settings:** Choose Language (Hindi/English/etc.), Voice, and Music Vibe.
* **Branding:** Upload your logo and set a watermark text.
* **Launch:** Click "Launch Production".


3. **Content Intelligence Tab:**
* After generation, switch to this tab to see **Viral Titles**, **Tags**, and generate an **AI Thumbnail**.



---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

Author - 

Ashutosh kumar 