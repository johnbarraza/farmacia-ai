# 💊 SaludApp Peru

**Tu salud, tus datos.** Asistente de salud personal para el paciente peruano vía WhatsApp y web.

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

## Autor

John Svante Barraza Ratachi — UP Data Science 2026-I
