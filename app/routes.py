import uuid
import traceback
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import ChatResponse, SourceNode, UploadResponse
from app.rag_service import rag_service
from app.database import get_db, Chat, Message, Document # <-- Import Document
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str
    chat_id: Optional[str] = None 

# --- GET ENDPOINTS (For Sidebar) ---

@router.get("/documents/{user_id}")
def get_documents(user_id: str, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.user_id == user_id).all()

@router.get("/chats/{user_id}")
def get_chats(user_id: str, db: Session = Depends(get_db)):
    return db.query(Chat).filter(Chat.user_id == user_id).order_by(desc(Chat.created_at)).all()

@router.get("/chat/{chat_id}")
def get_messages(chat_id: str, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat.messages

@router.delete("/chat/{chat_id}")
def delete_chat(chat_id: str, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if chat:
        db.delete(chat)
        db.commit()
    return {"status": "deleted"}

# --- ACTION ENDPOINTS ---

@router.post("/upload", response_model=UploadResponse)
async def upload_files(
    user_id: str = Form(...), 
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db) # <-- Need DB to save filename
):
    try:
        # 1. Ingest into Vector DB
        count = rag_service.ingest_documents(files, user_id)
        
        # 2. Save Metadata to Postgres (So UI remembers them)
        for file in files:
            # Check if exists to avoid duplicates in list
            exists = db.query(Document).filter_by(user_id=user_id, filename=file.filename).first()
            if not exists:
                doc = Document(user_id=user_id, filename=file.filename)
                db.add(doc)
        db.commit()

        return UploadResponse(status="success", files_processed=count, message="Indexed")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # 1. AI Response
        response = rag_service.chat(request.message, request.user_id)
        
        # 2. History Logic
        chat_id = request.chat_id
        if not chat_id:
            chat_id = str(uuid.uuid4())
            new_chat = Chat(id=chat_id, user_id=request.user_id, title=request.message[:30] + "...")
            db.add(new_chat)
            db.commit()

        user_msg = Message(chat_id=chat_id, role="user", content=request.message)
        db.add(user_msg)
        ai_msg = Message(chat_id=chat_id, role="assistant", content=response.response)
        db.add(ai_msg)
        db.commit()

        sources = [
            SourceNode(
                file_name=node.metadata.get("file_name", "Unknown"),
                page_label=node.metadata.get("page_label", "N/A"),
                text_snippet=node.node.get_text()[:200] + "...",
                score=node.score or 0.0
            ) for node in response.source_nodes
        ]
        
        # Return chat_id so frontend knows which chat we are in
        return ChatResponse(response=response.response, sources=sources)
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))