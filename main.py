import streamlit as st
import os
import subprocess
import glob
import yt_dlp

# ======== Folders ========
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ======== CSS Styling ========
def local_css():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: white;
            font-family: 'Poppins', sans-serif;
        }
        @keyframes gradientShift {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(270deg, #60a5fa, #a78bfa, #f472b6, #60a5fa);
            background-size: 800% 800%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientShift 8s ease infinite;
            text-align: center;
            margin-bottom: 0;
        }
        .hero-subtitle {
            text-align: center;
            font-size: 1.1rem;
            opacity: 0.8;
            margin-bottom: 2rem;
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 30px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.2s ease-in-out;
        }
        .glass-card:hover {
            transform: scale(1.01);
        }
        .reel-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 15px;
            text-align: center;
            transition: transform 0.2s ease-in-out;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        .reel-card:hover {
            transform: scale(1.03);
            background-color: rgba(255, 255, 255, 0.1);
        }
        video { border-radius: 12px; }
        .stButton>button {
            background: linear-gradient(45deg, #2563eb, #3b82f6);
            color: white;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        .stButton>button:hover {
            background: linear-gradient(45deg, #1d4ed8, #2563eb);
            box-shadow: 0 0 10px #3b82f6, 0 0 20px #60a5fa;
            transform: translateY(-3px);
        }
        [data-testid="stFileUploader"] {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 10px;
        }
        @keyframes pulse {
          0%, 100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.7); }
          50% { box-shadow: 0 0 15px 5px rgba(37, 99, 235, 0.5); }
        }
        .pulse-button > button {
            animation: pulse 2.5s infinite;
        }
        .login-container {
            max-width: 400px;
            margin: 80px auto 40px auto;
            padding: 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        }
        .stTextInput > div > input {
            background-color: rgba(255,255,255,0.1) !important;
            color: white !important;
        }
        .logout-button {
            background: linear-gradient(45deg, #ef4444, #f87171);
            color: white;
            border-radius: 8px;
            padding: 6px 18px;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            white-space: nowrap;
            width: auto;
            text-align: center;
        }
        .logout-button:hover {
            background: linear-gradient(45deg, #b91c1c, #ef4444);
            box-shadow: 0 0 10px #ef4444, 0 0 20px #f87171;
            transform: translateY(-2px);
        }
        </style>
        """, unsafe_allow_html=True
    )

# ======== Video & Audio Functions ========
def save_uploaded_file(uploaded_file):
    filepath = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filepath

def run_ffmpeg_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        st.error(f"FFmpeg error:\n{result.stderr}")
        return False
    return True

def extract_audio(video_path):
    audio_path = os.path.join(OUTPUT_DIR, "audio.wav")
    command = f'ffmpeg -i "{video_path}" -q:a 0 -map a "{audio_path}" -y'
    if run_ffmpeg_command(command) and os.path.exists(audio_path):
        return audio_path
    return None

def resize_video_reel_format(video_path):
    resized_path = os.path.join(OUTPUT_DIR, "resized.mp4")
    command = f'ffmpeg -i "{video_path}" -vf "scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" "{resized_path}" -y'
    if run_ffmpeg_command(command) and os.path.exists(resized_path):
        return resized_path
    return None

def chunk_video(video_path):
    chunk_pattern = os.path.join(OUTPUT_DIR, "chunk%03d.mp4")
    command = f'ffmpeg -i "{video_path}" -c copy -map 0 -segment_time 300 -f segment "{chunk_pattern}" -y'
    if run_ffmpeg_command(command):
        return OUTPUT_DIR
    return None

def show_reels():
    reels = glob.glob(f"{OUTPUT_DIR}/*.mp4")
    if not reels:
        st.warning("No reels found yet.")
        return
    cols = st.columns(3)
    for idx, reel in enumerate(reels):
        with cols[idx % 3]:
            st.markdown(f"<div class='reel-card'><h4>🎬 Reel {idx+1}</h4>", unsafe_allow_html=True)
            st.video(reel)
            with open(reel, "rb") as f:
                st.download_button("⬇ Download", f, file_name=f"Reel_{idx+1}.mp4")
            st.markdown("</div>", unsafe_allow_html=True)

def get_reels_summary():
    reels = glob.glob(f"{OUTPUT_DIR}/*.mp4")
    total_size = sum([os.path.getsize(r) for r in reels])/(1024*1024)
    return len(reels), total_size

# ======== YouTube Download ========
def download_youtube_video(url, output_folder=UPLOAD_DIR):
    opts = {
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'format': 'mp4',
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            if info:
                return ydl.prepare_filename(info)
        except Exception as e:
            st.error(f"Download failed: {e}")
    return None

# ======== Login / Logout ========
def login():
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h2>Login to AI Reel Creator</h2>", unsafe_allow_html=True)
    user = st.text_input("Username", key="input_username")
    pwd = st.text_input("Password", type="password", key="input_password")
    if st.button("Login"):
        if user and pwd:
            st.session_state["logged_in"] = True
            st.session_state["user"] = user
        else:
            st.warning("Please enter both username and password.")
    st.markdown("</div>", unsafe_allow_html=True)

def logout():
    st.session_state.clear()

# ======== Main App ========
def main_app():
    local_css()
    st.markdown("<h1 class='hero-title'>🎥 AI Reel Creator</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='hero-subtitle'>Welcome, {st.session_state.get('user','')}!</p>", unsafe_allow_html=True)

    cols = st.columns([9,1])
    with cols[1]:
        if st.button("Exit", key="logout_btn", use_container_width=False):
            logout()
            st.rerun()  # ✅ Updated from st.experimental_rerun()

    uploaded_file = st.file_uploader("📤 Upload your video", type=["mp4","mov","avi","mkv"])
    youtube_url = st.text_input("Or enter a YouTube video URL:")

    # Handle uploads
    if uploaded_file:
        st.session_state["video_path"] = save_uploaded_file(uploaded_file)
        st.success(f"✅ Video uploaded: {st.session_state['video_path']}")

    if youtube_url and st.button("Download from YouTube"):
        with st.spinner("Downloading..."):
            path = download_youtube_video(youtube_url.strip())
        if path:
            st.session_state["video_path"] = path
            st.success(f"✅ Downloaded: {path}")

    # If we have a video, show tools
    if st.session_state.get("video_path"):
        video_path = st.session_state["video_path"]
        tab1, tab2 = st.tabs(["🔧 Tools", "📂 Generated Reels"])
        with tab1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🎵 Extract Audio"):
                    audio_path = extract_audio(video_path)
                    if audio_path: st.audio(audio_path)
            with c2:
                if st.button("📱 Convert to Reel Format"):
                    rp = resize_video_reel_format(video_path)
                    if rp: st.video(rp)
            with c3:
                if st.button("✂ Chunk Video"):
                    chunk_video(video_path)
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("Start Generation"):
                with st.spinner("Processing into 30-sec reels..."):
                    cmd = f'python reel_merger.py "{video_path}"'
                    subprocess.run(cmd, shell=True)
                st.success("Reels generated!")

        with tab2:
            show_reels()
            c, s = get_reels_summary()
            st.info(f"Created {c} reels, total size {s:.2f} MB")

# ======== Main ========
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if st.session_state["logged_in"]:
    main_app()
else:
    login()
