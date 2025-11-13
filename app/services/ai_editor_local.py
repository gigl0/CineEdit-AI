import subprocess
import json
import re


def clean_ollama_output(raw: str) -> str:
    """
    Pulisce l'output del modello rimuovendo testo extra
    e lasciando solo il blocco JSON valido.
    """
    # Cerca un blocco JSON in mezzo al testo
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return match.group(0)
    return raw.strip()


def generate_edit_plan(scene_description: str, transcript: str | None = None) -> dict:
    """
    Genera un piano di montaggio creativo usando Ollama in locale.
    Funzione completamente standalone, compatibile con run_in_executor.
    """

    prompt = f"""
Sei un video editor cinematografico che crea short emozionali per social.
Analizza la scena e genera un piano di montaggio creativo.

Scena: {scene_description}
Trascrizione: {transcript or "Nessuna trascrizione"}

Fornisci l'output **solo** in formato JSON valido, esempio:

{{
  "mood": "ispirazionale",
  "music": "ambient piano",
  "caption": "testo breve",
  "fx": ["zoom_in", "fade_in"],
  "color": "soft warm"
}}

NON aggiungere testo prima o dopo il JSON.
    """

    try:
        # Esegui Ollama
        result = subprocess.run(
            ["ollama", "run", "llama3", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except Exception as e:
        return {"error": str(e)}

    raw_output = result.stdout.strip()

    # Pulisci eventuale testo extra
    cleaned = clean_ollama_output(raw_output)

    # Prova ad interpretare come JSON
    try:
        return json.loads(cleaned)
    except Exception:
        return {
            "error": "invalid JSON",
            "raw_output": raw_output,
            "cleaned": cleaned
        }
