import whisper

# Load Whisper model (medium)
model = whisper.load_model("medium")

# Transcribe directly (no saving to file)
result = model.transcribe(r"..\week1_task1\output\audio.wav", condition_on_previous_text=False)

# Print the full transcript to check
print("\n----- FULL TRANSCRIPT START -----\n")
print(result["text"])
print("\n----- FULL TRANSCRIPT END -----\n")

# Show total segments detected
print(f"Total segments detected: {len(result['segments'])}")
