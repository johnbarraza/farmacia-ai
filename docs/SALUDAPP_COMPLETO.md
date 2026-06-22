# SaludApp Peru — Documento Completo

## 🎯 Visión

**"Proxy de salud"** — el usuario entra a ahorrar plata en pastillas. Su historial
médico se construye solo como efecto secundario.

> "No eres una app de salud. Eres un comparador de precios de medicamentos.
> El historial clínico es el subproducto más valioso del país."

---

## 📊 Puntuación del Pipeline

| Stage | Resultado |
|---|---|
| Stage 0 (Pit check) | **PAINKILLER** — problema estructural real |
| Stage 1 (Research) | 15 alternativas mapeadas |
| Stage 2 (Gaps) | 5 gaps priorizados |
| Stage 2B (Iterations) | I1 ORIGINAL gana: 23/30 |
| Stage 3 (YC Validation) | **GO_WITH_CONSTRAINTS** |
| Stage 3B (MiroFish 10p) | **0.50 / 0.60** (WARN) |
| Stage 3C (Dossier) | **69/100** |

**Brecha al gate 0.60:** OCR accuracy en recetas manuscritas + chicken-egg inicial.
Se cierra con piloto de 30 días y 50 usuarios reales.

---

## 🔥 El Hook (por qué la usan)

```
Usuario compra pastillas en Inkafarma → recibe boleta
→ Abre SaludApp → 📸 FOTO a la receta (5 segundos)
→ App: "Losartan 50mg genérico:
   Inkafarma S/0.65 vs Boticas Arcángel S/0.33 (a 200m)
   AHORRAS S/51.30 AL MES"
→ Usuario compra en Arcángel → sube boleta → confirma ahorro
→ SaludApp registra: adherencia ✅, precio real ✅, ubicación ✅
```

**El data de salud entra como EFECTO SECUNDARIO del ahorro.**

---

## 🏗️ Arquitectura

### Stack

| Capa | MVP (Pitch martes) | Producción (post-pitch) |
|---|---|---|
| Frontend | **Streamlit** (1 archivo, deploy cloud) | **Flutter** (iOS + Android + Web) |
| Backend | Streamlit embedded | FastAPI + PostgreSQL |
| OCR | Gemini 2.5 Flash (cloud) | PaddleOCR local + Gemini cloud |
| DB | SQLite (session state) | PostgreSQL + SQLite offline |
| Mapas | Folium | flutter_map + OsmAnd tiles |
| Notificaciones | Streamlit session | Firebase local + SMS fallback |
| Deploy | Streamlit Cloud (gratis) | Docker + VPS |
| Mensajería | — | Hermes Agent (WhatsApp nativo) |

### Offline-first

```
📸 Foto receta → PaddleOCR local (sin internet)
🔔 Recordatorios → local notifications
📋 Historial → SQLite en el teléfono
🔄 Cuando WiFi → sincroniza + baja precios actualizados
```

---

## 🎨 Diseño UI/UX

### Inspiración

- **Amy Food Journal:** minimalismo, escribe lo que comiste, sin fricción
- **SparkyFitness:** self-hosted, privacy-first, multi-device sync
- **LifeStack:** tarjetas de energía, calendario con salud, modo oscuro premium
- **Imágenes de referencia:** cards con gradientes suaves, tipografía grande,
  temporizador circular, "To Do" minimalista, modo oscuro con acentos de color

### Principios

1. **5 segundos para completar la acción principal** (foto receta → resultado)
2. **1 pantalla = 1 acción** (sin menús profundos)
3. **La info de salud emerge, no se pide** (sin formularios)
4. **Offline siempre funciona** (sin pantallas de "cargando...")
5. **Voz como entrada primaria** (dictado de síntomas, comidas)

### Palette

```
Fondo principal:    #0F111A (dark premium)
Cards:              #1A1C28 con borde #2D3142
Acento primario:    #45F3FF (cyan eléctrico — ahorro, acción)
Acento positivo:    #00FF88 (verde — pastilla tomada, ahorro)
Acento alerta:      #FFAA00 (ámbar — pastilla olvidada)
Acento riesgo:      #FF3333 (rojo — score alto)
Texto:              #FFFFFF / #C5C6C7
```

### Tipografía

- Headlines: **Space Grotesk** (bold, moderno)
- Body: **Inter** (legible, profesional)
- Números/datos: **JetBrains Mono** (mono, datos médicos)
- Tamaño mínimo: 16px

---

## 🧭 Flow de 6 pantallas

### 1. 📸 ESCANEAR RECETA (entrada)
```
┌──────────────────────────────┐
│         📸                    │
│   Fotografía tu receta       │
│   o boleta de farmacia       │
│                              │
│   ┌──────────────────┐      │
│   │  TOMAR FOTO 📷   │      │
│   └──────────────────┘      │
│   ┌──────────────────┐      │
│   │  🎤 Dictar receta │      │
│   └──────────────────┘      │
│   ┌──────────────────┐      │
│   │  📁 Subir archivo │      │
│   └──────────────────┘      │
│                              │
│  Funciona sin internet ✅    │
│  Tus datos son tuyos 🔒      │
└──────────────────────────────┘
```
**Extrae:** medicamentos, dosis, frecuencia, paciente, médico, hospital, fecha.

### 2. 💰 AHORRAR (hook principal)
```
┌──────────────────────────────┐
│  💊 Losartan 50mg            │
│                              │
│  💚 Más barato (200m):       │
│  ┌──────────────────────────┐│
│  │ Boticas Arcángel        ││
│  │ S/ 0.33  ← AHORRAS 49%  ││
│  │ Av. Brasil 1520, Jesús M││
│  │ Abierto hasta 11pm ⏰    ││
│  └──────────────────────────┘│
│                              │
│  🔴 Más caro:                │
│  Inkafarma S/0.65            │
│                              │
│  💰 Ahorro mensual: S/51.30  │
│                              │
│  [🗺️ VER MAPA] [✅ YA COMPRÉ]│
└──────────────────────────────┘
```

### 3. ✅ CONFIRMAR COMPRA
```
┌──────────────────────────────┐
│  ¿Compraste en Arcángel?     │
│                              │
│  📸 Sube la boleta para      │
│  confirmar el precio real    │
│                              │
│  ┌──────────────────┐      │
│  │  FOTO BOLETA 🧾  │      │
│  └──────────────────┘      │
│                              │
│  ✅ Precio confirmado: S/0.33│
│  📊 Tu dato mejora la app    │
│  💊 Adherencia registrada ✅ │
└──────────────────────────────┘
```

### 4. 🔔 RECORDATORIOS (diario)
```
┌──────────────────────────────┐
│  Hoy, 21 junio               │
│                              │
│  ☀️ 8:00 AM                  │
│  ┌──────────────────────────┐│
│  │ Metformina 500mg    ✅   ││
│  │ Con comida           💊  ││
│  └──────────────────────────┘│
│                              │
│  🌙 8:00 PM                  │
│  ┌──────────────────────────┐│
│  │ Atorvastatina 20mg  ⏳   ││
│  │ Sin comida           💊  ││
│  └──────────────────────────┘│
│                              │
│  👨‍👩‍👧 Tu hija María recibe      │
│  alerta si olvidas.          │
│                              │
│  [🎤 "Tomé mi pastilla"]     │
└──────────────────────────────┘
```

### 5. 📊 MI SALUD (emerge solo)
```
┌──────────────────────────────┐
│  Hola, Juan                  │
│                              │
│  ┌──────────────────────────┐│
│  │ 🩺 Riesgo Diabetes       ││
│  │ Moderado · 14/26         ││
│  │ Última HbA1c: 6.8%      ││
│  └──────────────────────────┘│
│                              │
│  ┌──────────────────────────┐│
│  │ 💊 Adherencia            ││
│  │ ████████░░ 87% este mes  ││
│  │ Mejor que el mes pasado  ││
│  └──────────────────────────┘│
│                              │
│  ┌──────────────────────────┐│
│  │ 📄 Reporte para tu médico││
│  │ Descargar PDF →          ││
│  └──────────────────────────┘│
│                              │
│  Datos acumulados: 6 meses   │
└──────────────────────────────┘
```

### 6. 🔮 FUTURO (opcional, pitch closer)
```
┌──────────────────────────────┐
│  Con tus datos (anonimizados)│
│  + 10,000 pacientes más...   │
│                              │
│  🧬 PREDECIMOS TU RIESGO     │
│  ANTES QUE APAREZCA          │
│                              │
│  ┌──────────────────────────┐│
│  │ ⏱️ En 14 meses:          ││
│  │ 30% riesgo renal         ││
│  │ Intervención sugerida:   ││
│  │ Ajuste de Metformina     ││
│  └──────────────────────────┘│
│                              │
│  Modelo: MOTOR/FEMR + Delphi │
│  Data: 100% peruana, propia  │
└──────────────────────────────┘
```

---

## 📲 Entrada por voz

```
Usuario: 🎤 "Tomé mi Metformina"
App:     ✅ "Registrado. Próxima dosis: 8pm. Hoy llevas 100% adherencia."

Usuario: 🎤 "Me duele la cabeza desde ayer, tipo presión"
App:     📋 "Registrado. ⚠️ Si persiste con visión borrosa, ve a emergencia.
               Compartiré esto con tu médico en el próximo reporte."

Usuario: 🎤 "Almorcé arroz con pollo y chicha morada"
App:     🍽️ "~650 kcal. 1,800/2,200 hoy. ✅ Bien. 
               ⚠️ Alto en carbohidratos para tu perfil diabético."
               (Fase 2 — no en MVP)
```

---

## 💰 Pricing

| Plan | Precio | Incluye |
|---|---|---|
| **Gratuito** | S/ 0 | Receta, precios, recordatorios, offline, 1 perfil |
| **Familiar** | S/ 15/mes | + WhatsApp alertas (3 contactos) + perfil compartido |
| **Premium** | S/ 25/mes | + Watch sync + foto comida + PDF + exportar + voz avanzado |
| | | |
| **EPS Dashboard** | S/ 2,000/mes | Adherencia de afiliados, riesgos poblacionales |
| **Farmacia Partner** | S/ 500/mes | Leads por proximidad + listing destacado |
| **MINSA Insights** | S/ 5,000/mes | Datos anonimizados para salud pública |

---

## 🗺️ Roadmap

| Fase | Fecha | Hito | ¿Qué se necesita? |
|---|---|---|---|
| **MVP** | Jun 2026 | OCR + precios + recordatorios + FINDRISC | 1 founder + Claude Code |
| **Beta** | Ago 2026 | 50 usuarios activos, 30+ días de datos | Validación del hook de ahorro |
| **V1 Flutter** | Oct 2026 | App nativa iOS + Android, offline-first | 1 dev Flutter |
| **1K users** | Dic 2026 | Dataset longitudinal peruano inicial | Crecimiento orgánico |
| **Fase 2** | Ene 2027 | Watch sync + foto comida + voz avanzado | 1 dev backend |
| **5K users** | Mar 2027 | BEHRT / CLMBR sobre data peruana | Data scientist |
| **B2B launch** | Abr 2027 | 1er contrato EPS firmado | Sales B2B |
| **10K users** | Jun 2027 | MOTOR/FEMR time-to-event | GPU + datos |
| **100K users** | 2028+ | Delphi propio peruano | Infraestructura |

---

## 🔒 Competencia

| Competidor | Qué hace | Por qué ganamos |
|---|---|---|
| OPM-DIGEMID | Precios declarados, sin geo, web lenta | Precios REALES, geolocalizados, app |
| Inkafarma/Mifarma apps | Solo sus precios, sin historial | Todas las farmacias + historial clínico |
| Google/Apple Health | Datos de wearable, sin contexto médico | Recetas, diagnóstico, adherencia |
| WhatsApp grupos | Comparten precios manualmente | Automático, preciso, privado |
| LifeStack | Planificador de energía (B2C) | Enfermedades crónicas (B2B2C) |
| SparkyFitness | Self-hosted fitness tracker | Salud médica, no fitness |
| Amy Food Journal | Diario de calorías (iOS) | Medicamentos + riesgo + reporte médico |

---

## 🛡️ Seguridad

- **Offline-first:** los datos sensibles nunca salen del teléfono sin permiso
- **Anonimización:** datos para B2B son agregados, no individuales
- **Prompt injection:** delimitadores XML + sanitización estricta
- **Ley 29733:** consentimiento explícito, datos en Perú (VPS local o AWS São Paulo)
- **No vendor lock-in:** Hermes Agent es open-source, modelos son propios

---

## 📁 Archivos del proyecto

```
saludapp-peru/
├── ai/
│   ├── health_agents.py     ← OCR pipeline (Paddle→Gemini→DeepSeek→mock)
│   ├── ehr_simulator.py     ← Simulación BEHRT/MOTOR/Delphi para pitch
│   └── predict_risk.py      ← Modelos reales (FINDRISC + XGBoost + BEHRT)
├── backend/app/
│   ├── main.py              ← FastAPI 10 endpoints
│   └── health_models.py     ← RiskModel + roadmap EHR completo
├── frontend/
│   └── app.py               ← Streamlit 8 tabs (pitch-ready)
├── data/
│   ├── farmacias_lima.json  ← 15 farmacias con coordenadas
│   └── medicamentos.json    ← 20 medicamentos DIGEMID
├── docs/
│   ├── PLANNING.md          ← Arquitectura técnica
│   └── SALUDAPP_COMPLETO.md ← Este documento
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🎤 Pitch de 4 minutos

```
[30s]  PROBLEMA:
       En Perú no existe open health. 4M+ pacientes crónicos no tienen historial,
       olvidan pastillas, pagan hasta 80% de más. Sus médicos no saben qué tomaron.
       Sus familias no saben si están bien.

[60s]  SOLUCIÓN — DEMO EN VIVO:
       📸 Paciente sube foto de su receta.
       App extrae TODO: paciente, médico, medicamentos, dosis.
       💰 "Losartan 50mg: Inkafarma S/0.65 vs Boticas Arcángel S/0.33 (200m).
           AHORRAS S/51 AL MES."
       🔔 Recordatorios 8am y 8pm.
       👨‍👩‍👧 "Tu hija recibe alerta si olvidas."
       📊 "Riesgo diabetes: moderado. Reporte PDF para tu doctor."

[60s]  HERRAMIENTAS DATA SCIENCE:
       - PaddleOCR + Gemini Vision: extracción de recetas peruanas (Lectura 14)
       - Folium/GeoPandas: mapa de farmacias con precios crowdsourced (Lectura 3-7)
       - Streamlit: frontend deployado (Lectura 3-7)
       - Claude/Gemini API: extracción estructurada (Lectura 9)
       - Patrón agentes IA: búsqueda de precios + recordatorios (Lectura 10-11)
       - FINDRISC: modelo de riesgo validado OMS con slot para futuro MOTOR/Delphi

[60s]  MODELO DE NEGOCIO:
       Usuario: GRATIS (siempre). Familiar: S/15/mes. Premium: S/25/mes.
       EPS: S/2,000/mes por dashboard de adherencia.
       Farmacia: S/500/mes por leads.
       100K usuarios → S/116K/mes → $31K MRR.

[30s]  MOAT:
       Somos el PRIMER dataset longitudinal de salud en Perú.
       Recetas + boletas + adherencia + precios reales.
       Con 10K pacientes, entrenamos nuestro propio transformer de riesgo.
       Eso no lo tiene nadie. Eso no se copia sin tiempo.
```

---

## ✅ Checklist pre-pitch (Lunes 23 antes 09:05)

- [ ] Streamlit deployado en Cloud (URL pública)
- [ ] Video demo 1-2 min con audio + pantalla
- [ ] Slide deck ≤15 slides (Canva/PPT)
- [ ] QR a repo + demo en última slide
- [ ] Probar OCR con receta real (✅ ya funciona con Gemini 2.5 Flash)
- [ ] Probar EHR simulator (✅ fixeado)
- [ ] Copiar .env a saludapp-peru

---

*Documento generado 2026-06-21. Última actualización tras pipeline score 69/100, sim 0.50.*
