import os
import shutil
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
# CHANGED: Import Groq and HuggingFace
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from app.config import Config

class RAGService:
    def __init__(self):
        self._index = None
        self._chat_engine = None
        self._initialize_models()
        self._initialize_index()

    def _initialize_models(self):
        """Setup Free Open Source Models"""
        if not Config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
            
        # 1. Setup LLM (Groq - Llama 3)
        Settings.llm = Groq(
            model=Config.LLM_MODEL, 
            api_key=Config.GROQ_API_KEY
        )
        
        # 2. Setup Embedding (HuggingFace - Local CPU)
        # We explicitly map it to CPU to save costs on deployment
        print("📥 Loading embedding model (this might take a moment)...")
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=Config.EMBEDDING_MODEL,
            device="cpu" 
        )

    def _initialize_index(self):
        """Loads the index from ChromaDB if it exists."""
        db = chromadb.PersistentClient(path=Config.PERSIST_DIR)
        chroma_collection = db.get_or_create_collection(Config.COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        if chroma_collection.count() > 0:
            print("📚 Loading existing index from storage...")
            self._index = VectorStoreIndex.from_vector_store(
                vector_store, storage_context=storage_context
            )
            self._create_chat_engine()
        else:
            print("⚠️ No index found. Please upload documents.")

    def _create_chat_engine(self):
        if self._index:
            self._chat_engine = self._index.as_chat_engine(
                chat_mode="context",
                system_prompt="You are a helpful Knowledge Oracle. Answer strictly based on the provided context."
            )

    def ingest_documents(self, files):
        Config.ensure_dirs()
        
        # Clear existing data to avoid duplicates (Optional strategy)
        if os.path.exists(Config.PERSIST_DIR):
            shutil.rmtree(Config.PERSIST_DIR)
        if os.path.exists(Config.DATA_DIR):
            shutil.rmtree(Config.DATA_DIR)
        Config.ensure_dirs()

        for file in files:
            file_location = os.path.join(Config.DATA_DIR, file.filename)
            with open(file_location, "wb") as f:
                shutil.copyfileobj(file.file, f)

        db = chromadb.PersistentClient(path=Config.PERSIST_DIR)
        chroma_collection = db.get_or_create_collection(Config.COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        print("🧠 Processing documents...")
        documents = SimpleDirectoryReader(Config.DATA_DIR).load_data()
        self._index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )
        
        self._create_chat_engine()
        return len(files)

    def chat(self, message: str):
        if not self._chat_engine:
            raise Exception("Index not initialized. Please upload documents first.")
        
        response = self._chat_engine.chat(message)
        return response

rag_service = RAGService()