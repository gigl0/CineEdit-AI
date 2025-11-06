from fastapi import FastAPI
from app.routers.video import router as video_router
from app.routers.ai import router as ai_router

app = FastAPI(title="CineEdit-AI", version="0.1.0")

app.include_router(video_router, prefix="/videos", tags=["videos"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])

@app.get("/")
def root():
    return {"ok": True, "service": "cineedit-backend"}
