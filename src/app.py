import os
import sys

# ==========================================
# ☁️ CLOUD DEPLOYMENT FIX (CRITICAL)
# ==========================================
# This MUST be the very first thing that runs.
# It tells ImageMagick: "Look for policy.xml in THIS folder, not the system folder."
os.environ['MAGICK_CONFIGURE_PATH'] = os.getcwd()
# ==========================================

import PIL.Image
# ==========================================
# 🚑 HOTFIX: PILLOW 10.0.0 COMPATIBILITY
# ==========================================
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# ==========================================

import streamlit as st
import json
import time
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.modules.brain import Brain
from src.modules.voice import VoiceEngine
from src.modules.assets import AssetEngine
from src.modules.editor import VideoEditor
from src.modules.utils import clean_temp_folder

# --- CONFIGURATION ---
HISTORY_FILE = os.path.join(Config.DATA_DIR, "history.json")

# --- HELPER: PERSISTENT HISTORY MANAGER ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_to_history(entry):
    history = load_history()
    history.insert(0, entry)
    history = history[:10]
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)
    return history

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AURA 4.6 | Platinum Studio",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'page' not in st.session_state: st.session_state.page = "Generate"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"
if 'euri_key_session' not in st.session_state: st.session_state.euri_key_session = Config.EURIAI_API_KEY

# --- THEME ENGINE ---
def apply_theme():
    if st.session_state.theme == "Dark":
        st.markdown("""
            <style>
            .stApp { background-color: #0e1117; color: #e0e0e0; }
            section[data-testid="stSidebar"] { background-color: #161b22; }
            .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
                background-color: #1f2937; color: white; border: 1px solid #374151;
            }
            div[data-testid="stStatusWidget"] { background-color: #1f2937; border: 1px solid #374151; }
            div[data-testid="stExpander"] { background-color: #1f2937; border: 1px solid #374151; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .stApp { background-color: #f8f9fa; color: #212529; }
            section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #dee2e6; }
            .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
                background-color: #ffffff; color: #212529; border: 1px solid #ced4da;
            }
            div[data-testid="stStatusWidget"] { background-color: #ffffff; border: 1px solid #e9ecef; }
            div[data-testid="stExpander"] { background-color: #ffffff; border: 1px solid #e9ecef; }
            </style>
        """, unsafe_allow_html=True)
        
    st.markdown("""
        <style>
        div.stButton > button {
            background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
            border: none; color: white; font-weight: 700; text-transform: uppercase;
            padding: 0.8rem; border-radius: 8px; transition: all 0.3s;
        }
        div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(168, 85, 247, 0.4); }
        </style>
    """, unsafe_allow_html=True)

apply_theme()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("💎 AURA 4.6")
    st.caption("Director's Cut Edition")
    st.divider()
    
    selected_tab = st.radio("📍 Navigation", ["🚀 Generate", "📜 History", "⚙️ Settings", "📊 Dashboard"])
    
    st.divider()
    
    st.markdown("### 🎨 Appearance")
    theme_choice = st.radio("Theme Mode", ["Dark", "Light"], horizontal=True, index=0 if st.session_state.theme == "Dark" else 1)
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    st.divider()
    st.markdown("### 📡 System Health")
    c1, c2 = st.columns(2)
    with c1: 
        if Config.OPENAI_API_KEY: st.success("Brain: ON") 
        else: st.error("Brain: OFF")
    with c2:
        if st.session_state.euri_key_session: st.success("Euri: ON") 
        else: st.warning("Euri: OFF")

# --- PAGE 1: GENERATE (STUDIO) ---
if selected_tab == "🚀 Generate":
    st.title("🎬 Creative Studio")
    
    col_input, col_output = st.columns([1, 1.2], gap="large")
    
    with col_input:
        with st.container(border=True):
            st.subheader("1. Concept Strategy")
            topic = st.text_area("Video Topic", height=100, placeholder="e.g. 3 AI Tools better than ChatGPT (Show robots, coding, future city)")
            
            # --- NEW CONTROLS FOR AURA 4.6 ---
            c1, c2 = st.columns(2)
            with c1:
                structure = st.selectbox("🏗️ Structure", 
                    ["Viral Hook", "Educational", "Storytime", "Listicle", "Motivation"],
                    help="How the script is organized.")
                audience = st.selectbox("👥 Audience", 
                    ["General", "Students", "Professionals", "Kids", "Tech Enthusiasts"],
                    help="Who is watching?")
            with c2:
                style = st.selectbox("🎨 Visual Style", 
                    ["Fast Paced", "Cinematic", "Minimalist", "Documentary", "Vlog"],
                    help="The pacing and look of the video.")
                duration = st.select_slider("⏱️ Duration", ["30s", "45s", "60s"], value="60s")
            
            st.divider()
            
            c3, c4 = st.columns(2)
            with c3:
                language = st.selectbox("🌍 Language", ["English", "Hindi", "Spanish", "French", "German"])
            with c4:
                voice = st.selectbox("🎙️ Voice", ["Nova (Female)", "Alloy (Male)", "Echo (Deep)", "Hindi (Neural)"])

            st.divider()
            st.subheader("2. Vibe & Branding")
            music = st.selectbox("🎵 Music Mood", ["Chill", "Upbeat", "Dramatic", "Phonk", "Corporate"])
            
            branding_enabled = st.checkbox("Apply Watermark", value=True)
            watermark_text = ""
            logo_path = None
            
            if branding_enabled:
                watermark_text = st.text_input("Handle / Channel Name", "@YourChannel")
                logo_file = st.file_uploader("Upload Logo (PNG)", type=["png"])
                if logo_file:
                    logo_path = os.path.join(Config.TEMP_DIR, "logo.png")
                    with open(logo_path, "wb") as f:
                        f.write(logo_file.getbuffer())
            
            st.divider()
            generate_btn = st.button("🚀 LAUNCH PRODUCTION", use_container_width=True)

    with col_output:
        st.subheader("3. Live Monitor")
        
        if generate_btn and topic:
            status = st.status("💎 AURA Engine Initializing...", expanded=True)
            
            try:
                # PHASE 0: PREP
                clean_temp_folder(Config.TEMP_DIR)
                
                # PHASE 1: BRAIN (Updated for 4.6)
                status.write(f"🧠 **Brain:** Drafting '{structure}' script for {audience}...")
                brain = Brain(euri_key_override=st.session_state.euri_key_session)
                
                # Passing NEW parameters to Brain
                blueprint = brain.generate_video_blueprint(
                    topic=topic, 
                    language=language, 
                    structure=structure,
                    duration=duration,
                    audience=audience,
                    style=style
                )
                
                if not blueprint:
                    status.update(label="❌ Brain Failure", state="error")
                    st.stop()
                
                title = blueprint['upload_metadata']['title']
                status.write(f"✅ Strategy Locked: *{title}*")

                # PHASE 2: AUDIO
                status.write(f"🎙️ **Audio:** Synthesizing {language} neural voice...")
                script_text = blueprint['script']['full_voiceover']
                audio_path = os.path.join(Config.TEMP_DIR, "voice.mp3")
                
                target_voice = language if language != "English" else voice
                VoiceEngine.generate_audio(script_text, audio_path, voice_name=target_voice)
                status.write("✅ Audio Mastered")

                # PHASE 3: VISUALS
                scenes = blueprint['scenes']
                status.write(f"👁️ **Vision:** Scouting {len(scenes)} premium assets...")
                video_paths = AssetEngine.download_scene_assets(scenes)
                status.write(f"✅ Downloaded {len(video_paths)} Clips")

                # PHASE 4: EDITING
                status.write(f"🎬 **Editor:** Mixing tracks (Music: {music})...")
                
                # --- SAFETY CHECK: PREVENT CRASH IF LOGO MISSING ---
                safe_logo_path = None
                if logo_path and os.path.exists(logo_path):
                    safe_logo_path = logo_path
                
                assets = {
                    "audio_path": audio_path,
                    "video_paths": video_paths,
                    "music_mood": music,
                    "watermark_text": watermark_text,
                    "logo_path": safe_logo_path
                }
                
                final_video = VideoEditor.assemble_video(blueprint, assets)
                
                status.update(label="✅ Production Complete!", state="complete", expanded=False)
                
                st.balloons()
                st.success(f"**{title}**")
                st.video(final_video)
                
                with open(final_video, "rb") as f:
                    st.download_button("⬇️ Download Final Video", f, file_name=f"{title}.mp4", use_container_width=True)
                
                # CONTENT INTELLIGENCE
                with st.expander("📈 Viral Marketing & Thumbnails", expanded=True):
                    m_data = blueprint.get('marketing', {})
                    mc1, mc2 = st.columns(2)
                    
                    with mc1:
                        st.markdown("**🔥 Viral Titles:**")
                        for t in m_data.get('ctr_titles', []): st.info(f"• {t}")
                        st.markdown("**🏷️ SEO Tags:**")
                        st.code(", ".join(m_data.get('seo_tags', [])), language="text")
                        st.markdown("**📝 Description:**")
                        st.text_area("Copy:", m_data.get('seo_description', "N/A"), height=100)

                    with mc2:
                        st.markdown("**🎨 AI Thumbnail Generator**")
                        thumb_ideas = m_data.get('thumbnail_ideas', ["Futuristic Concept"])
                        selected_idea = st.selectbox("Choose Concept:", thumb_ideas)
                        
                        if st.button("✨ GENERATE THUMBNAIL"):
                            with st.spinner("🎨 AI is painting..."):
                                thumb_path = AssetEngine.generate_ai_image(selected_idea, "thumbnail_final.jpg")
                                if thumb_path:
                                    st.image(thumb_path)
                                    with open(thumb_path, "rb") as file:
                                        st.download_button("⬇️ Download JPG", file, file_name="thumbnail.jpg", mime="image/jpeg")
                                else:
                                    st.error("Thumbnail generation failed.")

                # SAVE HISTORY
                entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "topic": topic,
                    "title": title,
                    "path": final_video,
                    "language": language,
                    "marketing": blueprint.get('marketing', {})
                }
                save_to_history(entry)

            except Exception as e:
                status.update(label="❌ Critical System Error", state="error")
                st.error(f"Error Log: {e}")

        else:
            st.info("👈 System Standby. Enter a topic to begin.")
            st.markdown("""
                <div style="padding: 20px; border-radius: 10px; border: 1px dashed #6c757d; text-align: center;">
                    <h3 style="margin:0; opacity: 0.7;">Waiting for Input...</h3>
                </div>
            """, unsafe_allow_html=True)

# --- PAGE 2: HISTORY ---
elif selected_tab == "📜 History":
    st.title("📚 Content Archives")
    st.markdown("Your locally generated videos.")
    
    history_data = load_history()
    
    if not history_data:
        st.warning("No history found.")
    else:
        for item in history_data:
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                with c1:
                    if os.path.exists(item['path']):
                        st.video(item['path'])
                    else:
                        st.error("⚠️ Video file gone (Session Reset)")
                with c2:
                    st.subheader(item.get('title', 'Untitled'))
                    st.caption(f"📅 {item['timestamp']} | 🌍 {item['language']}")
                    
                    with st.expander("📈 View Saved SEO & Marketing"):
                        m = item.get('marketing', {})
                        st.markdown("**Viral Title:** " + (m.get('ctr_titles', ['N/A'])[0] if m.get('ctr_titles') else 'N/A'))
                        st.markdown("**Tags:**")
                        st.code(", ".join(m.get('seo_tags', [])), language="text")
                        st.markdown("**Description:**")
                        st.caption(m.get('seo_description', "No description saved."))

                    if os.path.exists(item['path']):
                         with open(item['path'], "rb") as f:
                            st.download_button("⬇️ Re-Download", f, file_name=f"{item['title']}.mp4", key=item['timestamp'])

# --- PAGE 3: SETTINGS ---
elif selected_tab == "⚙️ Settings":
    st.title("⚙️ Engine Configuration")
    
    with st.container(border=True):
        st.subheader("🔑 API Vault")
        
        st.info("💡 Note: Euri Key updates here apply to the current session only.")
        
        new_euri_key = st.text_input("Euri AI API Key (Override)", 
                                     value=st.session_state.euri_key_session if st.session_state.euri_key_session else "", 
                                     type="password",
                                     placeholder="sk-euri-...")
        
        if new_euri_key != st.session_state.euri_key_session:
            st.session_state.euri_key_session = new_euri_key
            st.success("✅ Euri Key Updated for this session!")

        st.divider()
        st.text_input("OpenAI Key (Loaded from Secrets)", value=Config.OPENAI_API_KEY, disabled=True, type="password")
        st.text_input("Pexels Key (Loaded from Secrets)", value=Config.PEXELS_API_KEY, disabled=True, type="password")
        
    with st.container(border=True):
        st.subheader("🧹 Maintenance")
        if st.button("Clear Temporary Files"):
            clean_temp_folder(Config.TEMP_DIR)
            st.success("Temp folder cleaned.")

# --- PAGE 4: DASHBOARD ---
elif selected_tab == "📊 Dashboard":
    st.title("📊 Mission Control")
    history_data = load_history()
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Videos", len(history_data))
    with c2: st.metric("Languages Used", len(set(h['language'] for h in history_data)) if history_data else 0)
    with c3: st.metric("Storage Used", "1.4 GB" if history_data else "0 MB")
    
    st.markdown("### 📅 Recent Activity")
    if history_data:
        df = pd.DataFrame(history_data)[["timestamp", "title", "language"]]
        st.dataframe(df, use_container_width=True, hide_index=True)