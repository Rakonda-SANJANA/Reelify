import re

# Load segments.txt from current folder
try:
    with open("segments.txt", "r", encoding="utf-8") as f:
        segments = f.readlines()
except FileNotFoundError:
    print("segments.txt not found. Place it in the same folder.")
    exit()

important_events = []

# Expanded, meaningful keywords
topic_keywords = [
    "project", "goal", "challenge", "action", "progress", "motivation", "solution",
    "problem", "stuck", "step", "change", "community", "support", "important",
    "highlight", "note", "now", "next", "finally", "remember", "key", "must",
    "however", "but", "so", "because", "therefore", "although"
]

# Process each segment
for line in segments:
    match = re.match(r"\[(.*?) - (.*?)\] (.*)", line)
    if match:
        start, end, text = match.groups()
        duration = float(end) - float(start)
        word_count = len(text.strip().split())
        flagged = False

        if duration > 4 or word_count > 15:
            important_events.append(f"[{start}] Long/Detailed segment ({duration:.1f}s, {word_count} words): {text.strip()}")
            flagged = True

        for keyword in topic_keywords:
            if keyword in text.lower():
                if not flagged:
                    important_events.append(f"[{start}] Keyword '{keyword}' detected: {text.strip()}")
                break

# Write output safely
try:
    with open("analysis.txt", "w", encoding="utf-8") as f:
        if important_events:
            for event in important_events:
                f.write(event + "\n")
        else:
            f.write("No significant events detected.\n")

    print(f"Analysis complete! Found {len(important_events)} important segments.")
    print("analysis.txt has been updated.")

except Exception as e:
    print("Error writing to analysis.txt:", str(e))
