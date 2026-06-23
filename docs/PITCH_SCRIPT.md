# FarmaciaAI — Script Pitch 7 minutos
**Martes 23 Jun 2026 · 09:05–09:12 AM · John Barraza**

---

## [0:00–1:00] PROBLEMA — "El dolor"

> "Mi abuela toma 3 medicamentos crónicos. Cada mes gasta S/180 en Inkafarma.
> Un día fui con ella a la farmacia de enfrente — la misma metformina costaba S/0.10 en vez de S/0.45.
> 4.5 veces más barata. A 3 cuadras de donde siempre compraba."

**El problema:** el paciente crónico en Lima no sabe dónde es más barato el medicamento que ya tiene recetado.

- 3.2 millones de diabéticos en Perú (MINSA 2024)
- Gasto mensual promedio: S/180–240 en medicamentos
- Dispersión de precios: hasta 450% para el mismo genérico (DIGEMID jun 2026)
- El 74% nunca compara precios — 5 entrevistas propias documentadas

**¿Cómo lo resuelven hoy?** Van siempre a la misma farmacia. Google no tiene precios actualizados. La app de DIGEMID es técnica y difícil.

---

## [1:00–4:30] SOLUCIÓN & DEMO EN VIVO

> "Construí FarmaciaAI — un bot de WhatsApp que en 30 segundos convierte tu receta médica en precios comparados y te dice cómo llegar a la farmacia más barata."

**[DEMO VIVO — abrir WhatsApp]**

1. Mandamos foto de receta → **[mostrar respuesta del bot]**
   - OCR con Gemini Vision → extrae medicamentos
   - Compara precios en 15 farmacias de Lima
   - Muestra "S/0.35/tableta en Boticas y Salud · 📍 Av. San Luis 2050 · [Google Maps]"

2. Escribir "MAPA" → **[abrir farmacia-ai.streamlit.app]**
   - Mapa interactivo Folium con farmacias filtradas por distrito
   - Tabla con dirección + link "Cómo llegar"
   - Buscador de 18,364 productos registrados en DIGEMID

3. Escribir "RIESGO" → **[mostrar tab Riesgo]**
   - Test FINDRISC (OMS) — sin análisis de sangre

**El insight no obvio:** WhatsApp tiene 94% de penetración en Lima. El paciente crónico ya está ahí. No necesita descargar nada.

---

## [4:30–5:30] MERCADO & MODELO

| | |
|---|---|
| **TAM** | $2.8B USD/año — mercado farmacéutico retail Perú |
| **SAM** | $480M — pacientes crónicos Lima con farmacia privada |
| **SOM** | $2.4M — 40K usuarios × S/9.90/mes en 12 meses |

**Freemium:**
- Free: 3 consultas OCR/mes
- Premium: S/9.90/mes — ilimitado + recordatorios + historial
- Familiar: S/14.90/mes — hasta 4 perfiles

**Costo variable por usuario:** ~$0.12/mes (Gemini + DeepSeek + hosting)
**Margen de contribución: ~95%**

---

## [5:30–6:30] TRACCIÓN & HERRAMIENTAS DEL CURSO

**Tracción:**
- Bot funcional en número real (+51 994 809 887) — probado en vivo
- 5 entrevistas con pacientes crónicos — validación real del dolor
- Score 80/100 en pipeline YC propio (github.com/JohnxBar/startup-validator-yc)
- Deploy live: farmacia-ai.streamlit.app

**Herramientas del curso usadas:**
- 📸 **PaddleOCR + Gemini Vision** (Lectura 14) — OCR de recetas médicas
- 🗺️ **Folium + GeoPandas** (Lecturas 3-7) — mapa interactivo de farmacias
- 🤖 **OpenClaw/Baileys** (Lectura 15) — agente personal en WhatsApp
- 🧠 **DeepSeek V3** (Lecturas 10-11) — clasificador de intents con LLM
- 📄 **Document AI / Claude** (Lectura 14) — extracción estructurada de recetas

---

## [6:30–7:00] THE ASK

> "Si tuvieran 30 segundos con un inversor en YC:
> Buscamos S/120,000 para 18 meses: scraper de precios DIGEMID en tiempo real,
> WhatsApp Business API oficial, y llegar a 5,000 usuarios Premium en Lima.
> El milestone que desbloquea ese dinero: 1,000 usuarios activos de pago con retención >60% a 3 meses."

---

## Tips para el Q&A (3 min)

**P: ¿WhatsApp no los puede bloquear?**
R: Sí, es el riesgo #1. Tenemos anti-spam implementado. Plan: migrar a WhatsApp Business API oficial cuando lleguemos a 500 usuarios activos.

**P: ¿Los precios son reales?**
R: Demo con 15 farmacias muestreadas manualmente. El roadmap incluye scraping automático del Observatorio de Precios DIGEMID (datos públicos del MINSA).

**P: ¿Por qué tú?**
R: Familiar con diabetes — experimento el dolor todos los meses. Economía UP — entiendo la estructura del mercado farmacéutico peruano. Solo founder con Claude Code como CTO.

**P: ¿Qué herramientas del curso usaste?**
R: Gemini Vision para OCR (Lectura 14), Folium para el mapa (Lecturas 3-7), Baileys estilo OpenClaw para WhatsApp (Lectura 15), DeepSeek para clasificación de intents (Lecturas 10-11).
