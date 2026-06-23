"""SaludApp Peru — FastAPI Backend"""
import os
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from app.health_models import RiskModel, FindriscInput

app = FastAPI(title="SaludApp Peru API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


# ── Schemas ──────────────────────────────────────────────────────────────────

class FindriscPayload(BaseModel):
    edad: str
    imc: str
    sexo: str = "M"
    cintura_hombre: Optional[str] = None
    cintura_mujer: Optional[str] = None
    actividad_fisica: bool = True
    frutas_verduras_diario: bool = True
    medicacion_hipertension: bool = False
    glucosa_alta_antes: bool = False
    familiar_diabetes: str = "ninguno"


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "SaludApp Peru API",
        "endpoints": [
            "GET  /farmacias",
            "GET  /medicamentos",
            "GET  /farmacias/precio/{med_id}",
            "POST /riesgo",
            "POST /ocr-boleta",
            "POST /recordatorios",
        ]
    }


@app.get("/farmacias")
def get_farmacias():
    path = DATA_DIR / "farmacias_lima.json"
    if not path.exists():
        raise HTTPException(404, "farmacias_lima.json not found")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/medicamentos")
def get_medicamentos():
    path = DATA_DIR / "medicamentos.json"
    if not path.exists():
        raise HTTPException(404, "medicamentos.json not found")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/farmacias/precio/{med_id}")
def get_precio(med_id: str):
    from ai.health_agents import buscar_precio_farmacia
    farmacias_path = DATA_DIR / "farmacias_lima.json"
    if not farmacias_path.exists():
        raise HTTPException(404)
    farmacias = json.loads(farmacias_path.read_text(encoding="utf-8"))
    return buscar_precio_farmacia(med_id, farmacias)


@app.post("/riesgo")
def assess_risk(payload: FindriscPayload):
    inp = FindriscInput(
        edad=payload.edad,
        imc=payload.imc,
        sexo=payload.sexo,
        cintura_hombre=payload.cintura_hombre,
        cintura_mujer=payload.cintura_mujer,
        actividad_fisica=payload.actividad_fisica,
        frutas_verduras_diario=payload.frutas_verduras_diario,
        medicacion_hipertension=payload.medicacion_hipertension,
        glucosa_alta_antes=payload.glucosa_alta_antes,
        familiar_diabetes=payload.familiar_diabetes,
    )
    result = RiskModel().assess(inp)
    return {
        "score": result.score,
        "nivel": result.nivel,
        "color": result.color,
        "riesgo_porcentaje": result.riesgo_porcentaje,
        "recomendacion": result.recomendacion,
        "siguiente_paso": result.siguiente_paso,
        "delphi_disponible": result.delphi_disponible,
    }


@app.post("/ocr-boleta")
async def ocr_boleta(file: UploadFile = File(...)):
    from ai.health_agents import extract_medicines_from_image
    image_bytes = await file.read()
    ext = (file.filename or "img.jpg").rsplit(".", 1)[-1].lower()
    img_type = "jpeg" if ext in ("jpg", "jpeg") else ext
    result = extract_medicines_from_image(image_bytes, img_type)
    return result


@app.post("/recordatorios")
def generate_reminders(data: dict):
    from ai.health_agents import generar_calendario_recordatorios
    meds = data.get("medicamentos", [])
    fecha = data.get("fecha_inicio", "2026-06-21")
    return generar_calendario_recordatorios(meds, fecha)


# ── WhatsApp Webhook ──────────────────────────────────────────────────────
from pydantic import BaseModel as PB
from typing import Literal

AUDIO_LIMIT_FREE = 60    # segundos
AUDIO_LIMIT_PAID = 600   # segundos

class WhatsAppMessage(PB):
    from_number: str
    text: str | None = None
    image_base64: str | None = None
    image_type: str = "jpeg"
    audio_base64: str | None = None
    audio_duration_seconds: int = 0


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(msg: WhatsAppMessage):
    import base64
    from app.whatsapp_intent import classify_intent, intent_to_response
    from app.user_session import (
        get_session, save_session, is_allowed, record_consultation,
        remaining_free, unlock, gate_message, unlock_message,
        handle_onboard_input, start_onboarding, onboard_prompt, UNLOCK_CODE, RESET_CODE,
        FREE_CONSULTATIONS,
    )
    from app.security import rate_limit_ok, validate_phone, sanitize_text, is_injection

    # ── 0. Seguridad de entrada ───────────────────────────────────────────────
    if not validate_phone(msg.from_number):
        return {"response": "", "medicamentos": [], "_debug": {"intent": "blocked_phone"}}

    if not rate_limit_ok(msg.from_number):
        return {"response": "⏳ Demasiados mensajes. Esperá un momento.", "medicamentos": [],
                "_debug": {"intent": "rate_limited"}}

    if msg.text:
        msg = msg.model_copy(update={"text": sanitize_text(msg.text)})
        if is_injection(msg.text):
            return {"response": "No entendí ese mensaje. Mandame una foto de tu receta o escribí AYUDA.",
                    "medicamentos": [], "_debug": {"intent": "blocked_injection"}}

    session = get_session(msg.from_number)
    response_text = ""
    medicamentos = []
    intent_used = "unknown"
    intent_source = "deterministic"

    # ── 1. Onboarding en curso → solo si no es un comando de navegación ──────
    _NAV_COMMANDS = {"mapa","riesgo","reporte","recordatorios","familiar","ayuda",
                     "precios","precio","hola","saludo","1","2","3","4"}
    if session.get("onboard_step") and session["onboard_step"] not in (None, "done"):
        if msg.text and msg.text.strip().lower() not in _NAV_COMMANDS:
            resp = handle_onboard_input(session, msg.text)
            if resp:
                return {"response": resp, "medicamentos": [], "_debug": {"intent": "onboarding"}}

    # ── 2. Comandos especiales ────────────────────────────────────────────
    if msg.text:
        cmd = msg.text.strip().lower()
        if cmd == UNLOCK_CODE:
            unlock(session)
            save_session(session)
            return {"response": unlock_message(), "medicamentos": [], "_debug": {"intent": "unlock"}}
        if cmd == RESET_CODE:
            from app.user_session import reset_consultations
            reset_consultations(session)
            save_session(session)
            return {"response": f"🔄 Consultas reiniciadas. Tenés {FREE_CONSULTATIONS} consultas gratis de nuevo.",
                    "medicamentos": [], "_debug": {"intent": "reset"}}

    # ── 3. Gate freemium ──────────────────────────────────────────────────
    if not is_allowed(session):
        return {"response": gate_message(session), "medicamentos": [], "_debug": {"intent": "gate"}}

    # ── 4. Audio → validar duración → transcribir con Gemini ─────────────
    if msg.audio_base64 and not msg.text:
        limit = AUDIO_LIMIT_PAID if session["unlocked"] else AUDIO_LIMIT_FREE
        if msg.audio_duration_seconds > limit:
            mins = limit // 60
            msg_limit = (
                f"🎤 Audio demasiado largo. "
                f"{'Suscribite para audios de hasta 10 minutos.' if not session['unlocked'] else 'Máximo 10 minutos.'}\n"
                f"Límite actual: {mins} minuto{'s' if mins > 1 else ''}."
            )
            return {"response": msg_limit, "medicamentos": [], "_debug": {"intent": "audio_too_long"}}
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
            audio_bytes = base64.b64decode(msg.audio_base64)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content([
                "Transcribí este audio en español. Solo el texto, sin comentarios adicionales.",
                {"mime_type": "audio/ogg", "data": audio_bytes},
            ])
            msg = msg.model_copy(update={"text": resp.text.strip()})
            intent_used = "audio_transcribed"
        except Exception as e:
            return {"response": "🎤 No pude procesar el audio. ¿Podés escribirme qué medicamento buscás?",
                    "medicamentos": [], "_debug": {"intent": "audio_error", "error": str(e)}}

    # ── 5. Imagen → OCR ───────────────────────────────────────────────────
    if msg.image_base64:
        img_bytes = base64.b64decode(msg.image_base64)
        from ai.health_agents import extract_medicines_from_image
        result = extract_medicines_from_image(img_bytes, msg.image_type)
        medicamentos = result.get("medicamentos", [])
        intent_used = "image_ocr"
        intent_source = "deterministic"

        if medicamentos:
            response_text = f"💊 *{len(medicamentos)} medicamento(s) en tu receta:*\n\n"
            for i, m in enumerate(medicamentos[:5], 1):
                nombre = m.get("nombre", "?")
                dosis = f" {m['dosis']}" if m.get("dosis") else ""
                frec  = f"\n   ⏰ {m['frecuencia']}" if m.get("frecuencia") else ""
                cant  = f"\n   ctd. {m['cantidad']}" if m.get("cantidad") else ""
                response_text += f"{i}. *{nombre}*{dosis}{frec}{cant}\n"

            # Basket: qué farmacia tiene más medicamentos juntos (precio+distancia)
            from ai.health_agents import buscar_precio_farmacia, fuzzy_med_id
            from collections import defaultdict
            meds_catalog  = json.loads((DATA_DIR / "medicamentos.json").read_text(encoding="utf-8"))["medicamentos"]
            farmacias_data = json.loads((DATA_DIR / "farmacias_lima.json").read_text(encoding="utf-8"))

            total_meds = min(len(medicamentos), 3)
            pharmacy_basket = defaultdict(lambda: {"meds": [], "total_efectivo": 0.0, "total_precio": 0.0, "info": None})
            meds_sin_precio = []

            for m in medicamentos[:3]:
                nombre_m = m.get("nombre", "?")
                med_id   = fuzzy_med_id(nombre_m, meds_catalog)
                precios  = buscar_precio_farmacia(med_id, farmacias_data, max_km=15.0)
                cat_info = next((x for x in meds_catalog if x["id"] == med_id), None)
                unidad   = cat_info.get("presentacion", "unidad").lower() if cat_info else "unidad"
                if not precios:
                    meds_sin_precio.append(nombre_m)
                    continue
                for p in precios:
                    fid = p["farmacia_id"]
                    pharmacy_basket[fid]["meds"].append(
                        {"nombre": nombre_m, "precio": p["precio"], "unidad": unidad}
                    )
                    pharmacy_basket[fid]["total_efectivo"] += p["precio_efectivo"]
                    pharmacy_basket[fid]["total_precio"]   += p["precio"]
                    if pharmacy_basket[fid]["info"] is None:
                        pharmacy_basket[fid]["info"] = p

            sorted_baskets = sorted(
                pharmacy_basket.items(),
                key=lambda x: (-len(x[1]["meds"]), x[1]["total_efectivo"])
            )

            if sorted_baskets:
                # ── 1 recomendación clara + 1 backup (no más — paradoja de elección) ──
                best_fid, best = sorted_baskets[0]
                info    = best["info"]
                dist_km = info.get("dist_km", 0)
                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={info['lat']},{info['lng']}"
                count   = len(best["meds"])

                response_text += f"\n✅ *Te recomendamos ir a:*\n"
                response_text += f"*{info['nombre']}* — {dist_km:.1f} km\n"
                for med in best["meds"]:
                    response_text += f"   • {med['nombre']}: S/{med['precio']:.2f}/{med['unidad']}\n"
                response_text += (
                    f"   💰 Total: S/{best['total_precio']:.2f} ({count}/{total_meds} meds)\n"
                    f"   📮 {info.get('direccion', '')}\n"
                    f"   🗺️ {maps_url}\n"
                )

                if len(sorted_baskets) > 1:
                    alt_fid, alt = sorted_baskets[1]
                    alt_info = alt["info"]
                    alt_maps = f"https://www.google.com/maps/dir/?api=1&destination={alt_info['lat']},{alt_info['lng']}"
                    response_text += (
                        f"\n_Si no tiene stock:_ {alt_info['nombre']} "
                        f"({alt_info.get('dist_km',0):.1f} km) — "
                        f"S/{alt['total_precio']:.2f} · {alt_maps}\n"
                    )

                if meds_sin_precio:
                    response_text += f"\n⚠️ Sin precio: {', '.join(meds_sin_precio)}\n"
            else:
                response_text += (
                    "\n⚠️ Estos medicamentos no están en nuestro catálogo de precios.\n"
                    "Buscá precios en:\n"
                    "🌐 https://farmacia-ai.streamlit.app\n"
                    "📋 https://www.digemid.minsa.gob.pe"
                )

            remaining = remaining_free(session) - 1
            if not session["unlocked"] and remaining > 0:
                response_text += f"\n\n_(Te quedan {remaining} consultas gratis)_"
            response_text += "\n\n¿Querés *RECORDATORIOS* para estas pastillas? Escribí SI."
        else:
            response_text = "❌ No pude leer la receta. ¿Podés mandar otra foto con mejor luz?"

        record_consultation(session)
        save_session(session)

        # Onboarding tras primera consulta
        if session["free_consultations"] == 1 and not session["onboarded"]:
            response_text += "\n\n" + start_onboarding(session)

        return {"response": response_text,
                "medicamentos": [{"nombre": m.get("nombre"), "dosis": m.get("dosis"),
                                  "frecuencia": m.get("frecuencia")} for m in medicamentos],
                "_debug": {"intent": intent_used, "source": intent_source}}

    # ── 6. Texto → clasificador híbrido ──────────────────────────────────
    if msg.text:
        intent_used, confidence, intent_source = await classify_intent(msg.text)
        response_text = intent_to_response(intent_used)

        # Solo cobrar OCR real (imagen/audio) — texto es gratis
        NON_BILLABLE = {"saludo", "gracias", "ayuda", "mapa", "riesgo",
                        "reporte", "recordatorios", "familiar", "otro"}
        if intent_used not in NON_BILLABLE:
            record_consultation(session)
            save_session(session)
            remaining = remaining_free(session)
            if not session["unlocked"] and remaining > 0:
                response_text += f"\n\n_(Consultas gratis restantes: {remaining}/{FREE_CONSULTATIONS})_"
            # Onboarding tras primera consulta real
            if session["free_consultations"] == 1 and not session["onboarded"]:
                response_text += "\n\n" + start_onboarding(session)
        else:
            save_session(session)

    return {
        "response": response_text,
        "medicamentos": [],
        "_debug": {"intent": intent_used, "source": intent_source},
    }
