import uuid, datetime as dt
from sqlalchemy import Column, String, DateTime, Integer, Text
from app.db.base import Base

class VideoJob(Base):
    __tablename__ = "video_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, default="queued")  # queued|processing|done|error
    input_path = Column(Text, nullable=False)
    output_path = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    duration_s = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)
