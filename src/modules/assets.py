import os
import requests
import json
import random
from concurrent.futures import ThreadPoolExecutor
from src.config import Config

class AssetEngine:
    PEXELS_BASE_URL = "https://api.pexels.com/videos/search"
    EURON_IMAGE_URL = "https://api.euron.one/v1/images/generations"  # Standard OpenAI-compatible endpoint
    
    @staticmethod
    def download_scene_assets(scenes, use_ai_images=False):
        """
        Downloads videos or generates AI images for each scene based on the Toggle Switch.
        Returns Dictionary: { scene_id: "path/to/file" }
        """
        mode_label = "AI ARTIST" if use_ai_images else "STOCK FOOTAGE"
        print(f"📦 ASSET ENGINE: Fetching {len(scenes)} assets via [{mode_label}]...")
        
        asset_map = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Pass the 'use_ai_images' flag to the worker
            future_to_scene = {
                executor.submit(AssetEngine._process_single_scene, scene, use_ai_images): scene['id'] 
                for scene in scenes
            }
            
            for future in future_to_scene:
                scene_id = future_to_scene[future]
                try:
                    path = future.result()
                    if path:
                        asset_map[scene_id] = path
                except Exception as e:
                    print(f"⚠️ Failed to process scene {scene_id}: {e}")
        
        return asset_map

    @staticmethod
    def _process_single_scene(scene, use_ai_images):
        """Decides whether to download video or generate image"""
        scene_id = scene.get('id')
        visual_plan = scene.get('visual', {})
        query = visual_plan.get('query', 'abstract background')
        
        # --- PATH A: AI MODE FORCED (The Storyteller) ---
        if use_ai_images:
            print(f"🎨 AI MODE: Generating image for '{query}'...")
            # Enhance prompt for better AI art
            art_prompt = f"Cinematic shot of {query}, highly detailed, 8k, photorealistic, dramatic lighting, vertical 9:16 aspect ratio"
            return AssetEngine.generate_ai_image(art_prompt, f"scene_{scene_id}.jpg")

        # --- PATH B: STOCK VIDEO MODE (Original) ---
        # 1. First, try to get a Real Video from Pexels
        video_path = AssetEngine.search_and_download_video(query, f"scene_{scene_id}.mp4")
        if video_path:
            return video_path
            
        # 2. If Video Fails, Fallback to AI Image
        print(f"⚠️ Pexels failed for '{query}'. Falling back to AI...")
        fallback_prompt = f"Cinematic shot of {query}, high resolution"
        return AssetEngine.generate_ai_image(fallback_prompt, f"scene_{scene_id}.jpg")

    @staticmethod
    def search_and_download_video(query, filename):
        """Downloads a SINGLE video from Pexels."""
        if not Config.PEXELS_API_KEY: return None
        
        headers = {"Authorization": Config.PEXELS_API_KEY}
        params = {"query": query, "orientation": "portrait", "per_page": 3, "size": "medium"}
        
        try:
            r = requests.get(AssetEngine.PEXELS_BASE_URL, headers=headers, params=params, timeout=10)
            if r.status_code != 200: return None
            
            data = r.json()
            videos = data.get('videos', [])
            
            if videos:
                # Pick best quality MP4 (HD but not 4K)
                for video in videos:
                    for file in video.get("video_files", []):
                        if file.get("file_type") == "video/mp4" and 700 < file.get("width", 0) < 2000:
                            return AssetEngine._download_file(file.get("link"), filename)
                
                # Fallback to first available if strictly filtered one not found
                if videos[0].get("video_files"):
                     return AssetEngine._download_file(videos[0]["video_files"][0].get("link"), filename)
            return None
        except:
            return None

    @staticmethod
    def _download_file(url, filename):
        save_path = os.path.join(Config.TEMP_DIR, filename)
        try:
            with requests.get(url, stream=True, timeout=20) as r:
                r.raise_for_status()
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return save_path
        except:
            return None

    @staticmethod
    def generate_ai_image(prompt: str, filename: str):
        """
        Generates AI Image using GEMINI 3 PRO (Nano Banana) via Euron.
        Falls back to Pollinations if Euron fails.
        """
        save_path = os.path.join(Config.TEMP_DIR, filename)
        
        # --- PRIMARY: GEMINI 3 PRO (EURON) ---
        if Config.EURIAI_API_KEY:
            # print(f"✨ GEN: Using Gemini 3 Pro for '{prompt[:20]}...'")
            headers = {
                "Authorization": f"Bearer {Config.EURIAI_API_KEY}",
                "Content-Type": "application/json"
            }
            # Euron uses standard OpenAI Image Format
            data = {
                "model": "gemini-3-pro-image-preview", # The specific model ID you found
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "standard"
            }
            
            try:
                resp = requests.post(AssetEngine.EURON_IMAGE_URL, headers=headers, json=data, timeout=30)
                
                if resp.status_code == 200:
                    json_data = resp.json()
                    if 'data' in json_data and len(json_data['data']) > 0:
                        image_url = json_data['data'][0]['url']
                        print(f"✨ Gemini 3 Generated: {filename}")
                        return AssetEngine._download_file(image_url, filename)
                
                # If we get here, Euron failed but didn't crash
                # print(f"⚠️ Euron Image Error: {resp.text[:100]}... Switching to Fallback.")
                
            except Exception as e:
                print(f"⚠️ Euron Connection Failed: {e}")

        # --- FALLBACK: POLLINATIONS (FREE) ---
        print(f"🎨 FALLBACK: Using Pollinations for '{prompt[:20]}...'")
        encoded_prompt = requests.utils.quote(prompt)
        # We request 9:16 vertical aspect ratio (1080x1920)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&model=flux"
        
        path = AssetEngine._download_file(url, filename)
        if path:
             print(f"🎨 Pollinations Generated: {filename}")
             return path
        return None