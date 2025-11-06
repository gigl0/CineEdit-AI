# app/routers/ai.py
from fastapi import APIRouter
from app.services.caption_generator import generate_placeholder_caption

router = APIRouter()

@router.post("/caption")
def caption():
    """
    Genera una caption temporanea per un video.
    """
    return {"caption": generate_placeholder_caption()}
