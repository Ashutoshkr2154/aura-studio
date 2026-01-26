import os
import requests
import json
import random
from concurrent.futures import ThreadPoolExecutor
from src.config import Config

class AssetEngine:
    PEXELS_BASE_URL = "https://api.pexels.com/videos/search"
    
    @staticmethod
    def download_scene_assets(scenes):
        """
        Downloads videos for each scene and returns a DICTIONARY:
        { scene_id: "path/to/video.mp4" }
        """
        print(f"📦 ASSET ENGINE: Fetching {len(scenes)} clips...")
        
        # We use a dictionary to map ID -> Path
        asset_map = {}
        
        # Parallel Download for speed (Faster than one by one)
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_scene = {
                executor.submit(AssetEngine._process_single_scene, scene): scene['id'] 
                for scene in scenes
            }
            
            for future in future_to_scene:
                scene_id = future_to_scene[future]
                try:
                    path = future.result()
                    if path:
                        asset_map[scene_id] = path
                except Exception as e:
                    print(f"⚠️ Failed to download scene {scene_id}: {e}")
        
        return asset_map

    @staticmethod
    def _process_single_scene(scene):
        """Helper to find and download one video for a specific scene"""
        scene_id = scene.get('id')
        visual_plan = scene.get('visual', {})
        
        # 1. Extract Queries
        query = visual_plan.get('query', 'abstract background')
        fallbacks = visual_plan.get('fallbacks', [])
        
        # 2. Search Pexels (Primary)
        video_url = AssetEngine.search_pexels(query)
        
        # 3. Try Fallbacks if main query fails
        if not video_url and fallbacks:
            for fb_query in fallbacks:
                print(f"🔄 Retrying Scene {scene_id} with: '{fb_query}'")
                video_url = AssetEngine.search_pexels(fb_query)
                if video_url: break
        
        # 4. Download if found
        if video_url:
            filename = f"scene_{scene_id}_{random.randint(1000,9999)}.mp4"
            save_path = os.path.join(Config.TEMP_DIR, filename)
            
            if AssetEngine._download_file(video_url, save_path):
                return save_path
                
        return None

    @staticmethod
    def search_pexels(query):
        """Searches Pexels API for a vertical video"""
        if not query: return None
        if not Config.PEXELS_API_KEY:
            print("⚠️ ASSET ERROR: Pexels API Key Missing")
            return None

        headers = {"Authorization": Config.PEXELS_API_KEY}
        params = {"query": query, "orientation": "portrait", "per_page": 3, "size": "medium"}
        
        try:
            r = requests.get(AssetEngine.PEXELS_BASE_URL, headers=headers, params=params, timeout=10)
            if r.status_code != 200: return None
            
            data = r.json()
            videos = data.get('videos', [])
            
            if videos:
                # Smart Selection: Pick best quality MP4 (not 4K, not tiny)
                best_video = videos[0]
                download_link = None
                
                for video in videos:
                    for file in video.get("video_files", []):
                        # Prefer MP4, Width 700-2000px (HD/FullHD)
                        if file.get("file_type") == "video/mp4" and 700 < file.get("width", 0) < 2000:
                            return file.get("link")
                
                # Fallback to first available link if no perfect match
                if videos[0].get("video_files"):
                    return videos[0]["video_files"][0].get("link")
                    
        except Exception as e:
            print(f"⚠️ Pexels Search Error ({query}): {e}")
            
        return None

    @staticmethod
    def _download_file(url, path):
        """Downloads a file from URL to Path"""
        try:
            with requests.get(url, stream=True, timeout=20) as r:
                r.raise_for_status()
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"❌ Download Failed: {e}")
            return False

    @staticmethod
    def generate_ai_image(prompt: str, filename: str = "thumbnail.jpg"):
        """
        Generates an AI Image using Pollinations (Free/Fast).
        Great for Thumbnails.
        """
        print(f"🎨 PAINTING: Generating AI Image for '{prompt}'...")
        
        # URL encode the prompt
        encoded_prompt = requests.utils.quote(prompt)
        # 16:9 Aspect Ratio (1280x720) using 'flux' model
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux"
        
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                output_path = os.path.join(Config.TEMP_DIR, filename)
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Image Saved: {output_path}")
                return output_path
            else:
                print("❌ Image Gen Failed.")
                return None
        except Exception as e:
            print(f"❌ Image Gen Error: {e}")
            return None