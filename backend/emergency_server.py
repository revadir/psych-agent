#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Psych Agent API - Emergency Mode")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str
    password: str

class MessageRequest(BaseModel):
    content: str

@app.get("/")
def root():
    return {"status": "Emergency backend running"}

@app.post("/api/auth/login")
def login(request: LoginRequest):
    if request.email == "admin@example.com" and request.password == "admin123":
        return {
            "access_token": "emergency_token_12345", 
            "token_type": "bearer"
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/chat/sessions/{session_id}/messages")
def send_message(session_id: int, request: MessageRequest):
    return {
        "user_message": {
            "id": 1,
            "role": "user", 
            "content": request.content,
            "created_at": "2025-12-31T18:40:00"
        },
        "assistant_message": {
            "id": 2,
            "role": "assistant",
            "content": "Emergency mode: Backend is temporarily running in simplified mode. AI agent services are being restored.",
            "created_at": "2025-12-31T18:40:01"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
