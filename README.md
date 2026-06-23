# 💊 FarmaciaAI

**Encontrá el medicamento más barato cerca tuyo.** Bot de WhatsApp + web para pacientes crónicos en Lima, Perú.

🌐 **Demo:** [farmacia-ai.streamlit.app](https://farmacia-ai.streamlit.app) · 📱 **Bot WhatsApp:** +51 994 809 887

> Surgió como la idea ganadora (score 80/100) del torneo de validación de startups YC del repositorio **[hw7_ds](https://github.com/JohnxBar/hw7_ds)** — un pipeline de agentes que evalúa ideas usando la metodología de Y Combinator.

---

## ¿Qué hace?

| Función | Tecnología |
|---|---|
| Bot WhatsApp — recibe fotos, texto y audio | Baileys (Node.js) |
| OCR receta médica → medicamentos + precios | Gemini Vision |
| Clasificador de intents híbrido | Determinista + DeepSeek LLM |
| Audio → transcripción → respuesta | Gemini 1.5 Flash |
| Mapa farmacias + precios Lima | Folium |
| Score riesgo diabetes | FINDRISC (OMS) |
| Freemium: 3 consultas gratis → suscripción | Sesiones JSON por usuario |
| Onboarding conversacional (edad + género) | FastAPI + Baileys |
| Seguridad: rate limiting, prompt injection | `security.py` |
| UI web | Streamlit |

---

## Quick start

```bash
pip install -r frontend/requirements.txt
cp .env.example .env  # agregar GEMINI_API_KEY + DEEPSEEK_API_KEY
streamlit run frontend/app.py
```

## Deploy Docker (recomendado)

```bash
cp .env.example .env   # llenar keys
docker compose up --build
# Backend:   http://localhost:8000
# Frontend:  http://localhost:8501
# WhatsApp:  docker logs -f saludapp-baileys  (escanear QR)
```

---

## Roadmap modelos de riesgo

| Fase | Modelo | Datos necesarios |
|---|---|---|
| MVP | FINDRISC (8 preguntas) | Cero |
| 1K pac | XGBoost / Cox | 3 meses data |
| 5K pac | BEHRT / CLMBR (FEMR) | 6+ meses, ICD-10 |
| 10K pac | MOTOR time-to-event | 12+ meses, OMOP |
| 100K+ | Delphi-like propio | Años de datos peruanos |

---

## Origen

Idea validada con el pipeline de agentes YC de **[github.com/JohnxBar/hw7_ds](https://github.com/JohnxBar/hw7_ds)**.
El pipeline evaluó 16 ideas en un torneo bracket — SaludApp obtuvo 80/100 y fue seleccionada para desarrollo.

---

## Herramientas del Curso Usadas

> Curso: Data Science con Python 2026-I — Universidad del Pacífico

| Herramienta | Lectura | Dónde en el código |
|---|---|---|
| **Gemini Vision / PaddleOCR** | L14 — Document AI | `ai/health_agents.py` → `_gemini_extract()`, `_try_paddleocr()` |
| **Folium + mapas geoespaciales** | L3-7 — GIS | `frontend/app.py` → Tab Comparar Precios |
| **OpenClaw / Baileys (agente WhatsApp)** | L15 — OpenClaw | `ai/baileys_gateway.js` |
| **DeepSeek V3 (clasificador LLM)** | L10-11 — agentes crewAI | `backend/app/whatsapp_intent.py` → `classify_deepseek()` |
| **Claude Code** | L15 — agentes de código | Co-founder técnico virtual para todo el backend |

---

## Documentación

- [`docs/PITCH.md`](docs/PITCH.md) — Dossier YC completo (14 secciones)
- [`docs/PITCH_SCRIPT.md`](docs/PITCH_SCRIPT.md) — Script de pitch 7 minutos
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Diagrama de arquitectura
- [`docs/research/entrevistas.md`](docs/research/entrevistas.md) — 5 entrevistas con usuarios
- [`docs/research/validacion_mercado.md`](docs/research/validacion_mercado.md) — Validación de mercado

---

## Autor

John Svante Barraza Ratachi — UP Data Science 2026-I
