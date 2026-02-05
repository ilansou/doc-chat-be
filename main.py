from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.routes import router

# 1. Setup Config
Config.ensure_dirs()

# 2. Initialize App
app = FastAPI(title="Personal Knowledge Oracle API")

# 3. Middleware (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Include Routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)