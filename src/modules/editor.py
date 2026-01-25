# ==========================================================
# 🚑 SETUP & PATCHES
# ==========================================================
import os
import sys
from src.config import Config
import numpy as np
if not hasattr(np, 'product'): np.product = np.prod
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'): PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# ==========================================================

import random
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ColorClip, CompositeAudioClip, ImageClip, TextClip, afx, concatenate_videoclips
from src.modules.subtitles import SubtitleEngine

class VideoEditor:
    
    @staticmethod
    def assemble_video(blueprint, assets):
        # Extract Mood from assets (passed from UI)
        mood = assets.get('music_mood', 'chill').lower()
        voice_model = assets.get('voice_model', 'Nova (Female)') # For logging
        
        print(f"\n🎬 EDITOR: Assembling (Mood: {mood} | Voice: {voice_model})...")
        
        # --- 1. Audio & Music ---
        if not os.path.exists(assets['audio_path']):
            print("❌ EDITOR ERROR: Audio file missing!")
            return None
            
        voice_audio = AudioFileClip(assets['audio_path'])
        duration = voice_audio.duration
        
        # --- 🎵 DYNAMIC MUSIC ENGINE (JUKEBOX) ---
        # Map UI selection to actual filenames
        music_map = {
            "chill": "chill.mp3",
            "upbeat": "upbeat.mp3",
            "dramatic": "dramatic.mp3",
            "phonk": "phonk.mp3",
            "corporate": "corporate.mp3"
        }
        
        # 1. Get filename based on mood (default to chill)
        filename = music_map.get(mood.split()[0].lower(), "chill.mp3") 
        music_path = os.path.join(Config.MUSIC_DIR, filename)
        bg_music = None

        if os.path.exists(music_path):
            print(f"🎵 Jukebox: Playing '{filename}'...")
            try:
                bg_music = AudioFileClip(music_path)
                
                # Loop if song is shorter than video
                if bg_music.duration < duration:
                    bg_music = afx.audio_loop(bg_music, duration=duration)
                else:
                    bg_music = bg_music.subclip(0, duration)
                
                # Volume Ducking (Lower volume so voice is clear)
                bg_music = bg_music.volumex(0.12) 
            except Exception as e:
                print(f"⚠️ Music Error: {e}")
        else:
            print(f"⚠️ Music file not found: {music_path} (Using Silence)")

        # --- 2. Visual Stitching ---
        video_files = assets.get('video_paths', [])
        clips = []
        
        if not video_files:
            print("⚠️ No video files found. Using Black Screen.")
            clips.append(ColorClip(size=(1080, 1920), color=(0,0,0), duration=duration))
        else:
            # Calculate how long each clip should be
            clip_duration = duration / len(video_files)
            
            print(f"✂️ Stitching {len(video_files)} clips ({clip_duration:.1f}s each)...")
            
            for vid_path in video_files:
                try:
                    clip = VideoFileClip(vid_path)
                    
                    # Force Vertical 9:16 Crop
                    if clip.h < 1920: 
                        clip = clip.resize(height=1920)
                    clip = clip.crop(x1=clip.w/2 - 540, width=1080, height=1920)
                    
                    # Trim/Loop to exact segment length
                    if clip.duration < clip_duration:
                        clip = clip.loop(duration=clip_duration)
                    else:
                        clip = clip.subclip(0, clip_duration)
                    
                    clips.append(clip)
                except Exception as e:
                    print(f"⚠️ Bad Clip {vid_path}: {e}")

        # Stitch them together
        if clips:
            try:
                final_visual = concatenate_videoclips(clips, method="compose")
                # Safety: Ensure exact match to audio duration
                if final_visual.duration > duration:
                     final_visual = final_visual.subclip(0, duration)
            except Exception as e:
                print(f"❌ Stitching Failed: {e}")
                final_visual = ColorClip(size=(1080, 1920), color=(0,0,0), duration=duration)
        else:
            final_visual = ColorClip(size=(1080, 1920), color=(0,0,0), duration=duration)

        # --- 3. Subtitles ---
        full_script = blueprint.get('script', {}).get('full_voiceover', "")
        subtitle_clips = []
        if full_script:
            try:
                subtitle_clips = SubtitleEngine.generate_subtitle_clips(full_script, duration, 1080)
            except: pass
            
        # --- 4. WATERMARK / BRANDING ---
        overlays = subtitle_clips
        
        # Text Watermark (e.g., @MyChannel)
        if assets.get('watermark_text'):
            try:
                print(f"💧 Adding Text Watermark: {assets['watermark_text']}")
                wm_txt = TextClip(
                    assets['watermark_text'], 
                    fontsize=30, 
                    color='white', 
                    font='Arial-Bold', 
                    method='caption',
                    align='East',
                    size=(1080, None)
                )
                # Positioned at bottom center, slightly transparent
                wm_txt = wm_txt.set_position(('center', 1750)).set_duration(duration).set_opacity(0.6)
                overlays.append(wm_txt)
            except Exception as e:
                print(f"⚠️ Watermark Text Error: {e}")

        # Image Logo
        if assets.get('logo_path') and os.path.exists(assets['logo_path']):
            try:
                print("🖼️ Adding Logo Overlay...")
                logo = ImageClip(assets['logo_path'])
                logo = logo.resize(height=150) # Resize to safe size
                
                # FIXED: Use .margin() instead of .set_margin()
                # Positioned top-right with padding
                logo = logo.margin(top=50, right=50, opacity=0).set_position(("right", "top")).set_duration(duration).set_opacity(0.8)
                
                overlays.append(logo)
            except Exception as e:
                print(f"⚠️ Logo Error: {e}")

        # --- 5. Render ---
        try:
            # Combine [Video + Subtitles + Overlays]
            final_video = CompositeVideoClip([final_visual] + overlays)
            
            # Mix Audio [Voice + Music]
            if bg_music:
                final_video = final_video.set_audio(CompositeAudioClip([voice_audio, bg_music]))
            else:
                final_video = final_video.set_audio(voice_audio)
            
            output_path = os.path.join(Config.OUTPUT_DIR, f"AURA_{random.randint(1000,9999)}.mp4")
            print(f"⚡ Rendering Multi-Scene Video to {output_path}...")
            
            final_video.write_videofile(
                output_path, 
                fps=30, 
                codec='libx264', 
                audio_codec='aac', 
                threads=4, 
                preset='ultrafast', 
                logger=None
            )
            print("✅ RENDER COMPLETE.")
            return output_path
            
        except Exception as e:
            print(f"❌ RENDER ERROR: {e}")
            return None