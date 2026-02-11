# 🔮 Personal Oracle API (Backend)

A high-performance RAG (Retrieval-Augmented Generation) API built with FastAPI, LlamaIndex, and Groq. It serves as the brain for the Personal Oracle application, handling document ingestion, vector embeddings, and LLM inference with strict multi-tenancy.

## ⚡ Tech Stack

- **Framework:** FastAPI (Python)
- **AI Orchestration:** LlamaIndex
- **LLM:** Groq (Llama 3.1-8b-instant) - Ultra-fast inference
- **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`) - Local CPU inference
- **Vector DB:** ChromaDB (Persistent storage)
- **Database:** PostgreSQL (Neon.tech) via SQLAlchemy
- **Auth:** Clerk (User ID verification via Headers)

## 🚀 Key Features

- **Multi-Tenant RAG:** Metadata filtering ensures users only chat with _their_ documents.
- **Hybrid Memory:** Uses Vector DB for semantic search and Postgres for chat history.
- **Source Attribution:** Returns exact filenames and page numbers for every AI claim.
- **Connection Pooling:** Robust database handling with SQLAlchemy.

## 🛠️ Setup & Run

1. **Clone the repo**

   ```bash
   git clone https://github.com/yourusername/oracle-backend.git
   cd oracle-backend
   ```

2. **Install Dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install          requirements.txt
   ```

3. **Environment Variables**
   Create a .env file

   GROQ_API_KEY=your_groq_key
   DATABASE_URL=your_neon_postgres_url

4. **Run the Server**
   ```bash
    uvicorn main:app --reload
   ```
   The API will be available at http://localhost:8000.

## 📚 API Endpoints

POST /upload: Ingest PDF/MD files.
POST /chat: Query the RAG engine.
GET /chats/{user_id}: Fetch chat history.
