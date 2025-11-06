import subprocess
import json

def generate_edit_plan(scene_description: str, transcript: str | None = None) -> dict:
    """
    Genera un piano di montaggio creativo usando Ollama in locale.
    """
    prompt = f"""
    Sei un video editor cinematografico che crea short emozionali per social.
    Analizza la scena e genera un piano d'editing creativo.

    Scena: {scene_description}
    Trascrizione (se presente): {transcript or "Nessuna trascrizione"}

    Fornisci l'output in formato JSON con le seguenti chiavi:
    {{
      "mood": "tono visivo (es. drammatico, ispirazionale, comico)",
      "music": "genere e ritmo consigliato (es. ambient piano, trap veloce)",
      "caption": "testo breve da sovrapporre al video",
      "fx": ["zoom_in", "color_boost", "fade_in"],
      "color": "tone o filtro consigliato (es. teal-orange, b/n, soft warm)"
    }}
    """

    # Esegui il modello locale tramite Ollama
    result = subprocess.run(
        ["ollama", "run", "llama3", prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    raw_output = result.stdout.strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return {"error": "invalid JSON", "raw_output": raw_output}
