from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import os, shutil

from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.video_job import VideoJob
from app.schemas.video_job import JobOut
from app.services.video_editor import auto_edit
from app.services.music_sync import choose_music_segment

router = APIRouter()

# crea tabelle al primo import
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", response_model=JobOut)
async def upload_video(file: UploadFile = File(...)):
    input_dir = Path(settings.STORAGE_DIR) / "input"
    output_dir = Path(settings.STORAGE_DIR) / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    suffix = os.path.splitext(file.filename or "")[1] or ".mp4"
    temp_path = input_dir / f"tmp_{file.filename or 'upload.mp4'}"
    with temp_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    db: Session = next(get_db())
    job = VideoJob(input_path=str(temp_path))
    db.add(job); db.commit(); db.refresh(job)

    new_input_path = input_dir / f"{job.id}{suffix}"
    temp_path.rename(new_input_path)
    job.input_path = str(new_input_path)
    db.add(job); db.commit(); db.refresh(job)

    return job

def _process_job(job_id: str, music_path: str | None = None):
    db: Session = next(get_db())
    job = db.get(VideoJob, job_id)
    if not job:
        return
    job.status = "processing"; db.add(job); db.commit()

    try:
        out_path = Path(settings.STORAGE_DIR) / "output" / f"{job.id}.mp4"
        music_sel = choose_music_segment(music_path, settings.MAX_DURATION_S) if music_path else None
        duration = auto_edit(
            input_path=job.input_path,
            output_path=str(out_path),
            max_duration_s=settings.MAX_DURATION_S,
            scene_threshold=settings.SCENE_THRESHOLD,
            music_path=music_sel,
            target_w=settings.TARGET_WIDTH,
            target_h=settings.TARGET_HEIGHT,
            fps=settings.FPS,
        )
        job.output_path = str(out_path)
        job.duration_s = duration
        job.status = "done"
    except Exception as e:
        job.status = "error"
        job.error = str(e)
    finally:
        db.add(job); db.commit()

@router.post("/{job_id}/process", response_model=JobOut)
def start_processing(job_id: str, bg: BackgroundTasks):
    db: Session = next(get_db())
    job = db.get(VideoJob, job_id)
    if not job:
        raise HTTPException(404, "Job non trovato")

    if job.status in ("processing", "done"):
        return job

    bg.add_task(_process_job, job_id, None)
    return job

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: str):
    db: Session = next(get_db())
    job = db.get(VideoJob, job_id)
    if not job:
        raise HTTPException(404, "Job non trovato")
    return job

@router.get("/{job_id}/download")
def download(job_id: str):
    db: Session = next(get_db())
    job = db.get(VideoJob, job_id)
    if not job:
        raise HTTPException(404, "Job non trovato")
    if job.status != "done" or not job.output_path or not Path(job.output_path).exists():
        raise HTTPException(409, "Il job non è pronto")
    return FileResponse(job.output_path, filename=f"{job.id}.mp4", media_type="video/mp4")
