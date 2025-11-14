import subprocess
import json
import re
from typing import Dict, Any


def extract_json_block(raw: str) -> str:
    """
    Estrae il primo blocco JSON valido da un output LLM.
    Gestisce casi con testo prima e dopo.
    """
    # Cerca un blocco {...}
    match = re.search(r"\{(?:.|\n)*\}", raw)
    if match:
        return match.group(0)
    return raw.strip()


def validate_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Garantisce che il piano di editing contenga tutte le chiavi richieste.
    Inserisce fallback sicuri.
    """
    return {
        "mood": plan.get("mood", "cinematic"),
        "music": plan.get("music", "ambient piano"),
        "caption": plan.get("caption", "Generated with CineEdit-AI"),
        "fx": plan.get("fx", ["fade_in"]),
        "color": plan.get("color", "soft warm")
    }


def generate_edit_plan(scene_description: str, transcript: str | None = None) -> dict:
    """
    Genera un piano di montaggio professionale usando Ollama in locale.
    Compatibile con run_in_executor.
    """

    prompt = f"""
You are a senior cinematic video editor.
Your task is to generate a professional editing plan for a short emotional video.

=============================
SCENE DESCRIPTION
=============================
{scene_description}

=============================
TRANSCRIPT
=============================
{transcript or "No transcript available"}

=============================
REQUIRED OUTPUT FORMAT
=============================

Return **ONLY** a JSON object with these exact keys:

{{
    "mood": "string describing the emotional tone",
    "music": "suggested genre and rhythm",
    "caption": "short overlay text",
    "fx": ["zoom_in", "color_boost", "fade_in"],
    "color": "cinematic color tone"
}}

DO NOT add explanations.
DO NOT include markdown.
Output pure JSON.
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3:70b", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    except Exception as e:
        return {"error": f"Ollama execution failed: {e}"}

    raw_output = result.stdout.strip()

    # Pulisci l'output
    cleaned = extract_json_block(raw_output)

    try:
        parsed = json.loads(cleaned)
        return validate_plan(parsed)

    except Exception:
        return {
            "error": "Failed to parse JSON",
            "raw_output": raw_output,
            "cleaned": cleaned
        }
