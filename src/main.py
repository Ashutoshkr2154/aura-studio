import os
import sys

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.modules.brain import Brain
from src.modules.voice import VoiceEngine
from src.modules.assets import AssetEngine
from src.modules.editor import VideoEditor
from src.modules.utils import clean_temp_folder

def run_aura_pipeline(topic: str):
    print("\n" + "="*60)
    print(f"🚀 AURA 4.1 (MULTI-SCENE): Processing '{topic}'")
    print("="*60 + "\n")
    
    # 0. Clean up old temporary files (Crucial for multi-scene)
    clean_temp_folder(Config.TEMP_DIR)
    
    # --- PHASE 1: THE BRAIN ---
    brain = Brain()
    blueprint = brain.generate_video_blueprint(topic)
    
    if not blueprint:
        print("❌ ABORT: Brain failed to generate blueprint.")
        return

    # Extract Key Data
    script_text = blueprint.get('script', {}).get('full_voiceover')
    scenes = blueprint.get('scenes', []) # Grab ALL scenes
    
    if not script_text:
        print("❌ ABORT: Empty script.")
        return

    # --- PHASE 2: ASSET PROCUREMENT ---
    print("\n📦 PHASE 2: GATHERING ASSETS")
    
    # 2.1 Voice
    audio_path = os.path.join(Config.TEMP_DIR, "voice_main.mp3")
    if not VoiceEngine.generate_audio(script_text, audio_path):
        print("❌ Voice failed.")
        return

    # 2.2 Visuals (Download Multiple Scenes)
    # The Asset Engine will loop through the scenes and download a clip for each
    video_paths = AssetEngine.download_scene_assets(scenes)

    if not video_paths:
        print("⚠️ Visuals failed. Editor will use Black Screen fallback.")

    # --- PHASE 3: PRODUCTION ---
    print("\n🎬 PHASE 3: FINAL ASSEMBLY")
    
    assets = {
        "audio_path": audio_path,
        "video_paths": video_paths  # Pass the LIST of videos
    }
    
    final_output = VideoEditor.assemble_video(blueprint, assets)
    
    if final_output:
        print("\n" + "="*60)
        print(f"✅ MISSION SUCCESS: Video Rendered Successfully!")
        print(f"📂 Location: {final_output}")
        print("="*60)
        
        # Open the folder for the user
        try:
            os.startfile(Config.OUTPUT_DIR)
        except:
            pass
    else:
        print("\n❌ MISSION FAILED during rendering.")

if __name__ == "__main__":
    while True:
        user_input = input("\n💡 Enter Video Topic (or 'q' to quit): ")
        if user_input.lower() == 'q':
            break
        run_aura_pipeline(user_input)