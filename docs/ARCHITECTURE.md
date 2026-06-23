# FarmaciaAI — Arquitectura del Sistema

## Diagrama

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIOS                                  │
│                                                                  │
│   📱 WhatsApp           🌐 Web Browser                          │
│   (foto, audio, texto)  (farmacia-ai.streamlit.app)             │
└──────────┬──────────────────────────┬───────────────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────┐      ┌───────────────────────┐
│  Baileys Gateway │      │   Streamlit Frontend  │
│  (Node.js)       │      │   (Python)            │
│                  │      │                       │
│  • Whitelist     │      │  • Demo Chat          │
│  • Anti-spam     │      │  • Comparar Precios   │
│  • Rate limiting │      │  • Riesgo Diabetes    │
│  • Audio/Foto    │      │  • Roadmap IA         │
└────────┬─────────┘      └──────────┬────────────┘
         │  HTTP POST                │  Direct import
         ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Python)                       │
│                                                                  │
│  POST /whatsapp/webhook                                          │
│    ├── Security (validate_phone, rate_limit, injection check)    │
│    ├── Session management (freemium 3 gratis → suscripción)     │
│    ├── Onboarding (edad, género)                                 │
│    ├── Intent classifier                                         │
│    │     Capa 1: Determinista (keywords/regex) — gratis, <1ms   │
│    │     Capa 2: DeepSeek V3 — solo si falla capa 1             │
│    └── OCR Pipeline                                              │
│          ├── Gemini Vision 1.5 Flash (imagen → JSON)            │
│          ├── DIGEMID validation (18,364 productos)               │
│          └── buscar_precio_farmacia() + Google Maps link         │
│                                                                  │
│  GET  /farmacias          → lista con precios                    │
│  GET  /medicamentos       → catálogo 20 genéricos               │
│  POST /riesgo             → FINDRISC score                       │
│  POST /ocr-boleta         → OCR directo (Streamlit)             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
         ┌─────────────────────┼──────────────────────┐
         ▼                     ▼                      ▼
┌────────────────┐  ┌─────────────────┐  ┌──────────────────────┐
│ Gemini Vision  │  │  DeepSeek V3    │  │  DIGEMID Catálogo    │
│ (Google AI)    │  │  (clasificador) │  │  18,364 productos    │
│                │  │                 │  │  data/digemid_       │
│ OCR recetas    │  │ Intent: mapa,   │  │  index.json          │
│ manuscritas    │  │ riesgo, precio  │  │  (MINSA, jun 2026)   │
│ $0.0015/img   │  │ $0.001/query    │  └──────────────────────┘
└────────────────┘  └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Datos (data/)                                  │
│                                                                  │
│  farmacias_lima.json   → 15 farmacias, 10 meds c/u, coordenadas │
│  medicamentos.json     → 20 genéricos con precios marca/genérico │
│  digemid_index.json    → 18,364 productos DIGEMID (19/06/2026)  │
│  sessions/             → sesiones por usuario (freemium state)   │
└─────────────────────────────────────────────────────────────────┘
```

## Stack tecnológico

| Capa | Tecnología | Por qué |
|---|---|---|
| WhatsApp gateway | Baileys v7 (Node.js) | OpenClaw pattern — Lectura 15 |
| Backend API | FastAPI (Python 3.11) | Async, tipado, rápido |
| OCR visión | Gemini Vision 1.5 Flash | Mejor calidad en recetas manuscritas en español |
| Clasificador intents | DeepSeek V3 | 40x más barato que GPT-4, español peruano |
| Mapa interactivo | Folium + streamlit-folium | Lecturas 3-7 del curso |
| Test de diabetes | FINDRISC (OMS) | Validado, sin análisis de sangre |
| Catálogo medicamentos | DIGEMID oficial | Fuente: MINSA Perú, actualizado diario |
| Frontend web | Streamlit | Rápido de iterar, deploy gratuito |
| Deploy | Docker (local) + Streamlit Cloud | |

## Flujo principal de usuario

```
Usuario manda foto de receta por WhatsApp
         ↓
Baileys descarga imagen → POST /whatsapp/webhook
         ↓
Security check (rate limit, phone validation)
         ↓
Freemium gate (3 gratis → pide código o suscripción)
         ↓
Gemini Vision extrae medicamentos del JSON
         ↓
DIGEMID valida nombres (18k productos reales)
         ↓
buscar_precio_farmacia() compara precios por unidad
         ↓
Respuesta WhatsApp:
  "1. Metformina 500mg
      ⏰ 2 veces al día  📦 30 tabletas
   💰 S/0.35/tableta en Boticas y Salud
   📍 Av. San Luis 2050, San Borja
   🗺️ [Google Maps link]"
```
