# app/routers/episodes.py
import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.video_job import VideoJob
from app.services.episode_analyzer import run_episode_analysis
from app.core.config import settings

router = APIRouter(prefix="/episodes", tags=["episodes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def analysis_task(job_id: str, video_path: str, db: Session):
    """Task eseguito in background per analizzare l'episodio."""
    try:
        # Aggiorna lo stato a "processing"
        db.query(VideoJob).filter(VideoJob.id == job_id).update({"status": "processing"})
        db.commit()

        results = run_episode_analysis(video_path)

        # Salva i risultati e aggiorna lo stato a "analyzed"
        db.query(VideoJob).filter(VideoJob.id == job_id).update({
            "status": "analyzed",
            "analysis_results": results
        })
        db.commit()
        print(f"Analisi completata per il job {job_id}")
    except Exception as e:
        db.query(VideoJob).filter(VideoJob.id == job_id).update({
            "status": "error",
            "error": str(e)
        })
        db.commit()
        print(f"Errore nell'analisi del job {job_id}: {e}")

@router.post("/upload_and_analyze")
async def upload_and_analyze(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Carica un episodio, crea un job di analisi e lo avvia in background.
    """
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    video_path = os.path.join(settings.STORAGE_DIR, "input", filename)

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Crea il job nel DB
    new_job = VideoJob(
        job_type='episode_analysis',
        status='queued',
        input_path=video_path,
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # Avvia il task in background
    background_tasks.add_task(analysis_task, new_job.id, video_path, SessionLocal())

    return {"message": "Analisi episodio avviata.", "job_id": new_job.id}

@router.get("/status/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Endpoint per il frontend per fare polling e conoscere lo stato/risultati dell'analisi.
    """
    job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
    if not job:
        return {"error": "Job non trovato"}
    return {
        "job_id": job.id,
        "status": job.status,
        "results": job.analysis_results,
        "error": job.error
    }