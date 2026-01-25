import os
import sys
from dotenv import load_dotenv

# Load secrets
load_dotenv()

# ==========================================================
# 🔧 SMART IMAGEMAGICK CONFIG (Windows vs. Cloud)
# ==========================================================
# 1. If running locally on Windows (Your Laptop)
if os.name == 'nt':
    IMAGEMAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
    if os.path.exists(IMAGEMAGICK_PATH):
        print(f"✅ Local ImageMagick Detected: {IMAGEMAGICK_PATH}")
        os.environ["IMAGEMAGICK_BINARY"] = IMAGEMAGICK_PATH
    else:
        print("⚠️ Local ImageMagick not found. Please check C:\\Program Files\\")

# 2. If running on Cloud (Linux/Streamlit)
else:
    # On Cloud, we rely on the system installation + policy.xml
    # We also define a fallback font for Linux
    print("☁️ Cloud Environment Detected. Using System ImageMagick.")

# ==========================================================
# ⚙️ MAIN CONFIGURATION
# ==========================================================
class Config:
    # 🔐 AUTHENTICATION
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EURIAI_API_KEY = os.getenv("EURIAI_API_KEY")
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    
    # 📂 DIRECTORY STRUCTURE
    # Fixes the 'asssets' typo by strictly using 'assets'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
    SFX_DIR = os.path.join(ASSETS_DIR, "sfx")
    FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
    TEMP_DIR = os.path.join(ASSETS_DIR, "temp")
    
    DATA_DIR = os.path.join(BASE_DIR, "data")
    OUTPUT_DIR = os.path.join(DATA_DIR, "output")
    
    # 🎥 VIDEO STANDARDS
    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920
    FPS = 30 # 30 is safer for Cloud rendering than 60
    
    # Subtitle Settings (Cloud Safe Font)
    # On Windows, Arial works. On Cloud, DejaVuSans is safer.
    FONT_NAME = os.path.join(FONTS_DIR, "bold.ttf")
    FONT_SIZE = 70
    FONT_COLOR = "yellow"
    STROKE_COLOR = "white"
    STROKE_WIDTH = 3

    # 🚑 VALIDATION
    @classmethod
    def validate(cls):
        # We only fail if BOTH keys are missing (Backup Brain logic)
        if not cls.OPENAI_API_KEY and not cls.EURIAI_API_KEY:
            # Just a warning instead of crash, allows UI to show error nicely
            print("⚠️ WARNING: No AI Keys found. App may fail to generate scripts.")
            
        # Ensure Critical Folders Exist
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.MUSIC_DIR, exist_ok=True) # Creates 'music' folder if missing

Config.validate()