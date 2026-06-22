# SaludApp Peru — Planning Document
## Proyecto Final · Data Science con Python 2026-I · UP

**Founder:** John Svante Barraza Ratachi  
**Presentación:** Martes 23 junio 2026 · 09:05 AM  
**Idea core:** App de salud personal donde el paciente peruano es dueño de sus propios datos.

---

## 1. Problema

En Perú no existe un sistema de "open health". El paciente llega al médico sin historial, guarda
sus boletas de farmacia en una bolsa de plástico, y no sabe cuánto paga de más vs. el genérico
equivalente a 200 metros. Las EPS no comparten datos con el paciente.

**Usuarios objetivo (MVP):** Pacientes crónicos (diabetes, hipertensión) en Lima que compran
medicamentos mensualmente.

**Dolor cuantificado:**
- Medicamento de marca vs. genérico: hasta 80% más caro sin saberlo
- Pastillas olvidadas: ~50% adherencia en enfermedades crónicas en LATAM (OPS 2023)
- Sin historial propio: cada médico nuevo empieza de cero

---

## 2. Solución MVP (lo que se entrega el 23 jun)

```
Flujo principal (demo 3 min):
  1. Usuario sube foto de boleta de farmacia
  2. PaddleOCR + Claude AI extrae medicamentos, dosis, frecuencia
  3. App genera calendario de recordatorios de pastillas
  4. Mapa Folium muestra farmacias cercanas con precios reales
  5. Cuestionario FINDRISC → score de riesgo de diabetes T2
```

---

## 3. Arquitectura

```
SaludApp Peru
├── frontend/
│   └── salud_app.py          ← Streamlit (4 tabs)
├── backend/
│   └── app/
│       ├── main.py           ← FastAPI (endpoints salud + minería legacy)
│       └── health_models.py  ← FINDRISC ahora / slot para Delphi futuro
├── ai/
│   ├── agents.py             ← legacy MineAssist (mantener como evidencia de trabajo previo)
│   └── health_agents.py      ← OCR boleta (Claude Vision + PaddleOCR fallback)
├── data/
│   ├── farmacias_lima.json   ← 20 farmacias Lima con coords y precios demo
│   ├── medicamentos.json     ← 50 medicamentos genéricos DIGEMID con precios
│   ├── cwru_bearing_small.csv← legacy (mantener)
│   └── machine_telemetry.csv ← legacy (mantener)
└── docs/
    ├── PLANNING.md           ← este archivo
    └── pitch_deck.pdf        ← (a crear)
```

---

## 4. Herramientas del curso usadas (≥2 obligatorio)

| # | Herramienta | Lectura | Dónde en el código |
|---|---|---|---|
| 1 | **PaddleOCR + Claude AI** | Lectura 14 | `ai/health_agents.py` → extrae texto de boleta |
| 2 | **Folium / GeoPandas** | Lecturas 3-7 | `frontend/salud_app.py` Tab 2 → mapa farmacias |
| 3 | **Streamlit** | Lecturas 3-7 | `frontend/salud_app.py` → toda la UI |
| 4 | **LLMs (Claude API)** | Lectura 9 | `ai/health_agents.py` → extracción estructurada |
| 5 | **crewAI / Agentes** | Lectura 10-11 | `ai/health_agents.py` → agente de búsqueda de precios |

---

## 5. Modelo de negocio (pitch)

| Plan | Precio | Para quién |
|---|---|---|
| Gratuito | S/0 | Usuario final — accede a todo |
| EPS Insights | S/2,000/mes | EPS (Rímac, Pacífico) — dashboard de adherencia de afiliados |
| Farmacia Partner | S/500/mes | Farmacias — listing destacado en el mapa + leads derivados |

**Contribution margin:** Costo LLM ~$0.01/OCR · Costo almacenamiento ~$0.002/usuario/mes → margen >95%

---

## 6. Estado actual de los repos EHR

Ninguno está integrado al MVP — se necesita data longitudinal primero.
SaludApp ES el generador de esa data.

| Repo | Estado | Cuándo usarlo | Qué necesita |
|---|---|---|---|
| **FINDRISC** | ✅ Integrado | AHORA — MVP | Cero data. 8 preguntas. |
| **XGBoost / Cox** | 📋 Planeado | ~1K pac, 3 meses | Features tabulares de la app |
| **BEHRT** (deepmind) | 📋 Planeado | ~5K pac, 6+ meses | Secuencias ICD-10 |
| **FEMR + CLMBR** (Shahlab) | 📋 Planeado | ~5K pac, 6+ meses | OMOP-CDM |
| **FEMR + MOTOR** | 📋 Planeado | ~10K pac, 12+ meses | Time-to-event labels |
| **Delphi** (gerstung-lab) | 📋 Planeado | ~100K pac | Arquitectura GPT-2 replicable, NO usar pesos UK Biobank |

## 7. Wearables — Apple Watch / Google Watch

APIs disponibles HOY. Se agregan en fase de datos (no MVP).

| Plataforma | API | Datos | Integración |
|---|---|---|---|
| Apple Watch | HealthKit (iOS) | FC, ECG, SpO2, sueño, pasos, AFib | Autorización del usuario en iPhone |
| Wear OS / Fitbit | Health Connect (Android) | FC, pasos, sueño, actividad | Permiso en app Android |

**Valor para el modelo:**
- FC en reposo + variabilidad → predictor de riesgo cardiovascular
- Patrones de sueño → correlación con diabetes/HTA
- Activity rings → adherencia a recomendación médica
- ECG (Apple Watch) → detección temprana de fibrilación atrial

**Roadmap wearables:**
- Fase 2 (~1K pac): HealthKit + Health Connect como fuente opcional de datos
- Fase 3 (~5K pac): features de wearable alimentan BEHRT/CLMBR
- Fase 4: alertas en tiempo real desde watch ("tu FC sugiere que no tomaste la pastilla")

## 8. Roadmap (para el pitch)

| Fase | Hito | Fecha |
|---|---|---|
| **MVP** | OCR boleta + mapa farmacias + FINDRISC deployado | Jun 2026 |
| **Beta** | 100 usuarios activos con 30 días de data cada uno | Sep 2026 |
| **Data Layer** | 10K pacientes → dataset longitudinal propio peruano | Mar 2027 |
| **Delphi Peru** | Transformer de riesgo entrenado en data peruana (reemplaza FINDRISC) | Jun 2027 |
| **B2B** | 1er contrato EPS firmado con dashboard de adherencia | Sep 2027 |

---

## 7. Slot de integración Delphi (diseño técnico)

El modelo de riesgo está abstraído en `backend/app/health_models.py`:

```python
class RiskModel:
    """
    Interfaz de predicción de riesgo crónico.
    
    MVP 2026:  FINDRISC (8 preguntas → score 0-26 → riesgo diabetes T2)
    Futuro:    Delphi-style transformer sobre historial longitudinal peruano
               - Input: secuencia de eventos ICD-10 del paciente
               - Output: probabilidad de diabetes T2, HTA, anemia en 12 meses
               - Datos de entrenamiento: acumulados por esta misma app
    
    Para hacer el swap: reemplazar el método `assess()` sin cambiar la API.
    """
    def assess(self, patient_data: dict) -> dict:
        ...
```

El endpoint FastAPI `/riesgo` recibe `patient_data` y llama `RiskModel().assess()`.
Cuando Delphi esté listo, solo se cambia el interior de `assess()`. El frontend no cambia.

---

## 8. Stack de deploy

- **Frontend:** Streamlit Community Cloud (gratis, URL pública instantánea)
- **Backend:** Render.com free tier (FastAPI, wake-up ~30s para demo)
- **DB:** SQLite local en Streamlit (session state para MVP), PostgreSQL en producción
- **Modelos:** Claude API (Anthropic) para OCR + extracción

---

## 9. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| Regulatorio: Ley 29733 datos de salud | Anonimización desde ingesta, consentimiento explícito en onboarding |
| Técnico: PaddleOCR falla en boleta peruana | Fallback a Claude Vision directamente (más robusto) |
| Mercado: EPS no pagan por insights año 1 | Revenue inicial = farmacias como leads (modelo GoodRx) |
| Ejecución: solo founder | Claude Code como CTO virtual + crewAI para automatizar tareas repetitivas |
