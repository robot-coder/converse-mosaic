# README.md

# Web-based Chat Assistant with FastAPI and LiteLLM

This project implements a web-based chat assistant with a front-end JavaScript UI and a back-end Python FastAPI server. The server interacts with Large Language Models (LLMs) via LiteLLM, supporting features such as continuous conversations, model selection, and multimedia uploads. The application is designed for deployment on Render.com.

## Features

- **Continuous conversations** with context retention
- **Model selection** among supported LLMs
- **Multimedia uploads** (images, audio, etc.)
- **Deployment-ready** on Render.com

## Technologies Used

- Python 3.11+
- FastAPI
- Uvicorn
- LiteLLM
- Starlette
- Requests
- python-multipart

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Create a virtual environment and activate it

```bash
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server locally

```bash
uvicorn main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

### 5. Deploy on Render.com

- Push your code to a GitHub repository.
- Create a new Web Service on Render.
- Connect your repository.
- Set the start command to:

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

- Ensure environment variables (if any) are configured appropriately.

## API Endpoints

| Endpoint | Method | Description |
| -------- | -------- | ----------- |
| `/chat` | POST | Send a message to the chat assistant. Supports conversation context. |
| `/model` | GET | Retrieve available models. |
| `/upload` | POST | Upload multimedia files. |

## Front-end Integration

The front-end JavaScript UI should interact with these endpoints to provide a seamless chat experience, supporting model selection and multimedia uploads.

## Code Structure

- `main.py`: FastAPI server implementation
- `requirements.txt`: Dependencies list
- `README.md`: This documentation

## License

This project is licensed under the MIT License.

---

# main.py

```python
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import requests
import uuid
import os
from liteLLM import LiteLLM

app = FastAPI()

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LiteLLM instance
llm = LiteLLM()

# Store conversation states
conversations: Dict[str, List[Dict[str, str]]] = {}

@app.get("/model")
def get_models() -> Dict[str, Any]:
    """
    Retrieve available models from LiteLLM.
    """
    try:
        models = llm.get_supported_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat(
    message: str = Form(...),
    conversation_id: Optional[str] = Form(None),
    model: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Handle chat messages, supporting continuous conversations.
    """
    try:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            conversations[conversation_id] = []

        # Append user message
        conversations[conversation_id].append({"role": "user", "content": message})

        # Prepare conversation context
        context = conversations[conversation_id]

        # Generate response from LLM
        response_text = llm.chat(
            messages=context,
            model=model
        )

        # Append assistant response
        conversations[conversation_id].append({"role": "assistant", "content": response_text})

        return {
            "conversation_id": conversation_id,
            "response": response_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handle multimedia file uploads.
    """
    try:
        contents = await file.read()
        filename = f"{uuid.uuid4()}_{file.filename}"
        save_path = os.path.join("uploads", filename)
        os.makedirs("uploads", exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(contents)
        # Here, you can process the uploaded file as needed
        return {"filename": filename, "message": "File uploaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```