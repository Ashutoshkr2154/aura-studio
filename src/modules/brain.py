import json
import os
import requests
from openai import OpenAI
from src.config import Config

class Brain:
    def __init__(self, euri_key_override=None):
        self.openai_client = None
        if Config.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Euri Configuration (Allow Override from UI for Creator Edition)
        self.euri_key = euri_key_override if euri_key_override else Config.EURIAI_API_KEY
        self.euri_url = "https://api.euron.one/api/v1/euri/chat/completions"
        self.euri_model = "gpt-4.1-nano" # Or "gpt-4o" if available on Euri

    def _get_master_prompt(self, language, structure, duration, audience, style):
        """
        AURA 4.6: The 'Render Safe' System Prompt.
        Integrates User Controls for Audience, Style, and Duration.
        """
        return f"""
# ==========================================================
# SYSTEM IDENTITY: "AURA 4.6 - PREMIUM VIDEO OUTPUT FIXER"
# ==========================================================
You are a Professional YouTuber + Video Editor + AI Engineer.
Your goal: Generate a PREMIUM, RELEVANT short video plan.

# ✅ USER CONTEXT
- Language: {language}
- Structure: {structure}
- Target Duration: {duration}
- Audience: {audience}
- Style: {style}

# ==========================================================
# MODULE 1: TOPIC RELEVANCE LOCK
# ==========================================================
1. Extract primary keyword & 5 supporting keywords.
2. EXACT subtopics (micro-points). Every scene must map to a subtopic.
3. No random clip selection.

# ==========================================================
# MODULE 2: VIDEO SCRIPT (COMPLETE FEEL)
# ==========================================================
Structure:
- Hook (0–2s): Shocking statement / Pattern Interrupt.
- Intro (2–6s): What & Why.
- Body (6–45s): 3-5 Value points (No fluff).
- Ending (45–55s): Summary.
- CTA (55-60s): Loop back line.

# ==========================================================
# MODULE 3: VISUAL RELEVANCE RULES
# ==========================================================
For every scene:
- Provide highly specific Pexels search query.
- If topic is abstract (e.g. "Peace"), search for concrete object (e.g. "Monk meditating").
- Confidence Score > 85 required.

# ==========================================================
# MODULE 4: AUDIO & SYNC RULES
# ==========================================================
- Video Duration MUST == Voice Duration (+0.3s buffer).
- Music enabled: True (Auto-ducking ON).
- Logo visible: True.

# ==========================================================
# ✅ FINAL OUTPUT (JSON ONLY)
# ==========================================================
Return ONLY valid JSON with this structure:
{{
  "upload_metadata": {{
    "title": "Viral Clickbait Title",
    "description": "SEO optimized description...",
    "tags": ["tag1", "tag2"],
    "hashtags": ["#tag1", "#tag2"]
  }},
  "marketing": {{
      "ctr_titles": ["Title 1", "Title 2"],
      "seo_tags": ["tag1", "tag2"],
      "seo_description": "...",
      "thumbnail_ideas": ["Idea 1", "Idea 2"]
  }},
  "meta": {{ "engine": "AURA_4.6", "language": "{language}" }},
  "script": {{ "full_voiceover": "...", "hook": "...", "mood": "Energetic" }},
  "branding": {{ "logo_opacity": 0.8, "logo_position": "top_right" }},
  "music": {{ "mood": "auto", "volume": 0.2 }},
  "scenes": [
    {{
      "id": 1,
      "narration": "...",
      "visual": {{ "query": "...", "fallback": "..." }},
      "overlay_text": "...",
      "duration_estimate": 3.5
    }}
  ]
}}
"""

    def generate_video_blueprint(self, topic: str, language: str = "English", structure: str = "Default", duration: str = "60s", audience: str = "General", style: str = "Fast Paced"):
        print(f"🧠 AURA BRAIN: Analyzing '{topic}' [{structure}] for {audience} in {style} style...")
        
        # Load the Master Prompt with NEW Inputs
        system_instruction = self._get_master_prompt(language, structure, duration, audience, style)

        # --- ATTEMPT 1: OPENAI (PRIMARY) ---
        if self.openai_client:
            try:
                print("🔹 Attempting with OpenAI...")
                return self._call_openai(topic, system_instruction)
            except Exception as e:
                print(f"⚠️ OpenAI Failed: {e}")
                print("🔄 Switching to Backup Engine (Euri AI)...")
        
        # --- ATTEMPT 2: EURI AI (FALLBACK) ---
        if self.euri_key:
            try:
                return self._call_euri(topic, system_instruction)
            except Exception as e:
                print(f"❌ Euri AI Failed: {e}")
        else:
            print("⚠️ No Euri API Key found in .env or Settings")

        print("❌ CRITICAL: Both Brains failed.")
        return None

    def _call_openai(self, topic, system_instruction):
        """Standard OpenAI Call"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Topic: {topic}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        return self._process_response(response.choices[0].message.content)

    def _call_euri(self, topic, system_instruction):
        """Fallback Euri Call using Requests"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.euri_key}"
        }
        
        user_prompt = f"Topic: {topic}\nREMINDER: Output Valid JSON ONLY. No markdown."

        payload = {
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "model": self.euri_model,
            "max_tokens": 3000, # Increased for larger 4.6 blueprints
            "temperature": 0.7
        }

        response = requests.post(self.euri_url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")
            
        data = response.json()
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
            # Clean up potential markdown formatting
            clean_content = raw_content.replace("```json", "").replace("```", "").strip()
            blueprint = json.loads(clean_content)
        except json.JSONDecodeError:
            print("❌ Error: AI did not return valid JSON.")
            return None
        
        # Validation
        if not blueprint.get('script', {}).get('full_voiceover'):
             print("❌ JSON missing script.")
             return None
             
        print(f"✅ BLUEPRINT GENERATED: {blueprint.get('upload_metadata', {}).get('title', 'Untitled')}")
        return blueprint