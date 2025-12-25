import os
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")

client = Client(api_key=GEMINI_API_KEY)
