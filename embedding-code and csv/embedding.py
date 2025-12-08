import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import ast

# Load model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ---------------------------
# Read your dataset
# ---------------------------
input_file = "final_merged_dataset.csv"
output_file = "final_with_embeddings.csv"

df = pd.read_csv(input_file)

# ---------------------------
# Clean and combine columns
# ---------------------------
def clean_text(text):
    if pd.isna(text):
        return ""
    return ''.join(e.lower() for e in str(text) if e.isalnum() or e.isspace())

df["title"] = df["title"].apply(clean_text)
df["transcript"] = df["transcript"].apply(clean_text)

# Combine title + transcript
df["combined"] = df["title"] + " " + df["transcript"]

# ---------------------------
# Chunking function
# ---------------------------
def chunk_text(text, max_words=300):
    words = text.split()
    chunks = []

    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)

    return chunks

df["chunks"] = df["combined"].apply(chunk_text)

# ---------------------------
# Function to embed all chunks and return averaged embedding
# ---------------------------
def embed_chunks(chunk_list):
    if len(chunk_list) == 0:
        return None

    # Embed each chunk
    chunk_embeddings = model.encode(chunk_list)

    # Average pooling → final embedding
    final_emb = np.mean(chunk_embeddings, axis=0)

    return final_emb.tolist()

# Apply embedding to each row
df["embedding"] = df["chunks"].apply(embed_chunks)

# ---------------------------
# Save updated CSV
# ---------------------------
df.to_csv(output_file, index=False)
print("✓ Full embeddings (with chunking) successfully generated and saved to:", output_file)
