import os
import requests
import random
from src.config import Config

class AssetEngine:
    @staticmethod
    def download_scene_assets(scenes):
        """
        Downloads videos for each scene using a Smart Fallback Strategy.
        Returns a Dictionary: { scene_id: "path/to/video.mp4" }
        """
        video_paths = {}
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
        
        headers = {"Authorization": Config.PEXELS_API_KEY}

        print(f"\n📦 ASSET ENGINE: Fetching {len(scenes)} unique clips...")

        for scene in scenes:
            scene_id = scene['id']
            # Smart Strategy: Try Main Query -> Then Fallbacks -> Then 'Abstract'
            queries = [scene['visual']['query']] + scene.get('visual_fallbacks', [])
            
            downloaded = False
            for query in queries:
                if downloaded: break
                
                print(f"👁️ Scouting Scene {scene_id}: '{query}'...")
                
                # Search Pexels
                url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation=portrait&size=medium"
                try:
                    res = requests.get(url, headers=headers)
                    if res.status_code != 200: continue

                    data = res.json()
                    
                    if data.get('videos'):
                        # Pick a random video from top 3 to keep it fresh
                        video = random.choice(data['videos'][:3])
                        video_files = video.get('video_files', [])
                        
                        # Find best quality (HD 720p/1080p to save RAM, avoid 4K)
                        best_link = None
                        for f in video_files:
                            if f['height'] >= 720 and f['height'] <= 1080:
                                best_link = f['link']
                                break
                        
                        # Fallback to any quality if HD not found
                        if not best_link and video_files: 
                            best_link = video_files[0]['link']

                        if best_link:
                            # Download
                            path = os.path.join(Config.TEMP_DIR, f"scene_{scene_id}.mp4")
                            with open(path, 'wb') as f:
                                f.write(requests.get(best_link).content)
                            
                            # Store in Dictionary mapping Scene ID -> File Path
                            video_paths[scene_id] = path
                            downloaded = True
                            print(f"✅ Acquired: {query}")
                except Exception as e:
                    print(f"⚠️ Search Error for '{query}': {e}")

            # Ultimate Fallback if everything failed
            if not downloaded:
                print(f"⚠️ Failed to find asset for Scene {scene_id}.")

        return video_paths

    @staticmethod
    def generate_ai_image(prompt, filename):
        """
        Generates a thumbnail using Pollinations (Free & Fast).
        """
        print(f"🎨 Generating Thumbnail: {prompt}")
        
        # Optimize prompt for YouTube
        full_prompt = f"{prompt}, youtube thumbnail, high contrast, 4k, cinematic lighting, text-free"
        encoded_prompt = requests.utils.quote(full_prompt)
        
        # Use Flux model via Pollinations
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                save_path = os.path.join(Config.TEMP_DIR, filename)
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                print("✅ Thumbnail Saved")
                return save_path
            else:
                print(f"❌ Thumbnail Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Image Gen Exception: {e}")
        
        return None