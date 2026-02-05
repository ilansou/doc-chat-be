from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.models import ChatRequest, ChatResponse, SourceNode, UploadResponse
from app.rag_service import rag_service

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        count = rag_service.ingest_documents(files)
        return UploadResponse(
            status="success",
            files_processed=count,
            message="Documents processed and index rebuilt successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Get response from LlamaIndex
        response = rag_service.chat(request.message)
        
        # Parse Sources (The Killer Feature)
        sources = []
        for node in response.source_nodes:
            # FIX: Safely get metadata. Some nodes might not have 'page_label'
            metadata = node.metadata if node.metadata else {}
            
            sources.append(SourceNode(
                file_name=metadata.get("file_name", "Unknown"),
                page_label=metadata.get("page_label", "N/A"), # Fallback if no page number
                text_snippet=node.node.get_text()[:200] + "...",
                score=node.score if node.score else 0.0
            ))
            
        return ChatResponse(response=response.response, sources=sources)
        
    except Exception as e:
        # Print the error to the terminal so you can see what went wrong
        print(f"Error: {str(e)}") 
        raise HTTPException(status_code=500, detail=str(e))