import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity

# ----------------------------
# 1. Load your cleaned dataset
# ----------------------------
INPUT_CSV = "merged_cleaned.csv"
OUTPUT_CSV = "merged_with_embeddings.csv"

df = pd.read_csv(INPUT_CSV)

print("Dataset loaded:", df.shape)
print("Columns:", df.columns.tolist())

# ----------------------------
# 2. Choose the text column for embeddings
# Priority:
# transcript_clean > title_clean
# ----------------------------
if "transcript_clean" in df.columns:
    df["text_for_embedding"] = df["transcript_clean"].fillna("")
else:
    df["text_for_embedding"] = df["title_clean"].fillna("")

# ----------------------------
# 3. Load open-source embedding model
# ----------------------------
model_name = "all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

print("Loaded model:", model_name)

# ----------------------------
# 4. Generate embeddings
# ----------------------------
texts = df["text_for_embedding"].tolist()

print("Generating embeddings...")

embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True
)

# Convert to list for saving in CSV
df["embedding_vector"] = embeddings.tolist()

# ----------------------------
# 5. Save final dataset
# ----------------------------
df.to_csv(OUTPUT_CSV, index=False)

print("✅ Embeddings generated and saved to:", OUTPUT_CSV)

# ----------------------------
# 6. Quick Similarity Test (Validation)
# ----------------------------
print("\n🔍 RUNNING SIMILARITY TEST...")

sample_indices = [0, 1, 2]  # you can change this
vecs = embeddings[sample_indices]

sim_matrix = cosine_similarity(vecs)

print("Sample similarity matrix:")
print(np.round(sim_matrix, 3))
