import re

# Load segments file
with open("segments.txt", "r", encoding="utf-8") as f:
    segments = f.readlines()

important_events = []
# Expanded keywords
topic_keywords = [
    "introduction", "summary", "important", "highlight", "conclusion",
    "tip", "note", "now", "next", "finally", "remember", "key", "must"
]

for line in segments:
    match = re.match(r"\[(.*?) - (.*?)\] (.*)", line)
    if match:
        start, end, text = match.groups()
        duration = float(end) - float(start)

        # Rule 1: Mark segments longer than 5 seconds
        if duration > 5:
            important_events.append(f"Long segment ({duration:.1f}s) at {start}: {text.strip()}")

        # Rule 2: Mark any keyword match
        for keyword in topic_keywords:
            if keyword.lower() in text.lower():
                important_events.append(f"Keyword '{keyword}' at {start}: {text.strip()}")
                break

# Save analysis result
with open("analysis.txt", "w", encoding="utf-8") as f:
    if important_events:
        for event in important_events:
            f.write(event + "\n")
    else:
        f.write("No significant events detected.\n")

print("Text analysis complete. Check analysis.txt.")
