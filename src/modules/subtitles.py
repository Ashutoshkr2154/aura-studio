from moviepy.editor import TextClip
from src.config import Config

class SubtitleEngine:
    """
    Generates 'Burned-in' captions for high retention.
    """
    
    @staticmethod
    def generate_subtitle_clips(full_text, total_duration, video_width):
        """
        Splits text into chunks and maps them to time segments.
        """
        # 1. Chunk the text (Max 5-6 words per chunk for readability)
        words = full_text.split()
        chunks = []
        chunk_size = 5
        
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i + chunk_size]))
            
        # 2. Calculate timing
        total_chars = len(full_text)
        clips = []
        current_time = 0
        
        print(f"📝 Subtitle Engine: Generating {len(chunks)} text chunks...")

        for chunk in chunks:
            # Proportional duration logic
            chunk_duration = (len(chunk) / total_chars) * total_duration
            
            # Create the TextClip
            # We use 'method="caption"' to allow auto-wrapping
            try:
                txt_clip = TextClip(
                    chunk.upper(),
                    fontsize=Config.FONT_SIZE, 
                    font=Config.FONT_NAME, 
                    color=Config.FONT_COLOR, 
                    stroke_color=Config.STROKE_COLOR, 
                    stroke_width=Config.STROKE_WIDTH,
                    size=(video_width * 0.8, None), # Wrap at 80% width
                    method='caption'
                ).set_start(current_time).set_duration(chunk_duration).set_position(('center', 'center'))
                
                clips.append(txt_clip)
                current_time += chunk_duration
            except Exception as e:
                print(f"⚠️ TextClip Error (ImageMagick issue?): {e}")
                # Continue without this subtitle if it fails
                continue
            
        return clips