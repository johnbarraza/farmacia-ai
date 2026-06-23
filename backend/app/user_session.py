"""
Gestión de sesiones de usuario por WhatsApp.
Persiste en data/sessions/<phone_hash>.json
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

SESSIONS_DIR = Path(__file__).resolve().parents[2] / "data" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

import os
FREE_CONSULTATIONS = int(os.getenv("FREE_CONSULTATIONS", "3"))
UNLOCK_CODE = "homework-startup"
RESET_CODE  = "reset-demo"   # código secreto para reiniciar consultas en pruebas
SUBSCRIBE_URL = "https://farmacia-ai.streamlit.app"


def _path(phone: str) -> Path:
    h = hashlib.md5(phone.encode()).hexdigest()
    return SESSIONS_DIR / f"{h}.json"


def get_session(phone: str) -> dict:
    p = _path(phone)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {
        "phone": phone,
        "free_consultations": 0,
        "unlocked": False,
        "onboarded": False,
        "onboard_step": None,   # None | "ask_edad" | "ask_genero" | "done"
        "profile": {"nombre": None, "edad": None, "genero": None},
        "created_at": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat(),
    }


def save_session(session: dict) -> None:
    session["last_seen"] = datetime.now().isoformat()
    _path(session["phone"]).write_text(
        json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def is_free(session: dict) -> bool:
    return session["free_consultations"] < FREE_CONSULTATIONS


def is_allowed(session: dict) -> bool:
    return session["unlocked"] or is_free(session)


def record_consultation(session: dict) -> None:
    if not session["unlocked"]:
        session["free_consultations"] += 1


def remaining_free(session: dict) -> int:
    return max(0, FREE_CONSULTATIONS - session["free_consultations"])


def unlock(session: dict) -> None:
    session["unlocked"] = True


def reset_consultations(session: dict) -> None:
    """Reinicia el contador de consultas — solo para pruebas."""
    session["free_consultations"] = 0
    session["unlocked"] = False


def gate_message(session: dict) -> str:
    return (
        f"🔒 Usaste tus {FREE_CONSULTATIONS} consultas gratis.\n\n"
        f"¿Tenés un código de acceso? Escribilo.\n\n"
        f"O suscribite para acceso ilimitado:\n{SUBSCRIBE_URL}"
    )


def unlock_message() -> str:
    return (
        f"✅ ¡Código válido! Tenés acceso por ahora.\n\n"
        f"Para acceso ilimitado suscribite acá:\n{SUBSCRIBE_URL}\n\n"
        f"Seguí mandando fotos de recetas o preguntas 💊"
    )


# ── Onboarding ────────────────────────────────────────────────────────────────

def onboard_prompt(session: dict) -> str | None:
    """Retorna la siguiente pregunta de onboarding, o None si ya terminó."""
    step = session.get("onboard_step")
    if step is None:
        return None
    if step == "ask_edad":
        return "👋 Una pregunta rápida para personalizar tu experiencia:\n¿Cuántos años tenés? (escribí solo el número)"
    if step == "ask_genero":
        return "¿Sos hombre o mujer? (escribí *H* o *M*)"
    return None


def handle_onboard_input(session: dict, text: str) -> str | None:
    """
    Procesa respuesta de onboarding. Retorna mensaje de confirmación o None si no
    estamos en onboarding.
    """
    step = session.get("onboard_step")
    if step not in ("ask_edad", "ask_genero"):
        return None

    text = text.strip()

    if step == "ask_edad":
        if text.isdigit() and 1 <= int(text) <= 120:
            session["profile"]["edad"] = int(text)
            session["onboard_step"] = "ask_genero"
            save_session(session)
            return "¿Sos hombre o mujer? (escribí *H* o *M*)"
        else:
            return "Por favor escribí solo tu edad en números (ej: 35)"

    if step == "ask_genero":
        g = text.upper()
        if g in ("H", "M", "HOMBRE", "MUJER"):
            session["profile"]["genero"] = "M" if g in ("H", "HOMBRE") else "F"
            session["onboard_step"] = "done"
            session["onboarded"] = True
            save_session(session)
            edad = session["profile"]["edad"]
            genero_txt = "hombre" if session["profile"]["genero"] == "M" else "mujer"
            return (
                f"✅ Perfecto! {edad} años, {genero_txt}.\n\n"
                f"Ya tengo tu perfil guardado. Podés mandarme:\n"
                f"• 📸 Foto de receta → precios en farmacias\n"
                f"• 🎤 Audio describiendo tu medicamento\n"
                f"• MAPA · RIESGO · REPORTE · RECORDATORIOS"
            )
        else:
            return "Escribí *H* para hombre o *M* para mujer"

    return None


def start_onboarding(session: dict) -> str:
    """Inicia el onboarding después de la primera consulta."""
    session["onboard_step"] = "ask_edad"
    save_session(session)
    return (
        "👋 ¡Genial! Para darte mejores recomendaciones necesito dos datos rápidos.\n\n"
        "¿Cuántos años tenés? (escribí solo el número)"
    )
