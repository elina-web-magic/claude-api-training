import os
import json
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from anthropic import Anthropic

# Load env variables (assuming .env is in the parent parent directory where the training repo is)
load_dotenv(dotenv_path="../../.env")

app = FastAPI(title="Monooka AI Backend")

# Enable CORS for the Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic Client
anthropic_client = Anthropic()

# Database File Path
DB_FILE = "chats.json"

# Models
class Message(BaseModel):
    role: str
    content: str

class ChatSession(BaseModel):
    id: str
    title: str
    context: str
    created_at: str
    messages: List[Message]

class CreateChatRequest(BaseModel):
    context: str

class SendMessageRequest(BaseModel):
    chat_id: str
    content: str

# Helper functions to manage the DB
def load_db() -> List[dict]:
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_db(data: List[dict]):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_chat(chat_id: str) -> Optional[dict]:
    db = load_db()
    for chat in db:
        if chat["id"] == chat_id:
            return chat
    return None

def update_chat(updated_chat: dict):
    db = load_db()
    for i, chat in enumerate(db):
        if chat["id"] == updated_chat["id"]:
            db[i] = updated_chat
            save_db(db)
            return
    db.append(updated_chat)
    save_db(db)

# API Endpoints
@app.get("/api/history")
def get_history():
    db = load_db()
    # Return minimal info for the sidebar
    return [{"id": chat["id"], "title": chat["title"], "context": chat["context"]} for chat in reversed(db)]

@app.get("/api/chat/{chat_id}")
def get_chat_session(chat_id: str):
    chat = get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@app.post("/api/chat")
def create_chat(req: CreateChatRequest):
    new_chat = {
        "id": str(uuid.uuid4()),
        "title": f"New Chat ({req.context})",
        "context": req.context,
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    db = load_db()
    db.append(new_chat)
    save_db(db)
    return new_chat

@app.post("/api/message")
def send_message(req: SendMessageRequest):
    chat = get_chat(req.chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Add user message
    user_msg = {"role": "user", "content": req.content}
    chat["messages"].append(user_msg)
    
    # Update title based on first message if it's "New Chat"
    if chat["title"].startswith("New Chat"):
        chat["title"] = req.content[:30] + ("..." if len(req.content) > 30 else "")

    # Call Claude API based on Context
    # For now, we simulate calling the logic from the notebooks using a generic system prompt based on context
    
    system_prompt = "You are Monooka AI, a helpful assistant."
    if chat["context"] == "001_prompting":
        system_prompt += " The user is testing prompt engineering concepts. Provide clear, direct answers, maintaining the persona requested."
    elif chat["context"] == "001_promt_evals_practice":
        system_prompt += " The user is practicing prompt evaluation. Act as an evaluator grading AI outputs based on criteria."
        
    try:
        # Prepare messages for Anthropic (excluding any internal UI-only messages if needed)
        api_messages = [{"role": m["role"], "content": m["content"]} for m in chat["messages"]]
        
        response = anthropic_client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            system=system_prompt,
            messages=api_messages
        )
        
        bot_text = response.content[0].text
        
    except Exception as e:
        bot_text = f"Error calling Claude API: {str(e)}"
        
    # Add bot message
    bot_msg = {"role": "assistant", "content": bot_text}
    chat["messages"].append(bot_msg)
    
    update_chat(chat)
    
    return {"message": bot_text}
