import pandas as pd
import ast
from gemini_config import model

# Load dataset
df = pd.read_csv("merged_with_embeddings.csv")
df["embedding_vector"] = df["embedding_vector"].apply(ast.literal_eval)

# ----------------------------
# Fetch transcript by video_id
# ----------------------------
def get_video_transcript(video_id):
    rows = df[df["id"] == video_id]

    if rows.empty:
        return None

    transcripts = rows["transcript_clean"].dropna().tolist()
    return " ".join(transcripts)

# ----------------------------
# Gemini Summarization
# ----------------------------
def summarize_with_gemini(text):
    prompt = f"""
Summarize the following YouTube video transcript in clear and concise bullet points:

{text}
"""
    response = model.generate_content(prompt)
    return response.text

# ----------------------------
# Final Pipeline
# ----------------------------
def summarize_video(video_id):
    transcript = get_video_transcript(video_id)

    if not transcript:
        return "❌ Transcript not found."

    print("Transcript fetched. Sending to Gemini...")

    # Limit length to avoid token issues
    transcript = transcript[:12000]

    return summarize_with_gemini(transcript)

# ----------------------------
# Test Interface
# ----------------------------
if __name__ == "__main__":
    vid = input("Enter Video ID: ")
    summary = summarize_video(vid)

    print("\n🔹 VIDEO SUMMARY 🔹\n")
    print(summary)
