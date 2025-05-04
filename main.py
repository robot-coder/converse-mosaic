from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from liteLLM import LiteLLM
import requests
from typing import Optional, List

app = FastAPI(title="Web-based Chat Assistant")

# Allow CORS for frontend development (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LiteLLM model (you can configure model parameters here)
llm = LiteLLM()

# Store conversation history per session (simple in-memory store)
# For production, consider persistent storage or session management
conversations = {}

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup if needed."""
    pass

@app.get("/")
async def root():
    return {"message": "Welcome to the Web-based Chat Assistant API"}

@app.post("/start_conversation/")
async def start_conversation(session_id: str):
    """
    Initialize a new conversation session.
    """
    conversations[session_id] = []
    return {"status": "started", "session_id": session_id}

@app.post("/send_message/")
async def send_message(
    session_id: str = Form(...),
    message: str = Form(...)
):
    """
    Send a message to the chat assistant and get a response.
    """
    if session_id not in conversations:
        return JSONResponse(status_code=400, content={"error": "Invalid session_id"})
    try:
        # Append user message to conversation history
        conversations[session_id].append({"role": "user", "content": message})
        # Generate response from LLM
        response = llm.chat(conversations[session_id])
        # Append assistant response
        conversations[session_id].append({"role": "assistant", "content": response})
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/select_model/")
async def select_model(model_name: str = Form(...)):
    """
    Switch the underlying LLM model.
    """
    try:
        llm.set_model(model_name)
        return {"status": "model switched", "model": model_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload_media/")
async def upload_media(file: UploadFile = File(...)):
    """
    Handle multimedia uploads.
    """
    try:
        content = await file.read()
        # For demonstration, just return file info
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation_history/")
async def get_conversation_history(session_id: str):
    """
    Retrieve the conversation history for a session.
    """
    if session_id not in conversations:
        return JSONResponse(status_code=400, content={"error": "Invalid session_id"})
    return {"history": conversations[session_id]}

# Additional endpoints can be added for multimedia processing, model info, etc.