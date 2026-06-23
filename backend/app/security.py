"""
Seguridad del bot WhatsApp: sanitización, detección de injection, rate limiting.
"""

import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timedelta

# ── Rate limiting (in-memory, suficiente para demo) ───────────────────────────

_buckets: dict[str, list[datetime]] = defaultdict(list)
RATE_WINDOW = timedelta(seconds=60)
RATE_MAX = 15  # mensajes por minuto por usuario


def rate_limit_ok(phone: str) -> bool:
    """True si el usuario puede enviar otro mensaje."""
    now = datetime.now()
    window_start = now - RATE_WINDOW
    _buckets[phone] = [t for t in _buckets[phone] if t > window_start]
    if len(_buckets[phone]) >= RATE_MAX:
        return False
    _buckets[phone].append(now)
    return True


# ── Sanitización de input ─────────────────────────────────────────────────────

MAX_TEXT_LEN = 500  # chars máximos aceptados

# Caracteres de control (excepto \n, \t)
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")

# Patrones de prompt injection comunes
_INJECTION_PATTERNS = re.compile(
    r"(ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|rules?|context))"
    r"|(system\s*:)"
    r"|(assistant\s*:)"
    r"|(you\s+are\s+now\s+(a\s+)?)"
    r"|(forget\s+(everything|all|your))"
    r"|(new\s+instructions?)"
    r"|(override\s+(all\s+)?(instructions?|rules?))"
    r"|(act\s+as\s+(if\s+you\s+are|a\s+))"
    r"|(pretend\s+(to\s+be|you\s+are))"
    r"|(jailbreak)"
    r"|(dan\s+mode)"
    r"|(\[INST\]|\[\/INST\]|<\|im_start\|>|<\|im_end\|>)",
    re.IGNORECASE,
)


def sanitize_text(text: str) -> str:
    """
    Limpia el texto del usuario:
    - Normaliza unicode
    - Elimina control chars
    - Trunca a MAX_TEXT_LEN
    """
    text = unicodedata.normalize("NFKC", text)
    text = _CTRL.sub("", text)
    text = text.strip()
    if len(text) > MAX_TEXT_LEN:
        text = text[:MAX_TEXT_LEN]
    return text


def is_injection(text: str) -> bool:
    """True si el texto parece un intento de prompt injection."""
    return bool(_INJECTION_PATTERNS.search(text))


def validate_phone(phone: str) -> bool:
    """Valida que el JID de WhatsApp tenga formato básico correcto."""
    # Acepta: @s.whatsapp.net (personal), @lid (multi-device LID), @g.us (grupos)
    return bool(re.match(r"^\d{7,20}(@s\.whatsapp\.net|@lid|@g\.us)$", phone))


# ── Wrapper seguro para texto hacia LLM ──────────────────────────────────────

def safe_user_content(text: str) -> str:
    """
    Envuelve el texto del usuario en delimitadores explícitos para el LLM.
    Reduce el riesgo de que el contenido escape al system prompt.
    """
    cleaned = sanitize_text(text)
    return f"<user_message>{cleaned}</user_message>"
