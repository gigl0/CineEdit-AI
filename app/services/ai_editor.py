# app/services/ai_editor.py
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_edit_plan(scene_description: str, transcript: str | None = None) -> dict:
    """
    Usa un modello AI per generare un piano di montaggio creativo
    a partire da una descrizione di scena (e opzionalmente dal parlato).
    """
    user_prompt = f"""
    Sei un video editor cinematografico che crea short emozionali per social.
    Analizza la scena seguente e genera un piano d'editing creativo.

    Scena: {scene_description}
    Trascrizione (se presente): {transcript or "Nessuna trascrizione"}

    Fornisci output in formato JSON con le seguenti chiavi:
    {{
      "mood": "descrizione del tono visivo (es. drammatico, ispirazionale, comico)",
      "music": "genere e ritmo consigliato (es. piano ambient, trap veloce, orchestrale)",
      "caption": "testo breve da sovrapporre al video",
      "fx": ["zoom_in", "color_boost", "fade_in"],
      "color": "tone o filtro consigliato (es. teal-orange, b/n, soft warm)"
    }}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_prompt}],
        temperature=0.8
    )

    raw_output = response.choices[0].message.content.strip()

    # tenta parsing in dizionario JSON
    import json
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return {"error": "invalid JSON", "raw": raw_output}
