"""
Clasificador híbrido de intents para WhatsApp.

Capa 1 — Determinista: keywords exactos + regex. Gratis, <1ms.
Capa 2 — DeepSeek: solo si capa 1 no alcanza confianza mínima.
"""

import os
import json
import re
import asyncio
from openai import AsyncOpenAI

# ── Intents disponibles ───────────────────────────────────────────────────────

INTENT_RESPONSES = {
    "saludo": (
        "👋 ¡Hola! Soy *SaludApp*, tu asistente de salud en Lima 💊\n\n"
        "Puedo ayudarte con:\n"
        "📸 *Foto de receta* → te digo dónde comprar más barato\n"
        "🎤 *Audio* → describime el medicamento que buscás\n"
        "📊 *RIESGO* → calculá tu riesgo de diabetes\n"
        "🗺️ *MAPA* → farmacias cercanas con precios\n"
        "📄 *REPORTE* → descargá tu informe en PDF\n\n"
        "¿Empezamos? Mandame una foto de tu receta o contame qué necesitás 🙌"
    ),
    "mapa":   "🗺️ Mapa de farmacias y precios: https://saludapp-peru.streamlit.app (tab Precios)",
    "riesgo": "📊 Calculá tu riesgo de diabetes: https://saludapp-peru.streamlit.app (tab Riesgo)",
    "reporte":"📄 Descargá tu reporte PDF: https://saludapp-peru.streamlit.app (tab Riesgo → descargar PDF)",
    "recordatorios": "✅ Recordatorios activados. Te voy a avisar cada día con tus medicamentos.",
    "familiar": "👨‍👩‍👧 Plan Familiar: 7 días gratis, luego S/11.90/mes. ¿Cuál es el WhatsApp de tu familiar?",
    "receta": "📸 ¡Perfecto! Mandame la foto de la receta y la proceso.",
    "precio": "💊 ¿De qué medicamento querés el precio? Mandame la foto de la receta o el nombre exacto.",
    "ayuda":  "🆘 Puedo ayudarte con:\n• Foto de receta → precios en farmacias\n• MAPA → farmacias cerca\n• RIESGO → test de diabetes\n• REPORTE → PDF de tu salud\n• FAMILIAR → plan familiar",
    "gracias": "😊 ¡De nada! ¿Necesitás algo más?",
    "otro":   "No entendí bien. Escribí AYUDA para ver qué puedo hacer, o mandame una foto de tu receta.",
}

# ── Capa 1: Determinista ──────────────────────────────────────────────────────

# Matches exactos (confianza 1.0)
_EXACT: dict[str, str] = {
    "1": "recordatorios", "2": "mapa", "3": "riesgo", "4": "reporte",
    "hola": "saludo", "hi": "saludo", "buenas": "saludo",
    "buenos dias": "saludo", "buenas tardes": "saludo", "buenas noches": "saludo",
    "mapa": "mapa", "farmacias": "mapa",
    "riesgo": "riesgo", "diabetes": "riesgo",
    "reporte": "reporte", "pdf": "reporte", "informe": "reporte",
    "recordatorios": "recordatorios", "recordatorio": "recordatorios",
    "familiar": "familiar", "alertas": "familiar",
    "ayuda": "ayuda", "help": "ayuda", "menu": "ayuda",
    "gracias": "gracias", "gracias!": "gracias", "ty": "gracias",
}

# Patrones regex (confianza 0.9)
_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(hola|buenas|saludos|hey|ey)\b", re.I), "saludo"),
    (re.compile(r"\b(gracias|thank|thx|genial|perfecto|excelente)\b", re.I), "gracias"),
    (re.compile(r"\b(farmacia|donde comprar|precio|barato|m[aá]s barato)\b", re.I), "mapa"),
    (re.compile(r"\b(riesgo|diabetes|glucosa|az[uú]car|insulina)\b", re.I), "riesgo"),
    (re.compile(r"\b(reporte|pdf|descargar|informe)\b", re.I), "reporte"),
    (re.compile(r"\b(recordatorio|recordar|aviso|notificaci[oó]n|alarma)\b", re.I), "recordatorios"),
    (re.compile(r"\b(familiar|familia|plan|hijo|esposa|mamá|papa)\b", re.I), "familiar"),
    (re.compile(r"\b(receta|medicamento|pastilla|medicina|f[aá]rmaco|c[aá]psula)\b", re.I), "receta"),
    (re.compile(r"\b(ayuda|help|qu[eé] pod[eé]s|qu[eé] hac[eé]s|menu)\b", re.I), "ayuda"),
]

def classify_deterministic(text: str) -> tuple[str | None, float]:
    """
    Retorna (intent, confidence) o (None, 0.0).
    Confidence 1.0 = match exacto, 0.9 = regex.
    """
    normalized = text.strip().lower()

    if normalized in _EXACT:
        return _EXACT[normalized], 1.0

    for pattern, intent in _PATTERNS:
        if pattern.search(normalized):
            return intent, 0.9

    return None, 0.0


# ── Capa 2: DeepSeek ─────────────────────────────────────────────────────────

_DEEPSEEK_INTENTS = list(INTENT_RESPONSES.keys())
_SYSTEM_PROMPT = f"""Eres un clasificador de intents para un bot de salud en WhatsApp (Perú).
Clasifica el mensaje del usuario en uno de estos intents: {", ".join(_DEEPSEEK_INTENTS)}.

Reglas:
- Si menciona receta, pastilla, medicamento, foto de receta → "receta"
- Si saluda → "saludo"
- Si pregunta precios o farmacias → "precio" o "mapa"
- Si no encaja en ninguno → "otro"

Responde SOLO con JSON válido, sin markdown:
{{"intent": "<intent>", "confidence": <0.0-1.0>}}"""


async def classify_deepseek(text: str) -> tuple[str, float]:
    """Llama a DeepSeek para clasificar el intent. Retorna (intent, confidence)."""
    from app.security import safe_user_content, is_injection

    # Bloquear injection antes de llegar al LLM
    if is_injection(text):
        return "otro", 1.0

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return "otro", 0.0

    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
    )

    try:
        resp = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": safe_user_content(text)},
            ],
            temperature=0.0,
            max_tokens=60,
        )
        raw = resp.choices[0].message.content.strip()
        data = json.loads(raw)
        intent = data.get("intent", "otro")
        confidence = float(data.get("confidence", 0.5))
        if intent not in INTENT_RESPONSES:
            intent = "otro"
        return intent, confidence
    except Exception:
        return "otro", 0.0


# ── Clasificador híbrido principal ────────────────────────────────────────────

DETERMINISTIC_THRESHOLD = 0.85

async def classify_intent(text: str) -> tuple[str, float, str]:
    """
    Retorna (intent, confidence, source).
    source = "deterministic" | "deepseek"
    """
    intent, conf = classify_deterministic(text)
    if intent and conf >= DETERMINISTIC_THRESHOLD:
        return intent, conf, "deterministic"

    intent, conf = await classify_deepseek(text)
    return intent, conf, "deepseek"


def intent_to_response(intent: str) -> str:
    return INTENT_RESPONSES.get(intent, INTENT_RESPONSES["otro"])
