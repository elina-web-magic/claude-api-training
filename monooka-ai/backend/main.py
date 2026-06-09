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
from prompts import run_diet_planner_prompt
from routes import LESSON_ROUTES

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

def get_curriculum():
    if not os.path.exists("curriculum.json"):
        return []
    with open("curriculum.json", "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def get_lesson_by_id(lesson_id: str) -> Optional[dict]:
    curr = get_curriculum()
    for proj in curr:
        for lesson in proj["lessons"]:
            if lesson["id"] == lesson_id:
                return lesson
    return None

# API Endpoints
@app.get("/api/curriculum")
def get_curriculum_endpoint():
    return get_curriculum()

@app.get("/api/chat/{chat_id}")
def get_chat_session(chat_id: str):
    chat = get_chat(chat_id)
    if not chat:
        lesson = get_lesson_by_id(chat_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        chat = {
            "id": chat_id,
            "title": lesson["title"],
            "context": chat_id,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        db = load_db()
        db.append(chat)
        save_db(db)
        
    return chat

@app.post("/api/message")
def send_message(req: SendMessageRequest):
    chat = get_chat(req.chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Add user message
    user_msg = {"role": "user", "content": req.content}
    chat["messages"].append(user_msg)
    # Title remains the lesson title, so we remove the title updating logic
    
    try:
        context_key = chat["context"]
        route = LESSON_ROUTES.get(context_key, {})
        
        if "extractor_prompt" in route and "generator_func" in route:
            # 1. Extraction Phase
            extractor_prompt = route["extractor_prompt"].format(user_input=req.content)
            extract_res = anthropic_client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=150,
                messages=[{"role": "user", "content": extractor_prompt}],
                temperature=0
            )
            
            raw_text = extract_res.content[0].text
            import re
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                raw_text = match.group(0)
                
            # Fallback for missing keys specific to diet planner
            try:
                params = json.loads(raw_text)
                if context_key == "3_promt/001_prompting":
                    params = {
                        "height": str(params.get("height", "unknown")),
                        "weight": str(params.get("weight", "unknown")),
                        "goal": str(params.get("goal", "unknown")),
                        "restrictions": str(params.get("restrictions", "none"))
                    }
            except:
                params = {}
            
            # 2. Generation Phase
            final_prompt = route["generator_func"](**params)
            
            max_tokens = route.get("max_tokens", 1000)
            response = anthropic_client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": final_prompt}],
                temperature=1.0
            )
            bot_text = response.content[0].text
            
        else:
            # Standard chat with custom or generic system prompt
            system_prompt = route.get("system_prompt", "You are Monooka AI, a helpful assistant.")
            api_messages = [{"role": m["role"], "content": m["content"]} for m in chat["messages"]]
            
            max_tokens = route.get("max_tokens", 500)
            response = anthropic_client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=max_tokens,
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
