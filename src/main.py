from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import app_configs, settings
from src.routes.voice import router as voice_router
from src.routes.voice_rag import router as voice_rag_router

app = FastAPI(**app_configs)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Include voice routes
app.include_router(
    voice_router,
    prefix="/voice",
    tags=["Voice APIs"]
)

app.include_router(voice_rag_router)
