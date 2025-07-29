from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
import os

# === USER CONFIGURATION ===
VIDEO_PATH = "videoplayback.mp4"         # Your full 5-min video file
SEGMENTS_FILE = "segments.txt"         # Your meaningful segments file (start end format)
OUTPUT_VIDEO = "summary_reel.mp4"
TARGET_DURATION = 60                   # Duration of the summary reel in seconds
FADE_DURATION = 0.5                    # Smooth in/out fade

# === Load Segments ===
def load_segments(path):
    segments = []
    with open(path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    start = float(parts[0])
                    end = float(parts[1])
                    if end > start:
                        segments.append((start, end))
                except ValueError:
                    continue
    return segments

# === Main Function ===
def create_summary_reel():
    print("Loading video...")
    video = VideoFileClip(VIDEO_PATH)
    segments = load_segments(SEGMENTS_FILE)
    print(f"Found {len(segments)} segments.")

    # Sort by duration (longer segments first)
    segments.sort(key=lambda x: x[1] - x[0], reverse=True)

    selected_clips = []
    total_duration = 0

    for start, end in segments:
        seg_duration = end - start
        if total_duration + seg_duration > TARGET_DURATION:
            seg_duration = TARGET_DURATION - total_duration
            end = start + seg_duration

        clip = video.subclip(start, end)

        # Apply fade-in and fade-out
        clip = clip.fadein(FADE_DURATION).fadeout(FADE_DURATION)

        # Safe resizing (fit height to 1080p, pad width)
        clip = clip.resize(height=1080)
        w, h = clip.size
        if w < 1080:
            x_pad = (1080 - w) // 2
            clip = clip.margin(left=x_pad, right=x_pad, color=(0, 0, 0))

        selected_clips.append(clip)
        total_duration += seg_duration
        if total_duration >= TARGET_DURATION:
            break

    if not selected_clips:
        print("No clips selected. Exiting.")
        return

    print(f"Total summary duration: {total_duration:.2f} seconds")
    final_clip = concatenate_videoclips(selected_clips, method="compose")

    # Handle audio
    final_audio = CompositeAudioClip([clip.audio for clip in selected_clips if clip.audio is not None])
    final_clip = final_clip.set_audio(final_audio)

    # Export
    print("Rendering summary reel...")
    final_clip.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", fps=30)
    print("✅ Summary reel saved as:", OUTPUT_VIDEO)

# === Run ===
if __name__ == "__main__":
    create_summary_reel()
