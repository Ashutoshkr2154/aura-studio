import os
import random
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, 
    ColorClip, ImageClip, concatenate_videoclips, vfx, CompositeAudioClip
)
from src.config import Config

class VideoEditor:
    
    @staticmethod
    def assemble_video(blueprint, assets):
        """
        AURA 4.6 PLATINUM EDITOR
        Features: Audio Ducking, Smart Logo Opacity, Render Safety, Cloud Fonts.
        """
        print("\n🎬 EDITOR: Initializing AURA 4.6 Render Pipeline...")
        
        # 1. Load Voiceover (The Master Clock)
        audio_path = assets.get('audio_path')
        if not os.path.exists(audio_path):
            print("❌ CRITICAL: Audio file missing. Cannot render.")
            return None
            
        voice_clip = AudioFileClip(audio_path)
        master_duration = voice_clip.duration + 0.5 
        print(f"⏱️ Target Duration: {master_duration:.2f}s")

        # 2. Prepare Visuals
        final_clips = []
        scenes = blueprint['scenes']
        video_paths = assets.get('video_paths', {})
        scene_duration = master_duration / len(scenes)

        for i, scene in enumerate(scenes):
            scene_id = scene['id']
            clip_path = video_paths.get(scene_id)
            
            # Clip Validation
            clip = None
            if clip_path and os.path.exists(clip_path):
                try:
                    clip = VideoFileClip(clip_path)
                    if clip.duration < 0.1 or clip.size[0] == 0: clip = None
                except: clip = None

            if clip is None:
                print(f"🚨 SCENE {scene_id} MISSING/CORRUPT! Generating Placeholder.")
                clip = ColorClip(size=(1080, 1920), color=(20, 20, 30), duration=scene_duration)

            # Resize & Crop (9:16)
            w, h = clip.size
            target_ratio = 1080 / 1920
            current_ratio = w / h
            
            if current_ratio > target_ratio:
                new_w = int(h * target_ratio)
                clip = clip.crop(x1=(w/2 - new_w/2), width=new_w, height=h)
            else:
                new_h = int(w / target_ratio)
                clip = clip.crop(y1=(h/2 - new_h/2), width=w, height=new_h)
                
            clip = clip.resize((1080, 1920))

            # Duration Lock
            if clip.duration < scene_duration:
                clip = vfx.loop(clip, duration=scene_duration)
            else:
                clip = clip.subclip(0, scene_duration)
                
            clip = clip.set_duration(scene_duration)
            final_clips.append(clip)

        # 3. Assemble Visual Track
        final_video_clip = concatenate_videoclips(final_clips, method="compose")
        final_video_clip = final_video_clip.set_duration(master_duration)

        # 4. Audio Mixing
        music_mood = assets.get('music_mood', 'Chill').lower()
        music_filename = f"{music_mood}.mp3"
        music_path = os.path.join(Config.MUSIC_DIR, music_filename)
        
        if not os.path.exists(music_path):
            fallback = os.path.join(Config.MUSIC_DIR, "upbeat.mp3")
            if os.path.exists(fallback): music_path = fallback

        if os.path.exists(music_path):
            print(f"🎵 Mixing Music: {os.path.basename(music_path)}")
            bg_music = AudioFileClip(music_path)
            if bg_music.duration < master_duration:
                bg_music = vfx.loop(bg_music, duration=master_duration)
            else:
                bg_music = bg_music.subclip(0, master_duration)
            bg_music = bg_music.volumex(0.12)
            final_audio = CompositeAudioClip([voice_clip, bg_music])
            final_video_clip = final_video_clip.set_audio(final_audio)
        else:
            final_video_clip = final_video_clip.set_audio(voice_clip)

        # 5. CAPTIONS
        print("📝 Generating Captions...")
        try:
            text_clips = []
            for i, scene in enumerate(scenes):
                txt = scene.get('overlay_text', '').upper()
                if txt:
                    # FORCE ARIAL on Cloud to avoid font path errors
                    font_to_use = "Arial"
                    
                    txt_clip = (TextClip(txt, fontsize=80, color='white', font=font_to_use, 
                                       stroke_color='black', stroke_width=4, method='caption', 
                                       size=(900, None), align='center')
                                .set_position(('center', 'center'))
                                .set_duration(scene_duration)
                                .set_start(i * scene_duration))
                    text_clips.append(txt_clip)
            
            if text_clips:
                final_video_clip = CompositeVideoClip([final_video_clip] + text_clips)
        except Exception as e:
            print(f"⚠️ Caption Error: {e}")

        # 6. Branding
        if assets.get('logo_path'):
            opacity = blueprint.get('branding', {}).get('logo_opacity', 0.8)
            logo = (ImageClip(assets['logo_path'])
                    .resize(height=150)
                    .set_opacity(opacity)
                    .set_position(("right", "top"))
                    .set_duration(master_duration)
                    .margin(right=20, top=20, opacity=0))
            final_video_clip = CompositeVideoClip([final_video_clip, logo])

        elif assets.get('watermark_text'):
            wm_txt = assets['watermark_text']
            wm = (TextClip(wm_txt, fontsize=30, color='white', font='Arial')
                  .set_opacity(0.6)
                  .set_position(('center', 0.92), relative=True)
                  .set_duration(master_duration))
            final_video_clip = CompositeVideoClip([final_video_clip, wm])

        # 7. Render
        output_path = os.path.join(Config.OUTPUT_DIR, f"AURA_{random.randint(1000,9999)}.mp4")
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        print("🚀 Rendering Final Export...")
        final_video_clip.write_videofile(
            output_path,
            fps=Config.FPS,
            codec='libx264',
            audio_codec='aac',
            preset='ultrafast',
            threads=4,
            logger=None
        )
        
        print("✅ RENDER COMPLETE.")
        return output_path