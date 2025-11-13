# app/services/speech_to_text.py

import os
import subprocess
import whisper
import torch

def extract_audio(video_path: str) -> str:
    """
    Estrae l'audio da un file video in formato WAV senza perdita di qualità.
    """
    audio_path = os.path.splitext(video_path)[0] + "_audio.wav"
    command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",                # no video
        "-acodec", "pcm_s16le",
        "-ar", "44100",       # qualità CD
        "-ac", "2",           # stereo
        audio_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return audio_path



import whisper

def transcribe_audio(video_path: str) -> str:
    """
    Trascrive l'audio del video usando Whisper GPU (se disponibile)
    """
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = whisper.load_model("base", device=device)
    result = model.transcribe(video_path)
    return result["text"]

