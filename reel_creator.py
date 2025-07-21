from moviepy.editor import VideoFileClip
import os

input_video = "videoplayback.mp4"
segments_file = "segments.txt"

def time_to_seconds(t):
    
    try:
        return float(t)
    except:
        
        return 0

# Step 1: Read segments.txt and parse segments
segments = []
with open(segments_file, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip() == "":
            continue
        try:
            time_part = line.split("]")[0]  # e.g. "[0.00 - 12.80"
            time_part = time_part.strip("[]")
            start_str, end_str = time_part.split(" - ")
            start_sec = time_to_seconds(start_str.strip())
            end_sec = time_to_seconds(end_str.strip())
            segments.append((start_sec, end_sec))
        except Exception as e:
            print(f"Skipping line due to error: {line.strip()} -> {e}")

print(f"Loaded {len(segments)} segments.")

# Step 2: Load the video once (avoid reloading multiple times)
video = VideoFileClip(input_video)
video_duration = video.duration
print(f"Video duration: {video_duration:.2f} seconds")

# Step 3: Create reels for each segment
for i, (start_sec, end_sec) in enumerate(segments, 1):
    # Validate segment times are within video duration
    if start_sec >= video_duration:
        print(f"Skipping segment {i}: start {start_sec} > video duration {video_duration}")
        continue
    if end_sec > video_duration:
        end_sec = video_duration

    # Limit clip length to max 30 seconds
    if end_sec - start_sec > 30:
        end_sec = start_sec + 30

    print(f"Creating reel {i}: {start_sec:.2f}s to {end_sec:.2f}s")

    clip = video.subclip(start_sec, end_sec)

    # Resize clip height to 1920 keeping aspect ratio
    clip_resized = clip.resize(height=1920)
    w, h = clip_resized.size

    if w > 1080:
        # Crop horizontally 
        x1 = int((w - 1080) / 2)
        clip_resized = clip_resized.crop(x1=x1, width=1080)
    elif w < 1080:
        # Pad left and right 
        x_padding = int((1080 - w) / 2)
        clip_resized = clip_resized.margin(left=x_padding, right=x_padding, color=(0,0,0))

    

    output_file = f"reel_{i}.mp4"
    clip_resized.write_videofile(output_file, codec="libx264", audio_codec="aac")

print("All reels created!")
