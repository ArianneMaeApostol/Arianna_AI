import os
from dotenv import load_dotenv

# Load environment variables from backend/.env explicitly
backend_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(backend_dir, ".env")
load_dotenv(dotenv_path)

# First check if the key is in environment variables (which loads from .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set. The backend will start, but requests to the AI agent will fail until you provide a key in backend/.env")
