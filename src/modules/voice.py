import asyncio
import edge_tts
import os

class VoiceEngine:
    """
    Handles Text-to-Speech generation using Microsoft Edge's free Neural voices.
    Now supports multiple languages and voice personas.
    """
    
    # 🌍 VOICE DATABASE
    # Maps UI friendly names to internal Edge-TTS voice IDs
    VOICE_MAP = {
        # English Options
        "Nova (Female)": "en-US-AriaNeural",
        "Alloy (Male)": "en-US-GuyNeural",
        "Echo (Deep)": "en-US-ChristopherNeural",
        
        # International Options
        "Hindi": "hi-IN-SwaraNeural",       # Indian Female
        "Spanish": "es-ES-ElviraNeural",    # Spanish Female
        "French": "fr-FR-DeniseNeural",     # French Female
        "German": "de-DE-KatjaNeural",      # German Female
        
        # Fallback
        "default": "en-US-AriaNeural"
    }

    @staticmethod
    async def _generate_async(text: str, voice: str, output_path: str):
        """Internal async generator."""
        # Rate: +10% speed makes it sound more like a content creator (less robotic)
        communicate = edge_tts.Communicate(text, voice, rate="+10%")
        await communicate.save(output_path)

    @staticmethod
    def generate_audio(text: str, output_path: str, voice_name: str = "Nova (Female)"):
        """
        Generates TTS audio using the selected voice model.
        """
        # 1. Lookup the correct voice ID
        selected_voice = VoiceEngine.VOICE_MAP.get(voice_name)
        
        # 2. If not found (e.g. user selected 'English' generic), default to Nova
        if not selected_voice:
            selected_voice = VoiceEngine.VOICE_MAP["default"]

        print(f"🎙️ VOICE ENGINE: Synthesizing {len(text.split())} words with '{selected_voice}'...")
        
        try:
            # Run the async function in a sync wrapper
            asyncio.run(VoiceEngine._generate_async(text, selected_voice, output_path))
            
            if os.path.exists(output_path):
                # print(f"✅ Audio Saved: {output_path}") # Optional debug
                return True
            else:
                print("❌ Voice Error: File creation failed.")
                return False
                
        except Exception as e:
            print(f"❌ Voice Critical Error: {e}")
            return False