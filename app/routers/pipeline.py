from fastapi import APIRouter
from app.services.speech_to_text import transcribe_audio
from importlib import reload
import app.services.ai_editor_local as ai_local
reload(ai_local)
from app.services.ai_editor_local import generate_edit_plan
from app.services.video_editor import apply_edit_plan
import asyncio

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/full")
async def full_pipeline(data: dict):
    """
    Esegue l'intera pipeline di CineEdit-AI in modo non bloccante.
    """
    video_path = data.get("video_path")
    if not video_path:
        return {"error": "video_path mancante"}

    loop = asyncio.get_event_loop()

    # Step 1 - Trascrizione
    print("[1] Inizio trascrizione")
    transcript = await loop.run_in_executor(None, transcribe_audio, video_path)
    print("[2] Fine trascrizione")

    # Step 2 - Generazione piano AI
    print("[3] Inizio generazione piano di montaggio")

    plan = await loop.run_in_executor(
        None,
        lambda: generate_edit_plan(
            f"Analizza e monta il video '{video_path}'",
            transcript
        )
    )

    print("[4] Fine generazione piano di montaggio")

    # Step 3 - Editing video
    print("[5] Inizio applicazione piano di montaggio")

    output_path = await loop.run_in_executor(
        None,
        lambda: apply_edit_plan(video_path, plan)
    )

    print("[6] Fine applicazione piano di montaggio")

    return {
        "ok": True,
        "video_path": video_path,
        "transcript": transcript[:300] + "..." if transcript else "",
        "plan": plan,
        "output_video": output_path
    }
