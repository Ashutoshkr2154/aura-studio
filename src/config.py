import os
from dotenv import load_dotenv

# Load secrets
load_dotenv()

# ==========================================================
# 🔧 IMAGEMAGICK CONFIGURATION (MANUAL OVERRIDE)
# ==========================================================
# We explicitly tell MoviePy where to find ImageMagick.
IMAGEMAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

if os.path.exists(IMAGEMAGICK_PATH):
    print(f"✅ ImageMagick Detected: {IMAGEMAGICK_PATH}")
    os.environ["IMAGEMAGICK_BINARY"] = IMAGEMAGICK_PATH
else:
    print(f"❌ CRITICAL: Could not find ImageMagick at: {IMAGEMAGICK_PATH}")
    print("👉 Please double-check the folder name in C:\\Program Files\\")

# ==========================================================
# ⚙️ MAIN CONFIGURATION
# ==========================================================
class Config:
    # 🔐 AUTHENTICATION
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EURIAI_API_KEY = os.getenv("EURIAI_API_KEY") # <--- NEW: Added Euri Key
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    
    # 📂 DIRECTORY STRUCTURE
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
    SFX_DIR = os.path.join(ASSETS_DIR, "sfx")
    FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
    TEMP_DIR = os.path.join(ASSETS_DIR, "temp")
    
    DATA_DIR = os.path.join(BASE_DIR, "data")
    OUTPUT_DIR = os.path.join(DATA_DIR, "output")
    MEMORY_DIR = os.path.join(DATA_DIR, "memory")
    
    SYSTEM_PROMPT_PATH = os.path.join(BASE_DIR, "system_prompt.txt")

    # 🎥 VIDEO STANDARDS
    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920
    FPS = 30
    
    # Subtitle Settings
    FONT_NAME = "Arial-Bold" 
    FONT_SIZE = 70
    FONT_COLOR = "yellow"
    STROKE_COLOR = "black"
    STROKE_WIDTH = 3

    # 🚑 VALIDATION
    @classmethod
    def validate(cls):
        # UPDATED LOGIC: We only fail if BOTH keys are missing.
        if not cls.OPENAI_API_KEY and not cls.EURIAI_API_KEY:
            raise ValueError("❌ CRITICAL ERROR: Both OPENAI_API_KEY and EURIAI_API_KEY are missing in .env")
            
        if not os.path.exists(cls.OUTPUT_DIR):
            os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
            
Config.validate()