# 💊 FarmaciaAI

**Encontrá el medicamento más barato cerca tuyo.** Bot de WhatsApp + web para pacientes crónicos en Lima, Perú.

🌐 **Demo:** [farmacia-ai.streamlit.app](https://farmacia-ai.streamlit.app) · 📱 **Bot WhatsApp:** +51 994 809 887

> Surgió como la idea ganadora (score 80/100) del torneo de validación YC del repositorio **[hw7_ds](https://github.com/JohnxBar/hw7_ds)** — pipeline de agentes que evalúa ideas con metodología Y Combinator.

---

## Demo en vivo

| Canal | Link |
|---|---|
| Web | [farmacia-ai.streamlit.app](https://farmacia-ai.streamlit.app) |
| WhatsApp | +51 994 809 887 — manda foto de una receta |
| Pitch deck | [docs/expo/pitch_farmaciaai.pdf](docs/expo/pitch_farmaciaai.pdf) |
| Diagrama arquitectura | [docs/expo/arquitectura.html](docs/expo/arquitectura.html) |
| Video demo — Streamlit web | [Ver demo](https://drive.google.com/file/d/1U_8DdoHUw7ygSaYne7PW8aNfJZfpTuTP/view?usp=sharing) |
| Video demo — Bot WhatsApp | [Ver demo](https://drive.google.com/file/d/1QZCEkH6WNhgfwyndTMTcrpG1x8W50-pa/view?usp=sharing) |

---

## ¿Qué hace?

| Función | Tecnología |
|---|---|
| Bot WhatsApp — recibe fotos, texto y audio | Baileys (Node.js) |
| OCR receta médica → medicamentos + precios | Gemini Vision |
| Clasificador de intents híbrido | Determinista + DeepSeek V3 |
| Precio/unidad (tableta, cápsula) + caja 30u | Pandas |
| Mapa farmacias + precios Lima (15 distritos) | Folium |
| Score riesgo diabetes | FINDRISC (OMS) |
| Freemium: 3 consultas gratis → suscripción | Sesiones JSON por usuario |
| Seguridad: rate limiting, prompt injection | `security.py` |
| UI web | Streamlit |

---

## Herramientas del curso usadas

| Herramienta | Lectura | Dónde en el código |
|---|---|---|
| Gemini Vision — OCR de recetas | L14 | `backend/app/ocr.py` |
| Baileys / OpenClaw — bot WhatsApp | L15 | `whatsapp/bot.js` |
| DeepSeek V3 — clasificación intents | L10-11 | `backend/app/intent.py` |
| Folium + mapas GIS | L3-7 | `frontend/app.py` → tab Mapa |
| Claude Code — CTO virtual | L15 | todo el repo |

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

## Validación del problema

5 entrevistas con pacientes crónicos (diabéticos, hipertensos) realizadas entre el 12 y 20 de junio de 2026.
Ver `docs/research/entrevistas.md` para citas textuales y patrones comunes.

**Resultado clave:** 5/5 entrevistados no comparan precios; 5/5 usarían WhatsApp como canal.

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

## Desarrollo en 11 días — historial completo

El proyecto se construyó en dos repositorios. El trabajo comenzó en **[hw7_ds](https://github.com/JohnxBar/hw7_ds)** (validación y pipeline de agentes YC) y continuó en este repo (implementación del producto).

| Fecha | Repo | Hito |
|---|---|---|
| 12 Jun | [hw7_ds](https://github.com/JohnxBar/hw7_ds) | Pipeline de agentes YC — torneo de 16 ideas, FarmaciaAI gana con 80/100 |
| 13 Jun | [hw7_ds](https://github.com/JohnxBar/hw7_ds) | One-liner, problem statement, segmento de clientes |
| 14 Jun | Este repo / docs | Entrevista 1 (familiar directo, 68a, Lima) |
| 15 Jun | Este repo / docs | Entrevista 2 (diabético, Lima Norte) |
| 16 Jun | Este repo / docs | Entrevista 3 (hipertensa, Surquillo) |
| 18 Jun | Este repo / docs | Entrevista 4 (cuidadora UP) |
| 20 Jun | Este repo / docs | Entrevista 5 (ex-paciente SISMED, Lima Este) |
| 22 Jun | Este repo | MVP completo: bot WhatsApp + Streamlit + DIGEMID + deploy |

Las entrevistas tienen fecha explícita en [`docs/research/entrevistas.md`](docs/research/entrevistas.md).
El historial de commits de la fase de validación vive en [github.com/JohnxBar/hw7_ds](https://github.com/JohnxBar/hw7_ds).

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

John Svante Barraza Ratachi — Economía 9° ciclo, Universidad del Pacífico
Asistente de Investigación, CIUP · UP Data Science 2026-I
