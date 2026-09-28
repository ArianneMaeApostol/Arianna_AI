#!/bin/bash

# Resolve the absolute path to this script's directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=================================================="
echo " Starting ChatGPT-like AI Agent (Vonet AI)"
echo "=================================================="

# 1. Verify virtual environment exists
if [ ! -d "venv" ]; then
    echo "[-] Error: Virtual environment 'venv' not found."
    echo "    Please create it using: python3 -m venv venv"
    exit 1
fi

# 2. Check if .env file exists and contains the Gemini API key
if [ ! -f "backend/.env" ]; then
    echo "[!] Warning: backend/.env file not found. Creating a template..."
    mkdir -p backend
    echo "# Replace with your actual Gemini API Key" > backend/.env
    echo "GEMINI_API_KEY=" >> backend/.env
fi

# 3. Read the API key value (handles standard properties formats)
API_KEY=$(grep -E "^GEMINI_API_KEY=" backend/.env | cut -d'=' -f2- | tr -d '[:space:]')

if [ -z "$API_KEY" ]; then
    echo "[!] Warning: GEMINI_API_KEY is empty in backend/.env"
    echo "    Please open backend/.env and paste your API key."
    echo "    The server will start but calls to the AI will fail."
    echo ""
fi

# 4. Start the FastAPI development server
echo "[+] Starting FastAPI server at http://localhost:8000"
echo "[+] Press Ctrl+C to stop."
echo ""

./venv/bin/python -m uvicorn backend.main:app --reload --port 8000
