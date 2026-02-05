from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str

class SourceNode(BaseModel):
    file_name: str
    page_label: str
    text_snippet: str
    score: float

class ChatResponse(BaseModel):
    response: str
    sources: List[SourceNode]

class UploadResponse(BaseModel):
    status: str
    files_processed: int
    message: str