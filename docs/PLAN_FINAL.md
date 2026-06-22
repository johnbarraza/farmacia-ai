# PLAN FINAL — Demo del Martes 24 Jun 09:05

## Pipeline score: 69/100 · PAINKILLER · sim 0.50 · GO_WITH_CONSTRAINTS

---

## 1. LA MÁQUINA (backstage)

```
┌─────────────────────────────────────────────────────────────┐
│                    SALUDAPP ENGINE                          │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │ OCR      │  │ PRICES   │  │ RISK     │  │ REMINDERS  │ │
│  │ Gemini   │  │ farmacias│  │ FINDRISC │  │ cron daily │ │
│  │ 2.5 Flash│  │ lim.json │  │ model    │  │ whatsapp   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘ │
│       │             │             │              │         │
│  ┌────┴─────────────┴─────────────┴──────────────┴───────┐ │
│  │                   API UNIFICADA                       │ │
│  │     /ocr  /precios  /riesgo  /recordatorios           │ │
│  └──────────────────────┬────────────────────────────────┘ │
└─────────────────────────┼──────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ┌───────────┐  ┌───────────┐  ┌───────────┐
   │ WHATSAPP  │  │ STREAMLIT │  │ FLUTTER   │
   │ entrada   │  │ resultados│  │ completo  │
   │ Hermes    │  │ AHORA demo│  │ POST-PITCH│
   └───────────┘  └───────────┘  └───────────┘
```

---

## 2. EL CHAT (WhatsApp — simulado en demo)

```
⏱️  09:06 AM — Jurado ve en vivo

┌─────────────────────────────────────┐
│  📲 SaludApp Peru                   │
│  ─────────────────────────────────  │
│                                     │
│  👤 Paciente:                       │
│  📸 [foto de receta médica]         │
│                                     │
│  ─────────────────────────────────  │
│  💊 SaludApp:                       │
│  ✅ Receta del Dr. Velásquez       │
│     MINSA — 02/10/2024              │
│                                     │
│  Tus medicamentos:                  │
│  1️⃣ Hiosina — 1 ampolla c/8h       │
│  2️⃣ Ranitidina — 1 tab c/12h       │
│  3️⃣ Dimenhidrinato — 1 tab c/8h    │
│                                     │
│  💰 AHORRO ESTIMADO:               │
│  💚 Arcángel:   S/4.50 total       │
│  🔴 Inkafarma:   S/9.80 total       │
│  ─────────────────                  │
│  💵 Ahorrás S/5.30 en esta compra   │
│                                     │
│  ¿Qué querés hacer?                 │
│  🔔 RECORDATORIOS (gratis)          │
│  🗺️ VER MAPA COMPLETO →            │
│  📊 CALCULAR RIESGO DIABETES →     │
│  📄 REPORTE PARA TU MÉDICO →       │
│                                     │
│  (Las opciones con → abren         │
│   la app web con más detalle)       │
└─────────────────────────────────────┘
```

---

## 3. EL FLOW COMPLETO

```
PASO 1 — USUARIO MANDA FOTO POR WHATSAPP
  │
  ├─ Hermes Agent recibe imagen
  ├─ Llama a Gemini 2.5 Flash OCR
  ├─ Extrae: medicamentos, dosis, médico, fecha, hospital
  │
  ▼
PASO 2 — AGENTE RESPONDE EN WHATSAPP
  │
  ├─ Busca genérico equivalente (DIGEMID mapping)
  ├─ Busca precios en farmacias cercanas (crowdsourced + OPM base)
  ├─ Muestra el más barato + ahorro
  ├─ Ofrece acciones: recordatorios, mapa, riesgo, reporte
  │
  ▼
PASO 3 — USUARIO ELIGE ACCIÓN
  │
  ├─ "RECORDATORIOS" → Hermes activa cron diario
  │   "☀️ 8am — Hiosina 1 ampolla"
  │   "🌙 8pm — Ranitidina 1 tableta"
  │
  ├─ "MAPA" → Link a Streamlit
  │   https://saludapp-peru.streamlit.app?tab=mapa&med=hiosina
  │   Muestra mapa interactivo con todas las farmacias + precios
  │
  ├─ "RIESGO" → Link a Streamlit
  │   Muestra cuestionario FINDRISC + score
  │
  ├─ "REPORTE" → Link a Streamlit
  │   Genera .md con historial completo → descargable
  │
  └─ "FAMILIAR" → Activa prueba 7 días
      "¿WhatsApp de tu contacto? → +51 987..."
      "💳 Activar ahora: YAPE → https://..."
  │
  ▼
PASO 4 — WEB APP (Streamlit)
  │
  ├─ Mapa interactivo Folium con todas las farmacias
  ├─ Gráfico de adherencia mensual
  ├─ Score FINDRISC con colores por nivel de riesgo
  ├─ Reporte PDF descargable
  ├─ Simulación EHR para el pitch
  │
  ▼
PASO 5 — DATOS SE ACUMULAN (background)
  │
  ├─ Cada receta → 1 registro en historial del paciente
  ├─ Cada boleta confirmada → 1 precio real en la DB
  ├─ Cada mes → adherencia calculada automáticamente
  ├─ Con 10K pacientes → se entrena BEHRT/MOTOR/Delphi propio
```

---

## 4. LA DEMO DEL MARTES (4 minutos)

| Tiempo | Slide / Acción | Qué ve el jurado |
|---|---|---|
| 0:00-0:20 | Slide 1: Problema | "4M peruanos crónicos. 68% no sabe que existe el genérico. Pierde hasta S/238/mes." |
| 0:20-0:50 | **DEMO EN VIVO** — WhatsApp | Abro la app web → Tab "📲 Chat". Muestro la conversación simulada. "El paciente manda foto de receta..." |
| 0:50-1:30 | **DEMO EN VIVO** — OCR real | Subo la receta de muestra → Gemini extrae medicamentos. "Hiosina, Ranitidina, Dimenhidrinato." |
| 1:30-2:10 | **DEMO EN VIVO** — Precios | Tab "💰 Farmacias". Mapa Folium. "Arcángel S/4.50 vs Inkafarma S/9.80. Ahorro: 46%." |
| 2:10-2:40 | **DEMO EN VIVO** — Riesgo | Tab "📊 Riesgo". FINDRISC. "Score: 14/26. Riesgo moderado." |
| 2:40-3:10 | **DEMO EN VIVO** — Futuro | Tab "🔮 Futuro". Simulación BEHRT/MOTOR/Delphi. "Con 10K pacientes, predecimos antes que aparezca." |
| 3:10-3:40 | Slide: Revenue | "S/7.90/mes Premium. S/500/mes farmacia. S/2K/mes EPS. Margen 89%." |
| 3:40-4:00 | Slide: Roadmap | "Año 1: 1K usuarios Lima. Año 2: 10K + Flutter. Año 3: LATAM." |

**QR en última slide → Streamlit Cloud URL + GitHub repo**

---

## 5. QUÉ CONSTRUIR HOY

### Streamlit app (7 tabs final)

| # | Tab | Contenido | Estado |
|---|---|---|---|
| 1 | 📲 **Chat WhatsApp** | Simulación conversación + OCR | ⬜ Construir |
| 2 | 💊 Medicamentos | OCR real + recordatorios | ✅ Listo |
| 3 | 💰 Farmacias | Mapa Folium + ranking precios | ✅ Listo |
| 4 | 📊 Riesgo | FINDRISC score | ✅ Listo |
| 5 | 📄 Reporte | .md → PDF descargable | ✅ Listo |
| 6 | 🔮 Futuro | Simulación BEHRT/MOTOR/Delphi | ✅ Listo |
| 7 | ℹ️ Acerca | Arquitectura + roadmap | ✅ Listo |

### Deploy

| Tarea | Herramienta |
|---|---|
| Subir a GitHub | git push |
| Deploy Streamlit Cloud | share.streamlit.io |
| URL pública | saludapp-peru.streamlit.app |
| Video 1-2 min | OBS grabando el demo |
| Slide deck | Canva |
| QR | qr-code-generator.com |

---

## 6. POST-PITCH (Junio → Diciembre)

```
JUN 24 → Pitch aprobado
JUL    → Hermes Agent en VPS recibiendo WhatsApp real
         Primeros 50 pacientes beta (grupos Facebook diabetes)
AGO    → Validación: ¿escanearon receta? ¿ahorraron? ¿volvieron?
SEP    → 10 farmacias partner pagando S/500/mes
OCT    → MVP Flutter (offline-first, cámara nativa)
NOV    → 1,000 usuarios activos
DIC    → Dataset: 1,000 pacientes × 6 meses = 6,000 recetas
         Entrenar XGBoost baseline
```

---

## 7. COSTOS REALES (para el pitch)

| Stage | Costo mensual |
|---|---|
| MVP (demo) | **$0/mes** (Streamlit Cloud gratis + Gemini free tier) |
| Beta (50 users) | **~$3/mes** (Gemini OCR + WhatsApp msgs) |
| 1K users | **~$50/mes** (95% gratis, 5% premium) |
| 10K users | **~$500/mes** |
| 100K users | **~$5K/mes** |

**Margen bruto: 89-95% en todos los stages.**
