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

    def _get_master_prompt(self, language, structure):
        """
        AURA 4.5 PLATINUM: The 'Relevance Lock' System Prompt with Structure Support.
        """
        # --- STRUCTURE LOGIC ---
        structure_instructions = {
            "Default": "Standard engaging video with Hook, Body, and Conclusion.",
            "Myth vs Fact": "Start with a common MYTH. Debunk it immediately. Explain the FACT. Summary.",
            "Top 3 List": "Fast paced listicle. 'Here are top 3...'. Number 3, Number 2, Number 1 (The best one).",
            "Storytime": "First person narrative 'I'. 'This is how I...'. Emotional arc. Lesson learned.",
            "Did You Know?": "Start with 'Did you know...'. Present a shocking fact. Explain the science/history behind it.",
            "Motivation": "Deep, slow pacing. Philosophical quotes. Strong punchline at the end."
        }
        selected_instruction = structure_instructions.get(structure, structure_instructions["Default"])

        return f"""
        # IDENTITY
        You are AURA 4.5 (Platinum), an elite AI Video Director & YouTube Strategist. 
        Your goal is to create high-retention, viral short-form videos (Reels/Shorts).

        # USER TOPIC IS THE FOCUS.
        # LANGUAGE: {language}
        # STRUCTURE: {structure} ({selected_instruction})

        # STRICT "RELEVANCE LOCK" RULES
        1. EVERY visual, word, and overlay MUST match the topic perfectly.
        2. NO generic "person typing" clips unless the topic is specifically about typing.
        3. If the topic is abstract (e.g., "Integrity"), use metaphorical visuals (e.g., "Unbreakable chain") or specific examples.

        # VIDEO TIMING (Total 45-60s)
        1. HOOK (0-3s): Pattern interrupt. Must stop the scroll.
        2. BODY (3-50s): Follow the '{structure}' format. Fast pacing.
        3. CTA (50-60s): Loop back to start.

        # VISUAL SEARCH QUERY RULES
        - You MUST provide Pexels search queries.
        - Queries must be concrete nouns/verbs (e.g., "Lion roaring" NOT "Strength").
        - Provide 3 alternatives per scene: [Exact, Metaphor, Broad].

        # MARKETING & SEO REQUIREMENTS
        - You MUST generate "marketing" data: Clickbait titles, SEO tags, and Thumbnail concepts.

        # OUTPUT FORMAT (JSON ONLY)
        Return PURE JSON. No Markdown. No Pre-text.
        {{
            "upload_metadata": {{
                "title": "Viral Clickbait Title",
                "description": "SEO optimized description with keywords...",
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
                "hashtags": ["#tag1", "#tag2", "#tag3"]
            }},
            "marketing": {{
                "ctr_titles": ["Option 1", "Option 2", "Option 3"],
                "seo_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
                "seo_description": "Short description for YouTube...",
                "thumbnail_ideas": ["Futuristic robot face close up", "Glowing blue circuit board", "Hacker in hoodie with green code"]
            }},
            "script": {{
                "full_voiceover": "Full spoken text in {language}...",
                "mood": "Energetic"
            }},
            "scenes": [
                {{
                    "id": 1,
                    "timestamp": "00:00-00:03",
                    "narration": "First sentence...",
                    "visual": {{ "query": "specific search term" }},
                    "visual_fallbacks": ["fallback query 1", "fallback query 2"],
                    "overlay_text": "BIG HOOK HERE"
                }},
                ... (continue for all scenes)
            ]
        }}
        """

    def generate_video_blueprint(self, topic: str, language: str = "English", structure: str = "Default"):
        print(f"🧠 AURA BRAIN: Analyzing '{topic}' [{structure}] in {language}...")
        
        # Load the Master Prompt with Structure
        system_instruction = self._get_master_prompt(language, structure)

        # --- ATTEMPT 1: OPENAI (PRIMARY) ---
        if self.openai_client:
            try:
                print("🔹 Attempting with OpenAI...")
                return self._call_openai(topic, system_instruction)
            except Exception as e:
                print(f"⚠️ OpenAI Failed: {e}")
                print("🔄 Switching to Backup Engine (Euri AI)...")
        
        # --- ATTEMPT 2: EURI AI (FALLBACK) ---
        # Checks for Euri Key (Config or Override)
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
        
        # Euri might not support 'response_format': 'json_object', so we emphasize it in the prompt
        user_prompt = f"Topic: {topic}\nREMINDER: Output Valid JSON ONLY. No markdown."

        payload = {
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "model": self.euri_model,
            "max_tokens": 2500, # Increased token limit for full JSON
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
            # Clean up potential markdown formatting if Euri adds it
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
