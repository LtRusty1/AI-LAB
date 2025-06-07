from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI(title="AI-Lab Backend - Minimal")

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    error: str = None
    thought_process: str = None
    session_id: str = None

@app.get("/")
def read_root():
    return {"message": "AI-Lab backend is running!", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat: ChatRequest):
    # Simple echo response for testing
    return ChatResponse(
        response=f"Echo: {chat.message}",
        status="success",
        thought_process="This is a simple echo response for testing",
        session_id=chat.session_id or str(int(time.time()))
    ) 