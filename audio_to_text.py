import whisper
import os

# Path to the audio file extracted in week1_task1
AUDIO_FILE = os.path.join("..", "week1_task1", "output", "audio.wav")

# Load the medium Whisper model
model = whisper.load_model("medium")

# Transcribe the full audio without early stopping
result = model.transcribe(AUDIO_FILE, condition_on_previous_text=False)

# Save the full transcript text
with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])

# Save the timestamped segments
with open("segments.txt", "w", encoding="utf-8") as f:
    for segment in result["segments"]:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        f.write(f"[{start:.2f} - {end:.2f}] {text}\n")

print("Transcription saved to transcript.txt and segments.txt")
