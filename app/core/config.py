from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./cineedit.db"
    STORAGE_DIR: str = "./data"
    MAX_DURATION_S: int = 60
    SCENE_THRESHOLD: int = 30
    TARGET_HEIGHT: int = 1920
    TARGET_WIDTH: int = 1080
    FPS: int = 30
    OPENAI_API_KEY: str = ""  

    class Config:
        env_file = ".env"
        extra = "allow"  # permette variabili extra nell'env

settings = Settings()

Path(settings.STORAGE_DIR, "input").mkdir(parents=True, exist_ok=True)
Path(settings.STORAGE_DIR, "output").mkdir(parents=True, exist_ok=True)
