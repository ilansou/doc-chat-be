import os
import shutil
import time
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
import chromadb
from app.config import Config

class RAGService:
    def __init__(self):
        self._initialize_models()
        # Initialize Chroma Client once
        self._client = chromadb.PersistentClient(path=Config.PERSIST_DIR)
        self._collection = self._client.get_or_create_collection(Config.COLLECTION_NAME)

    def _initialize_models(self):
        Settings.llm = Groq(model=Config.LLM_MODEL, api_key=Config.GROQ_API_KEY)
        # Use CPU for embeddings to save cost
        Settings.embed_model = HuggingFaceEmbedding(model_name=Config.EMBEDDING_MODEL, device="cpu")

    def _get_index(self):
        vector_store = ChromaVectorStore(chroma_collection=self._collection)
        return VectorStoreIndex.from_vector_store(vector_store=vector_store)

    def ingest_documents(self, files, user_id: str):
        Config.ensure_dirs()
        
        # 1. Create a specific temp folder for this user
        # Sanitize user_id just in case
        safe_user_id = "".join([c for c in user_id if c.isalnum() or c in ('-','_')])
        temp_dir = os.path.join(Config.DATA_DIR, safe_user_id)
        
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except OSError:
                pass # Ignore if previous run left locked files
        
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # 2. Save uploaded files to temp folder
            for file in files:
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)

            # 3. Load Documents
            loader = SimpleDirectoryReader(temp_dir)
            documents = loader.load_data()
            
            # 4. TAGGING: Add user_id to every document metadata
            for doc in documents:
                doc.metadata["user_id"] = user_id

            # 5. Insert into Vector DB (Append mode)
            vector_store = ChromaVectorStore(chroma_collection=self._collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # This appends to the existing collection
            VectorStoreIndex.from_documents(documents, storage_context=storage_context)
            
            return len(files)

        finally:
            # 6. Cleanup (Safe Mode)
            # We wait a split second to let file handles release
            time.sleep(0.5)
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except OSError as e:
                print(f"⚠️ Warning: Could not delete temp files immediately: {e}")
                # We don't raise the error, so the user still gets a 'Success' response

    def chat(self, message: str, user_id: str):
        index = self._get_index()
        
        # Filter by user_id
        filters = MetadataFilters(
            filters=[
                ExactMatchFilter(key="user_id", value=user_id)
            ]
        )

        chat_engine = index.as_chat_engine(
            chat_mode="context",
            filters=filters,
            system_prompt="You are a helpful assistant. Answer based only on the user's documents."
        )
        
        return chat_engine.chat(message)

rag_service = RAGService()