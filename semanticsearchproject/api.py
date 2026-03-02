from fastapi import FastAPI
import pandas as pd
import numpy as np
import faiss
import ast
from sentence_transformers import SentenceTransformer
from gemini_config import client
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="QueryTube AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

df = None
index = None
model_embed = SentenceTransformer("all-MiniLM-L6-v2")

# ------------------ INGEST ------------------
@app.post("/ingest")
def ingest_data():
    global df, index

    df = pd.read_csv("merged_with_embeddings.csv")
    df["embedding_vector"] = df["embedding_vector"].apply(ast.literal_eval)
    embeddings = np.vstack(df["embedding_vector"].values).astype("float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, "youtube_embeddings.index")

    return {"status": "success", "vectors_loaded": index.ntotal}

# ------------------ SEARCH ------------------
@app.get("/search")
def semantic_search(query: str, top_k: int = 5):
    global df, index

    if df is None or index is None:
        return {"error": "VectorDB not loaded. Call /ingest first."}

    try:
        query_vec = model_embed.encode([query], normalize_embeddings=True).astype("float32")
        distances, indices = index.search(query_vec, top_k)

        results = []
        for rank, idx in enumerate(indices[0]):
            video = df.iloc[int(idx)]
            score = 1 / (1 + float(distances[0][rank]))

            results.append({
                "video_id": str(video["id"]),
                "title": str(video.get("title_clean", video.get("title", ""))),
                "channel_name": str(video.get("channel_title", "")),
                "similarity": round(score, 4)
            })

        return {"query": query, "results": results}

    except Exception as e:
        return {"error": str(e)}


# ------------------ SUMMARIZE ------------------
@app.get("/summarize")
def summarize(video_id: str):
    global df

    if df is None:
        return {"error": "Dataset not loaded. Call /ingest first."}

    try:
        rows = df[df["id"] == video_id]

        if rows.empty:
            return {"error": "Video ID not found in dataset."}

        transcript = " ".join(rows["transcript_clean"].dropna().astype(str).tolist())

        if len(transcript.strip()) == 0:
            return {"error": "Transcript is empty for this video."}

        transcript = transcript[:12000]

        prompt = f"Summarize this YouTube transcript in clear bullet points:\n{transcript}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return {"video_id": video_id, "summary": response.text}

    except Exception as e:
        return {"error": str(e)}
