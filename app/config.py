import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Paths
    DATA_DIR = "data"
    PERSIST_DIR = "storage_chroma"
    COLLECTION_NAME = "knowledge_base"
    
    # --- MODEL SETTINGS ---
    LLM_MODEL = "llama-3.1-8b-instant" 
    
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2" 

    @staticmethod
    def ensure_dirs():
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.PERSIST_DIR, exist_ok=True)