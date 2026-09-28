import os
import sys
from dotenv import load_dotenv

# Ensure the backend directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Explicitly load backend/.env file
backend_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(backend_dir, ".env")
load_dotenv(dotenv_path)

try:
    from google import genai
except ImportError:
    print("ERROR: google-genai is not installed. Please run 'pip install -r backend/requirements.txt' first.")
    sys.exit(1)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY is not set in backend/.env or your environment variables.")
    print("Please open backend/.env and add your key: GEMINI_API_KEY=AIzaSy...")
    sys.exit(1)

print("Connecting to Gemini API...")
try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Say 'Hello, Vonet Agent is online!' in a brief, friendly sentence."
    )
    print("\n[SUCCESS] Connected to Gemini API successfully!")
    print(f"Gemini Response: {response.text.strip()}")
except Exception as e:
    print(f"\n[FAILURE] Failed to connect: {str(e)}")
    print("Please double check that your API key is correct and you have internet access.")
    sys.exit(1)
