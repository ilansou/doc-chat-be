import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # GROQ API KEY (Free)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # Paths
    DATA_DIR = "data"
    PERSIST_DIR = "storage_chroma"
    COLLECTION_NAME = "knowledge_base"
    
    # Model Settings
    LLM_MODEL = "llama3-8b-8192" # Very fast, free on Groq
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2" # Small, fast, runs on CPU

    @staticmethod
    def ensure_dirs():
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.PERSIST_DIR, exist_ok=True)