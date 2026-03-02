# QueryTube AI - Infosys Springboard Internship Project

Semantic search and summarization system for YouTube videos.  
This project collects channel video metadata, builds text embeddings, indexes vectors with FAISS, and serves search/summarization APIs with a simple web UI.

## Features
- Collects YouTube channel video data via YouTube Data API v3
- Builds semantic embeddings using `sentence-transformers` (`all-MiniLM-L6-v2`)
- Stores and searches vectors using FAISS
- Returns top semantic matches for a user query
- Summarizes selected video transcripts using Gemini
- Includes FastAPI backend + static frontend + Streamlit prototype

## Repository Structure
```text
.
|-- frontend/
|   |-- index.html
|   |-- search.html
|   |-- css/style.css
|   `-- js/app.js
|-- semanticsearchproject/
|   |-- api.py
|   |-- app.py
|   |-- collecting.py
|   |-- gemini_config.py
|   |-- vector_store.py
|   |-- requirements.txt
|   |-- pyproject.toml
|   `-- ... (data and helper scripts)
|-- CSV data to Vector DB(Qdrant)/
|-- embedding-code and csv/
|-- files/
|-- YT_info.py
`-- README.md
```

## Tech Stack
- Python 3.10+
- FastAPI + Uvicorn
- Streamlit
- Pandas, NumPy
- Sentence Transformers
- FAISS
- Google GenAI (Gemini API)
- HTML, CSS, JavaScript (frontend)

## Environment Variables
Create `semanticsearchproject/.env`:

```env
YOUTUBE_API_KEY=your_youtube_api_key
CHANNEL_ID=your_channel_id
GEMINI_API_KEY=your_gemini_api_key
```

Never commit real keys. Use placeholders in shared files.

## Local Setup
```powershell
cd semanticsearchproject
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install fastapi uvicorn python-dotenv google-genai faiss-cpu streamlit
```

## Run the Project
1. Generate/update dataset and embeddings as needed (project scripts).
2. Start backend API:
```powershell
cd semanticsearchproject
uvicorn api:app --reload
```
3. Load vectors into memory:
   - Call `POST /ingest` once after starting API.
4. Open frontend:
   - Open `frontend/index.html` in browser (or serve via local static server).
5. Optional Streamlit UI:
```powershell
cd semanticsearchproject
streamlit run app.py
```

## API Endpoints
- `POST /ingest` -> loads `merged_with_embeddings.csv` and builds FAISS index
- `GET /search?query=<text>&top_k=5` -> semantic search results
- `GET /summarize?video_id=<id>` -> Gemini summary for selected transcript

## Security Notes
- `.env` is ignored and must remain local only.
- Rotate any keys that were previously exposed.
- Restrict API keys by referrer/IP and quota in provider dashboards.

## How It Works
1. Collect video metadata/transcript data for a channel.
2. Clean/process text and generate embedding vectors.
3. Persist embeddings in CSV and optional FAISS index file.
4. `/ingest` loads vectors and creates in-memory FAISS index.
5. User search query is embedded and matched against indexed vectors.
6. Selected result transcript is passed to Gemini for concise summary output.
