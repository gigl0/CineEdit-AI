from fastapi import FastAPI
from app.routers.video import router as video_router
from app.routers.ai import router as ai_router
from app.routers import video, ai
import sys, os

sys.path.append(os.path.dirname(__file__))

app = FastAPI(title="CineEdit-AI", version="0.1.0")

app.include_router(video_router)
app.include_router(ai_router)

@app.get("/")
def root():
    return {"ok": True, "service": "cineedit-backend"}
