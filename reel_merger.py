from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

input_video = "videoplayback.mp4"
segments_file = "segments.txt"

def time_to_seconds(t):
    # Converts time string like "0.00" or "12.80" to float seconds
    try:
        return float(t)
    except:
        return 0.0

# Step 1: Read and parse segments
segments = []
with open(segments_file, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip() == "":
            continue
        try:
            time_part = line.split("]")[0].strip("[]")
            start_str, end_str = time_part.split(" - ")
            start_sec = time_to_seconds(start_str.strip())
            end_sec = time_to_seconds(end_str.strip())
            if end_sec > start_sec:
                segments.append((start_sec, end_sec))
        except Exception as e:
            print(f"Skipping line due to error: {line.strip()} -> {e}")

print(f"Loaded {len(segments)} segments.")

# Step 2: Load video once
video = VideoFileClip(input_video)
video_duration = video.duration
print(f"Video duration: {video_duration:.2f} seconds")

# Filter out segments beyond video duration
segments = [(max(0, s), min(e, video_duration)) for s,e in segments if s < video_duration]

# Step 3: Create reels by merging segments until 30 seconds max per reel
MAX_REEL_DURATION = 30.0
reels = []
current_reel_segments = []
current_reel_duration = 0.0

for start, end in segments:
    seg_duration = end - start
    if seg_duration <= 0:
        continue

    # If adding this segment exceeds max reel duration, finalize current reel
    if current_reel_duration + seg_duration > MAX_REEL_DURATION:
        if current_reel_segments:
            reels.append(current_reel_segments)
        current_reel_segments = []
        current_reel_duration = 0.0

    current_reel_segments.append((start, end))
    current_reel_duration += seg_duration

# Add last reel if exists
if current_reel_segments:
    reels.append(current_reel_segments)

print(f"Created {len(reels)} merged reels.")

# Helper: resize + pad to 1080x1920 without distortion
def resize_and_pad(clip, target_w=1080, target_h=1920):
    w, h = clip.size
    scale_w = target_w / w
    scale_h = target_h / h
    scale = min(scale_w, scale_h)
    clip_resized = clip.resize(scale)
    nw, nh = clip_resized.size

    pad_left = int((target_w - nw) / 2)
    pad_right = target_w - nw - pad_left
    pad_top = int((target_h - nh) / 2)
    pad_bottom = target_h - nh - pad_top

    clip_padded = clip_resized.margin(
        left=pad_left, right=pad_right, top=pad_top, bottom=pad_bottom, color=(0,0,0)
    )
    return clip_padded

# Step 4: Process each reel, concatenate, resize+pad and save
for i, reel_segments in enumerate(reels, 1):
    clips = []
    for start_sec, end_sec in reel_segments:
        sub = video.subclip(start_sec, end_sec)
        clips.append(sub)
    reel_clip = concatenate_videoclips(clips)

    # Resize and pad
    reel_clip_final = resize_and_pad(reel_clip, 1080, 1920)

    output_filename = f"merged_reel_{i}.mp4"
    print(f"Writing {output_filename}...")
    reel_clip_final.write_videofile(
        output_filename,
        codec="libx264",
        audio_codec="aac",
        fps=video.fps,
        preset="medium",
        threads=4,
        verbose=False,
        logger=None
    )

print("All merged reels created successfully!")
