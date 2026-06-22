# 💊 SaludApp Peru

**Tu salud, tus datos.** App de salud personal para el paciente peruano.

## MVP

| Función | Tecnología |
|---|---|
| OCR boleta → medicamentos | Gemini Vision / PaddleOCR |
| Recordatorios de pastillas | Lógica Python |
| Mapa farmacias + precios | Folium |
| Score riesgo diabetes | FINDRISC (OMS) |
| UI | Streamlit |

## Quick start

```bash
pip install -r frontend/requirements.txt
cp .env.example .env  # agregar API keys
streamlit run frontend/app.py
```

## Deploy

```bash
docker compose up -d --build
# → http://localhost:8501
```

## Roadmap modelos de riesgo

| Fase | Modelo | Datos necesarios |
|---|---|---|
| MVP | FINDRISC (8 preguntas) | Cero |
| 1K pac | XGBoost / Cox | 3 meses data |
| 5K pac | BEHRT / CLMBR (FEMR) | 6+ meses, ICD-10 |
| 10K pac | MOTOR time-to-event | 12+ meses, OMOP |
| 100K+ | Delphi-like propio | Años de datos peruanos |

## Autor

John Svante Barraza Ratachi — UP Data Science 2026-I
