import streamlit as st
import os
import sys
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

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AURA Platinum | AI Studio",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME ENGINE (PLATINUM LIGHT) ---
st.markdown("""
    <style>
    /* Platinum Light Theme */
    .stApp { 
        background-color: #f8f9fa; 
        color: #212529; 
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { 
        background-color: #ffffff; 
        border-right: 1px solid #dee2e6; 
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #ffffff; 
        border: 1px solid #ced4da; 
        color: #212529; 
        border-radius: 8px;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 0.2rem rgba(99, 102, 241, 0.25);
    }
    
    /* Primary Action Button */
    div.stButton > button {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        border: none;
        color: white;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 0.8rem;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    div.stButton > button:hover {
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    div[data-testid="stMetric"] label { color: #6c757d; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #212529; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #e9ecef;
        border-radius: 5px;
        color: #495057;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #4f46e5;
        border: 1px solid #4f46e5;
        font-weight: 600;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        color: #212529;
    }
    </style>
""", unsafe_allow_html=True)

if 'history' not in st.session_state: st.session_state.history = []
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

def navigate_to(page): st.session_state.page = page

# --- SIDEBAR ---
with st.sidebar:
    st.title("💎 AURA PLATINUM")
    st.caption("v4.3 | Content Strategy Engine")
    st.divider()
    
    if st.button("📊 Dashboard", use_container_width=True): navigate_to("Dashboard")
    if st.button("🎬 Creative Studio", use_container_width=True): navigate_to("Studio")
    if st.button("🔑 Neural Vault", use_container_width=True): navigate_to("Settings")
    if st.button("📜 Archives", use_container_width=True): navigate_to("History")
    
    st.divider()
    st.markdown("### 📡 System Status")
    c1, c2 = st.columns(2)
    with c1: 
        st.markdown("**OpenAI**")
        if Config.OPENAI_API_KEY: st.success("Online") 
        else: st.error("Offline")
    with c2:
        st.markdown("**Euri AI**")
        if Config.EURIAI_API_KEY: st.success("Online") 
        else: st.warning("Standby")

# --- DASHBOARD PAGE ---
def page_dashboard():
    st.title("📊 Mission Control")
    st.markdown("Global overview of your content empire.")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Videos Created", len(st.session_state.history), "+3 Today")
    with c2: st.metric("Avg. Engagement", "High", "Viral Potential")
    with c3: st.metric("SEO Score", "98/100", "Optimized")
    with c4: st.metric("Storage", "1.4 GB", "Local")
    
    st.markdown("### 🚀 Quick Actions")
    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("✨ New Project", use_container_width=True): navigate_to("Studio")
    
    st.markdown("### 📅 Recent Productions")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)[["Date", "Topic", "Language", "Status"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("System initialized. Ready for first launch.")

# --- STUDIO PAGE (THE CORE) ---
def page_studio():
    st.title("🎬 Creative Studio")
    
    # Layout: Input Left, Output Right
    col_input, col_output = st.columns([1, 1.3], gap="large")
    
    with col_input:
        st.markdown("### 1. Strategy & Concept")
        with st.container(border=True):
            topic = st.text_area("Video Topic", height=100, placeholder="e.g. The Future of Quantum Computing...")
            
            c1, c2 = st.columns(2)
            with c1:
                language = st.selectbox("🌍 Language", ["English", "Hindi", "Spanish", "French", "German"])
                voice = st.selectbox("🎙️ Voice Model", ["Nova (Female)", "Alloy (Male)", "Echo (Deep)"])
            with c2:
                duration = st.select_slider("⏱️ Duration", ["30s", "45s", "60s"], value="45s")
                music = st.selectbox("🎵 Music Vibe", ["Chill", "Upbeat", "Dramatic", "Phonk", "Corporate"])
            
            # --- BRANDING SECTION (NEW) ---
            with st.expander("🎨 Branding & Watermark"):
                watermark_text = st.text_input("Channel Name (Watermark)", placeholder="@AuraAI")
                logo_file = st.file_uploader("Upload Logo (PNG)", type=["png"])

            st.divider()
            generate_btn = st.button("🚀 LAUNCH PRODUCTION", use_container_width=True)

    with col_output:
        st.markdown("### 2. Live Output Monitor")
        
        if generate_btn and topic:
            # TABS for Output
            tab_video, tab_marketing, tab_logs = st.tabs(["📺 Video Preview", "📈 Content Intelligence", "⚙️ System Logs"])
            
            # --- EXECUTION LOGIC ---
            with tab_logs:
                log_container = st.empty()
                progress_bar = st.progress(0)
                
                def log(msg, step=None):
                    log_container.code(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
                    if step: progress_bar.progress(step)

                try:
                    # PHASE 0
                    log("Initializing AURA 4.3...", 5)
                    clean_temp_folder(Config.TEMP_DIR)
                    
                    # Save Logo if uploaded
                    logo_path = None
                    if logo_file:
                        logo_path = os.path.join(Config.TEMP_DIR, "logo.png")
                        with open(logo_path, "wb") as f:
                            f.write(logo_file.getbuffer())
                    
                    # PHASE 1: BRAIN
                    log(f"🧠 BRAIN: Analyzing topic in {language}...", 15)
                    brain = Brain()
                    # PASS LANGUAGE TO BRAIN
                    blueprint = brain.generate_video_blueprint(topic, language=language)
                    
                    if not blueprint:
                        st.error("Brain Failure.")
                        st.stop()
                    
                    # Extract Data
                    script = blueprint.get('script', {}).get('full_voiceover')
                    scenes = blueprint.get('scenes', [])
                    marketing_data = blueprint.get('marketing', {})
                    title = blueprint.get('upload_metadata', {}).get('title', 'Untitled')
                    
                    log(f"✅ Script Generated ({len(script.split())} words)", 30)

                    # PHASE 2: ASSETS
                    # Determine voice logic
                    if language != "English":
                        target_voice = language # e.g. "Hindi"
                    else:
                        target_voice = voice # e.g. "Nova"

                    log(f"🎙️ AUDIO: Synthesizing with {target_voice}...", 45)
                    audio_path = os.path.join(Config.TEMP_DIR, "voice_main.mp3")
                    VoiceEngine.generate_audio(script, audio_path, voice_name=target_voice)
                    
                    log(f"👁️ VISION: Scouting {len(scenes)} scenes...", 60)
                    video_paths = AssetEngine.download_scene_assets(scenes)
                    
                    # PHASE 3: EDITING
                    log(f"🎬 EDITOR: Assembling with Watermark...", 80)
                    
                    # --- CONNECTING EVERYTHING ---
                    assets = {
                        "audio_path": audio_path, 
                        "video_paths": video_paths,
                        "music_mood": music,
                        "voice_model": target_voice,
                        "watermark_text": watermark_text,
                        "logo_path": logo_path
                    }
                    
                    final_path = VideoEditor.assemble_video(blueprint, assets)
                    
                    if final_path:
                        log("✅ RENDER COMPLETE.", 100)
                        st.balloons()
                        
                        # --- 1. VIDEO TAB ---
                        with tab_video:
                            st.success(f"**{title}**")
                            st.video(final_path)
                            with open(final_path, 'rb') as f:
                                st.download_button("⬇️ Download Video", f, file_name=f"{title}.mp4")

                        # --- 2. MARKETING TAB ---
                        with tab_marketing:
                            st.subheader("🚀 Viral Strategy & Assets")
                            
                            m_c1, m_c2 = st.columns(2)
                            
                            with m_c1:
                                st.markdown("**🔥 Viral Title Options**")
                                for t in marketing_data.get('ctr_titles', ["N/A"]):
                                    st.info(f"• {t}")
                                    
                                st.markdown("**🏷️ SEO Tags**")
                                tags = marketing_data.get('seo_tags', [])
                                st.code(", ".join(tags) if tags else "N/A", language="text")
                                
                                st.markdown("**📝 Description**")
                                st.text_area("Copy:", marketing_data.get('seo_description', "N/A"), height=100)

                            with m_c2:
                                st.markdown("**🎨 AI Thumbnail Generator**")
                                
                                # Get ideas from Brain
                                thumb_ideas = marketing_data.get('thumbnail_ideas', ["Futuristic AI Robot"])
                                selected_idea = st.selectbox("Choose Concept:", thumb_ideas)
                                
                                if st.button("✨ GENERATE THUMBNAIL"):
                                    with st.spinner("🎨 AI is painting your thumbnail (Flux Model)..."):
                                        thumb_path = AssetEngine.generate_ai_image(selected_idea, "thumbnail_final.jpg")
                                        if thumb_path:
                                            st.image(thumb_path, caption="AI Generated Thumbnail (1280x720)")
                                            with open(thumb_path, "rb") as file:
                                                st.download_button(
                                                    label="⬇️ Download Thumbnail",
                                                    data=file,
                                                    file_name="thumbnail.jpg",
                                                    mime="image/jpeg"
                                                )
                                        else:
                                            st.error("Thumbnail generation failed.")

                        # Save History
                        st.session_state.history.append({
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Topic": topic,
                            "Language": language,
                            "Status": "✅ Success",
                            "Path": final_path
                        })
                    else:
                        st.error("Render Failed.")
                        
                except Exception as e:
                    st.error(f"Critical Error: {e}")

        else:
            with col_output:
                st.info("👈 Waiting for Strategy Input...")
                st.image("https://images.unsplash.com/photo-1614064641938-3bbee52942c7?q=80&w=2670&auto=format&fit=crop", caption="AURA System Standby")

# --- SETTINGS PAGE ---
def page_settings():
    st.title("🔑 Neural Vault")
    with st.container(border=True):
        st.subheader("API Keys (Loaded from .env)")
        st.text_input("OpenAI Key", value=Config.OPENAI_API_KEY or "", type="password", disabled=True)
        st.text_input("Euri AI Key", value=Config.EURIAI_API_KEY or "", type="password", disabled=True)
        st.text_input("Pexels Key", value=Config.PEXELS_API_KEY or "", type="password", disabled=True)

# --- HISTORY PAGE ---
def page_history():
    st.title("📜 Archives")
    if not st.session_state.history:
        st.info("No records found.")
        return
    
    for job in reversed(st.session_state.history):
        with st.expander(f"{job['Date']} | {job['Topic']} ({job['Language']})"):
            st.video(job['Path'])

# --- MAIN ROUTER ---
def main():
    if st.session_state.page == "Dashboard": page_dashboard()
    elif st.session_state.page == "Studio": page_studio()
    elif st.session_state.page == "Settings": page_settings()
    elif st.session_state.page == "History": page_history()

if __name__ == "__main__":
    main()