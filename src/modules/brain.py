import json
import os
import requests
from openai import OpenAI
from src.config import Config

class Brain:
    def __init__(self):
        self.openai_client = None
        if Config.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Euri Configuration
        self.euri_url = "https://api.euron.one/api/v1/euri/chat/completions"
        self.euri_model = "gpt-4.1-nano" # Or "gpt-4o" if available on Euri

    def _load_system_prompt(self):
        if not os.path.exists(Config.SYSTEM_PROMPT_PATH):
            return ""
        with open(Config.SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()

    def generate_video_blueprint(self, topic: str, language: str = "English"):
        print(f"🧠 AURA BRAIN: Analyzing topic '{topic}' in {language}...")
        
        base_instruction = self._load_system_prompt()
        if not base_instruction:
            print("❌ Error: System Prompt missing.")
            return None

        # --- 🚀 PROMPT INJECTION (SEO + LANGUAGE) ---
        # We append specific instructions to force the AI to give us Premium Data
        extended_instruction = base_instruction + f"""
        
        IMPORTANT UPDATES:
        1. LANGUAGE: The 'full_voiceover' MUST be written in {language}.
        2. SEO & MARKETING: You must add a "marketing" key to the JSON with:
           - "ctr_titles": [List of 3 viral, clickbaity titles]
           - "seo_description": "A YouTube description with keywords"
           - "seo_tags": [List of 15 high-volume tags]
           - "thumbnail_ideas": [List of 3 visual concepts for a thumbnail]
        """

        # --- ATTEMPT 1: OPENAI (PRIMARY) ---
        if self.openai_client:
            try:
                print("🔹 Attempting with OpenAI...")
                return self._call_openai(topic, extended_instruction)
            except Exception as e:
                print(f"⚠️ OpenAI Failed: {e}")
                print("🔄 Switching to Backup Engine (Euri AI)...")
        
        # --- ATTEMPT 2: EURI AI (FALLBACK) ---
        if Config.EURIAI_API_KEY:
            try:
                return self._call_euri(topic, extended_instruction)
            except Exception as e:
                print(f"❌ Euri AI Failed: {e}")
        else:
            print("⚠️ No Euri API Key found in .env")

        print("❌ CRITICAL: Both Brains failed.")
        return None

    def _call_openai(self, topic, system_instruction):
        """Standard OpenAI Call"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Status: READY\nInput Topic: {topic}\nOutput: JSON ONLY."}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        return self._process_response(response.choices[0].message.content)

    def _call_euri(self, topic, system_instruction):
        """Fallback Euri Call using Requests"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.EURIAI_API_KEY}"
        }
        
        # Euri might not support 'response_format': 'json_object', so we emphasize it in the prompt
        user_prompt = f"Status: READY\nInput Topic: {topic}\nOutput: VALID JSON ONLY. NO MARKDOWN."

        payload = {
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "model": self.euri_model,
            "max_tokens": 1500, # Increased token limit for SEO data
            "temperature": 0.7
        }

        response = requests.post(self.euri_url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")
            
        data = response.json()
        
        # Adjust this path based on Euri's actual response structure
        # Assuming it mimics OpenAI's structure:
        raw_content = data['choices'][0]['message']['content']
        return self._process_response(raw_content)

    def _process_response(self, raw_content):
        """Helper to parse and save debug JSON"""
        # Save Debug
        debug_path = os.path.join(Config.TEMP_DIR, "debug_last_response.json")
        try:
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(raw_content)
        except Exception:
            pass
            
        try:
            blueprint = json.loads(raw_content)
        except json.JSONDecodeError:
            print("❌ Error: AI did not return valid JSON.")
            return None
        
        # Validation
        if not blueprint.get('script', {}).get('full_voiceover'):
             print("❌ JSON missing script.")
             return None
             
        print(f"✅ BLUEPRINT GENERATED: {blueprint.get('upload_metadata', {}).get('title', 'Untitled')}")
        return blueprint