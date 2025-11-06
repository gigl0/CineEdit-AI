from fastapi import FastAPI
from app.routers.video import router as video_router
from app.routers.ai import router as ai_router
from app.services.ai_editor_local import generate_edit_plan
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Assicura che il progetto riconosca i moduli interni
sys.path.append(os.path.dirname(__file__))

app = FastAPI(
    title="CineEdit-AI",
    version="0.1.0",
    description="Backend per generare e applicare piani di montaggio AI"
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # puoi restringerlo dopo, es: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Includi i router principali
app.include_router(video_router)
app.include_router(ai_router)

@app.get("/")
def root():
    return {"ok": True, "service": "cineedit-backend"}
