from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import routers
try:
    from backend.routers import chat, data
except ImportError:
    from routers import chat, data

app = FastAPI(
    title="DC Crime & Real Estate Chatbot API",
    description="API for querying DC crime and real estate data",
    version="1.0.0"
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
    "*"  # Allow all for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(data.router, prefix="/api", tags=["data"])

@app.get("/")
def read_root():
    return {"message": "Welcome to DC Crime & Real Estate API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
