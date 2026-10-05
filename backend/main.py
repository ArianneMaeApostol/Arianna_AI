import os
import json
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

from google import genai
import backend.config as config
from backend.agents import AGENT_PROMPTS

app = FastAPI(title="ChatGPT-like AI Agent")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Attachment(BaseModel):
    mime_type: str
    data: str  # base64 string

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    attachments: Optional[List[Attachment]] = None

class ChatRequest(BaseModel):
    messages: List[Message]
    agent_id: str = "default"

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    gemini_key = os.getenv("GEMINI_API_KEY") or config.GEMINI_API_KEY
    if not gemini_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured on the server. Please add it to your Vercel Environment Variables or backend/.env file."
        )

    try:
        client = genai.Client(api_key=gemini_key)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize Gemini Client: {str(e)}"
        )

    # Get system instruction for selected agent
    agent_id = request.agent_id or "default"
    agent = AGENT_PROMPTS.get(agent_id, AGENT_PROMPTS["default"])
    system_prompt = agent["system_prompt"]

    # Format the conversational history for Gemini.
    # Note: Gemini expects roles to be 'user' and 'model' (not 'assistant').
    contents = []
    for msg in request.messages:
        role = "user" if msg.role == "user" else "model"
        content_text = msg.content if msg.content.strip() else " "
        parts = [{"text": content_text}]

        if msg.attachments:
            for att in msg.attachments:
                parts.append({
                    "inline_data": {
                        "mime_type": att.mime_type,
                        "data": att.data
                    }
                })

        contents.append({
            "role": role,
            "parts": parts
        })

    def event_generator():
        models_to_try = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash"]

        for attempt, current_model in enumerate(models_to_try):
            started_streaming = False
            try:
                # Query Gemini stream API with model fallback
                response = client.models.generate_content_stream(
                    model=current_model,
                    contents=contents,
                    config={
                        "system_instruction": system_prompt
                    }
                )
                for chunk in response:
                    if chunk.text:
                        started_streaming = True
                        yield f"data: {json.dumps({'text': chunk.text})}\n\n"
                # Successfully finished streaming
                return

            except Exception as e:
                err_str = str(e)
                # If streaming already started, cannot cleanly restart mid-response
                if started_streaming:
                    yield f"data: {json.dumps({'error': err_str})}\n\n"
                    return

                # Check if it's a transient server capacity or rate limit issue
                upper_err = err_str.upper()
                is_transient = any(code in upper_err for code in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "HIGH DEMAND"])

                if attempt < len(models_to_try) - 1 and is_transient:
                    time.sleep(1.0)
                    continue
                else:
                    yield f"data: {json.dumps({'error': err_str})}\n\n"
                    return

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Mount frontend directory for static hosting.
# Check parent directory to locate the sibling folder 'frontend'.
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_path = os.path.join(parent_dir, "frontend")

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {
            "status": "online",
            "message": "Backend server is running, but frontend/ folder is not created yet."
        }
