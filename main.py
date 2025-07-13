import streamlit as st
import os
import subprocess

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    success = run_ffmpeg_command(command)
    if success and os.path.exists(audio_path):
        return audio_path
    else:
        return None

def resize_video_reel_format(video_path):
    resized_path = os.path.join(OUTPUT_DIR, "resized.mp4")
    command = (
        f'ffmpeg -i "{video_path}" -vf '
        '"scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" '
        f'"{resized_path}" -y'
    )
    success = run_ffmpeg_command(command)
    if success and os.path.exists(resized_path):
        return resized_path
    else:
        return None

def chunk_video(video_path):
    chunk_pattern = os.path.join(OUTPUT_DIR, "chunk%03d.mp4")
    command = f'ffmpeg -i "{video_path}" -c copy -map 0 -segment_time 300 -f segment "{chunk_pattern}" -y'
    success = run_ffmpeg_command(command)
    if success:
        # Let's list created chunks to confirm
        created_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("chunk") and f.endswith(".mp4")]
        if created_files:
            st.write(f"Chunks created: {created_files}")
        else:
            st.warning("No chunk files found in output folder.")
        return OUTPUT_DIR
    else:
        return None

# Streamlit UI
st.title("Video Processing & Audio Extractor")

uploaded_file = st.file_uploader("Upload your video", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file:
    video_path = save_uploaded_file(uploaded_file)
    st.success(f"Video uploaded successfully: {video_path}")

    if st.button("Extract Audio"):
        audio_path = extract_audio(video_path)
        if audio_path:
            st.audio(audio_path)
            st.success(f"Audio extracted and saved to: {audio_path}")
        else:
            st.error("Audio extraction failed.")

    if st.button("Convert to Reel Format"):
        resized_path = resize_video_reel_format(video_path)
        if resized_path:
            st.video(resized_path)
            st.success(f"Video resized to 1080x1920 and saved to: {resized_path}")
        else:
            st.error("Video resize failed.")

    if st.button("Chunk Video (Optional)"):
        chunk_dir = chunk_video(video_path)
        if chunk_dir:
            st.success(f"Video chunked and saved in folder: {chunk_dir}")
        else:
            st.error("Video chunking failed.")
