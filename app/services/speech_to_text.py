# app/services/speech_to_text.py

import os
import subprocess
import whisper

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



def transcribe_audio(video_path: str) -> str:
    """
    Trascrive l'audio di un video locale usando Whisper in esecuzione locale.
    """
    # 1. Estrai l'audio in WAV
    audio_path = extract_audio(video_path)

    # 2. Carica il modello Whisper locale
    model = whisper.load_model("medium")  # opzioni: "tiny", "base", "small", "medium", "large"

    # 3. Trascrivi
    result = model.transcribe(audio_path, language="en", task="transcribe")

    # 4. Ritorna solo il testo
    return result["text"]
