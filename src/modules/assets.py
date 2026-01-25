import requests
import os
import random
from src.config import Config

class AssetEngine:
    PEXELS_BASE_URL = "https://api.pexels.com/videos/search"
    
    @staticmethod
    def search_and_download_video(query: str, filename: str):
        """Downloads a SINGLE video from Pexels."""
        if not Config.PEXELS_API_KEY:
            print("❌ ASSET ERROR: Pexels API Key is missing.")
            return None
            
        headers = {"Authorization": Config.PEXELS_API_KEY}
        params = {"query": query, "orientation": "portrait", "per_page": 5, "size": "medium"}
        
        print(f"🔍 Searching Pexels for: '{query}'...")
        
        try:
            response = requests.get(AssetEngine.PEXELS_BASE_URL, headers=headers, params=params)
            if response.status_code != 200:
                return None
                
            data = response.json()
            videos = data.get("videos", [])
            
            if not videos:
                print(f"⚠️ No videos found for '{query}'.")
                return None
            
            # Smart Selection: Pick the best MP4 that isn't too huge
            best_video = videos[0] # Default to first
            download_link = None
            
            for video in videos:
                for file in video.get("video_files", []):
                    # We prefer HD (around 720p/1080p) but not 4K (too slow)
                    if file.get("file_type") == "video/mp4" and 700 < file.get("width", 0) < 2000:
                        download_link = file.get("link")
                        break
                if download_link: break
            
            if not download_link: return None
            
            # Download
            output_path = os.path.join(Config.TEMP_DIR, filename)
            with open(output_path, "wb") as f:
                f.write(requests.get(download_link).content)
            
            # print(f"⬇️ Acquired Asset: {filename}") # Optional: Uncomment for debug
            return output_path

        except Exception as e:
            print(f"❌ Asset Error: {e}")
            return None

    @staticmethod
    def download_scene_assets(scenes):
        """
        Input: List of scene dictionaries from the Brain.
        Output: List of valid file paths.
        """
        video_paths = []
        print(f"\n📦 ASSET ENGINE: Fetching {len(scenes)} unique clips...")
        
        for i, scene in enumerate(scenes):
            query = scene.get("visual", {}).get("query", "abstract background")
            filename = f"scene_{i}.mp4"
            
            path = AssetEngine.search_and_download_video(query, filename)
            if path:
                video_paths.append(path)
            else:
                # If search fails, try a fallback generic term
                print(f"⚠️ Search failed for '{query}'. Trying fallback.")
                path = AssetEngine.search_and_download_video("abstract technology", filename)
                if path: video_paths.append(path)
                
        return video_paths

    @staticmethod
    def generate_ai_image(prompt: str, filename: str = "thumbnail.jpg"):
        """
        Generates an AI Image using Pollinations (Free/Fast).
        Great for Thumbnails.
        """
        print(f"🎨 PAINTING: Generating AI Image for '{prompt}'...")
        
        # URL encode the prompt
        encoded_prompt = requests.utils.quote(prompt)
        # We request a 16:9 aspect ratio image (1280x720) using the 'flux' model for high quality
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux"
        
        try:
            response = requests.get(url)
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