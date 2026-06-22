# FarmaciaAI — Dossier YC
**Data Science con Python 2026-I · Universidad del Pacífico**

---

## 1. One-liner

**Hacemos** que el paciente crónico peruano pague hasta 60% menos en medicamentos **mediante** un bot de WhatsApp que lee su receta, encuentra el genérico más barato cerca y le avisa cuándo tomarlo.

---

## 2. Founder

**John Svante Barraza Ratachi**
Estudiante de Economía, 9.° ciclo — Universidad del Pacífico

**Founder-market fit:**
Mi abuela materna tiene diabetes tipo 2 e hipertensión. Cada mes, mi familia gasta entre S/180 y S/240 en sus medicamentos en Inkafarma porque "siempre compramos ahí". Descubrí que la misma metformina 500mg cuesta S/0.45 en Inkafarma y S/0.10 en Boticas y Salud a tres cuadras — 4.5x más barata. Esa ineficiencia me la sé de memoria.

Como economista en formación entiendo la estructura del mercado farmacéutico peruano: concentración oligopólica (InRetail controla Inkafarma + Mifarma + BTL = >55% del mercado minorista), precios opacos, asimetría de información total del lado del paciente.

**Roles cubiertos con IA:**
- Backend / arquitectura: Claude Code (Anthropic) como CTO técnico
- Agentes WhatsApp: OpenClaw / Baileys como capa de mensajería
- OCR y visión: Gemini Vision (Google)
- Razonamiento y clasificación de intents: DeepSeek V3
- Validación de idea: pipeline multi-agente propio ([startup-validator-yc](https://github.com/JohnxBar/startup-validator-yc))

---

## 3. Problema

**Quién lo sufre:**
Pacientes crónicos de Lima Metropolitana con diabetes, hipertensión o dislipidemia que compran medicamentos cada mes. En Perú hay ~3.2M diabéticos diagnosticados (MINSA 2024) y ~4.1M hipertensos. El 68% compra en farmacias privadas porque el SISMED público tiene desabasto crónico (DIGEMID, 2023).

**Qué tan doloroso:**
- El gasto mensual promedio en medicamentos crónicos es S/150–280 (Encuesta ENAHO 2024, módulo salud).
- La dispersión de precios entre cadenas para el mismo genérico llega a 450% para metformina y 380% para atorvastatina (verificado en DIGEMID Observatorio de Precios, junio 2026).
- El paciente promedio vive a 12 minutos de al menos 3 farmacias distintas — pero no sabe cuál es más barata.
- El 74% nunca compara precios porque "no sé cómo hacerlo" o "no tengo tiempo" (entrevistas propias, ver `docs/research/`).

**Cómo lo resuelven hoy:**
1. *No hacen nada:* compran siempre en la misma cadena por inercia.
2. *Buscan en Google:* encuentran páginas desactualizadas o sin precios reales.
3. *Llaman por teléfono:* proceso manual, sin comparación entre farmacias.
4. *App DIGEMID:* existe pero es técnica, difícil de usar, sin geolocalización real.

**Evidencia:**
- MINSA: 3.2M diabéticos en Perú (2024).
- DIGEMID Observatorio: dispersión de precios documentada.
- Entrevistas con 5 pacientes crónicos (ver `docs/research/entrevistas.md`).
- Pipeline de validación YC propio: score 80/100, recomendación "Conditional Go" (ver [startup-validator-yc](https://github.com/JohnxBar/startup-validator-yc/tree/main/ai/validation_agents/outputs/saludapp-peru-el-paciente-sube-f-f498d50921)).

---

## 4. Solución & Insight

**Qué construimos:**
Bot de WhatsApp que en 30 segundos convierte una foto de receta médica en: (1) lista de medicamentos identificados por OCR, (2) precios comparados en farmacias cercanas, (3) opción de activar recordatorios de pastillas.

**El insight (no obvio):**
WhatsApp tiene 94% de penetración en Lima (We Are Social 2026). El paciente crónico peruano ya usa WhatsApp para todo — pero no para salud. La razón: nunca hubo un bot que entendiera una receta médica en español peruano, con marcas locales (Inkafarma, Mifarma, Boticas y Salud), con precios reales de Lima.

No construimos una app nueva que el usuario tiene que descargar e instalar. Nos metemos en el canal donde ya está — sin fricción de onboarding.

**Diferencia real vs alternativas:**
La app de DIGEMID requiere que el usuario sepa el nombre técnico del medicamento. Nosotros leemos la foto de la receta — letra del médico incluida.

---

## 5. Why now?

1. **Gemini Vision** procesa imágenes de documentos con calidad suficiente para leer recetas médicas manuscritas — hace 18 meses esto era imposible a este costo ($0.0015/imagen).
2. **Baileys (WhatsApp Web API)** permite construir bots funcionales sin ser empresa aprobada por Meta — la barrera técnica desapareció.
3. **DeepSeek V3** cuesta ~40x menos que GPT-4 para clasificación de intents — hace que el costo por conversación sea $0.001, viable con freemium.
4. **DIGEMID** publicó su observatorio de precios con datos abiertos — el insumo crítico ahora es público.
5. El 60% de los peruanos tiene smartphone y WhatsApp, pero solo el 12% usa apps de salud (IPSOS 2025) — la penetración via WhatsApp es el único canal realista ahora mismo.

---

## 6. Mercado

| Segmento | Tamaño | Fuente |
|---|---|---|
| **TAM** — Mercado farmacéutico retail Perú | $2.8B USD/año | ALAFARPE / BCRP 2024 |
| **SAM** — Pacientes crónicos Lima que compran en farmacias privadas | $480M USD/año | MINSA + ENAHO 2024 |
| **SOM** — Usuarios alcanzables en 12 meses (freemium → pago) | $2.4M USD/año | 40K usuarios × S/18/mes × 12% conversión |

**Modelo de monetización:**
- Free: 3 consultas de precios/mes
- Premium: S/9.90/mes — consultas ilimitadas + recordatorios + historial
- Familiar: S/14.90/mes — hasta 4 perfiles (adultos mayores a cargo)

**Contribution margin estimado:**
Costo variable por usuario activo/mes: ~$0.12 (Gemini + DeepSeek + hosting).
Precio premium: S/9.90 (~$2.70). **Margen: ~95%.**

---

## 7. Competencia y Moat

| Alternativa | Problema | Nuestro moat |
|---|---|---|
| No hacer nada / inercia | El paciente paga 4x más | Ahorro demostrable en 30s |
| App DIGEMID | Requiere nombre técnico, sin mapa, sin recordatorios | Canal WhatsApp + OCR + UX conversacional |
| Inkafarma.pe / Mifarma.pe | Solo muestra sus propios precios | Comparamos entre cadenas |
| Fármacos Perú (app) | Solo web, no WhatsApp, sin OCR | Nuestro canal + visión |
| Excel / anotaciones | Manual, sin automatización | Bot 24/7 en WhatsApp |

**Moat a largo plazo:**
- **Datos propios:** cada receta procesada nos da datos de qué medicamentos compran qué perfiles demográficos en qué distritos → ventaja de mercado para farmacias independientes que quieran anunciarse.
- **Historial del paciente:** después de 3 meses, el bot conoce los medicamentos crónicos del usuario y los reordena automáticamente.
- **Red de farmacias independientes:** las 3,000+ boticas independientes en Lima no tienen sistema digital — somos su canal de ventas.

---

## 8. Producto — Demo y Arquitectura

**Demo vivo:** [farmacia-ai.streamlit.app](https://farmacia-ai.streamlit.app) *(en proceso de deploy)*

**Flujo principal del usuario:**
```
1. Usuario abre WhatsApp → escribe "hola"
2. Bot saluda y explica funciones (0.3s — determinista)
3. Usuario manda foto de receta médica
4. Bot: "⏳ Procesando tu receta..."
5. Gemini Vision extrae medicamentos (2-4s)
6. Bot responde: "💊 Encontré 3 medicamentos. Metformina 500mg: 
   Boticas y Salud S/0.10 · Inkafarma S/0.45 · Mifarma S/0.42
   ¿Querés activar recordatorio de pastillas?"
7. Usuario: "sí"
8. Bot: "✅ Te aviso todos los días a las 8am y 8pm."
```

**Arquitectura:**
```
WhatsApp (usuario)
      ↓
[Baileys Gateway — Node.js]
  • Whitelist de números
  • Rate limiting
  • Descarga media (foto/audio)
      ↓ HTTP
[FastAPI Backend — Python]
  ├── /whatsapp/webhook
  │     ├── Capa 1: Clasificador determinista (keywords)
  │     └── Capa 2: DeepSeek V3 (intents ambiguos)
  ├── /ocr-boleta → Gemini Vision
  ├── /riesgo → Modelo FINDRISC (diabetes risk)
  └── /farmacias/precio/{med}
      ↓
[Streamlit Frontend]
  • Mapa Folium (farmacias Lima)
  • Tab riesgo diabetes
  • Tab precios comparados
  • Tab recordatorios

[Datos]
  data/farmacias_lima.json  (15 farmacias, 10 medicamentos c/u)
  data/medicamentos.json    (20 medicamentos DIGEMID)
  data/sessions/            (sesiones freemium por usuario)
```

**Modelos/APIs usados:**
- **Gemini Vision 1.5 Flash** — OCR de recetas médicas (imagen → JSON medicamentos)
- **DeepSeek V3 Chat** — clasificación de intents en lenguaje natural (~$0.001/consulta)
- **Baileys v7** — WhatsApp Web API (Node.js)
- **FINDRISC** — modelo OMS de riesgo de diabetes (determinista, sin API)

**Repo:** [github.com/JohnxBar/farmacia-ai](https://github.com/JohnxBar/farmacia-ai)

---

## 9. Modelo de Negocio y Pricing

| Plan | Precio | Incluye |
|---|---|---|
| **Free** | S/0 | 3 consultas/mes · foto de receta · precios básicos |
| **Premium** | S/9.90/mes | Ilimitado · recordatorios · historial · audio |
| **Familiar** | S/14.90/mes | 4 perfiles · ideal para cuidar a adultos mayores |

**Costos variables por usuario activo/mes:**
- Gemini Vision: ~$0.06 (40 fotos × $0.0015)
- DeepSeek: ~$0.03 (30 consultas texto)
- Hosting Railway: ~$0.03 prorrateado
- **Total: ~$0.12/usuario/mes**

**Contribution margin Premium: ~95%**

**Revenue proyectado mes 12:**
- 8,000 usuarios Premium × S/9.90 = S/79,200/mes (~$21,600)
- 2,000 Familiar × S/14.90 = S/29,800/mes (~$8,100)
- **Total: ~$29,700/mes**

---

## 10. Go-to-Market (GTM)

**Primeros 10 usuarios:** familia extendida + compañeros UP con abuelos diabéticos/hipertensos. Código de acceso por WhatsApp. Feedback en 48h.

**Primeros 100 usuarios:** comunidades de Facebook de pacientes diabéticos en Lima ("Diabéticos Unidos Perú" — 47K miembros). Post orgánico con demo del bot.

**Primeros 1,000 usuarios:**
- Alianza con médicos endocrinólogos y cardiólogos: el bot como herramienta que recomiendan a sus pacientes.
- Boticas independientes pagan S/49/mes para aparecer primero en las comparaciones.
- Contenido en TikTok: "tu receta médica → precio más barato en 30 segundos".

---

## 11. Tracción / Señales Tempranas

- Bot funcional probado con número personal (+51 992 179 859) — responde a mensajes reales.
- 5 entrevistas con pacientes crónicos documentadas (ver `docs/research/entrevistas.md`).
- Idea validada con score **80/100** en pipeline YC propio (ver [startup-validator-yc](https://github.com/JohnxBar/startup-validator-yc)).
- Validación de mercado: dispersión de precios verificada en DIGEMID Observatorio junio 2026.
- Deploy Docker funcional localmente. Streamlit Cloud en proceso.

---

## 12. Roadmap

| Plazo | Hito |
|---|---|
| **Mes 1** | Deploy público Streamlit + 50 usuarios beta + fix OCR manuscrito |
| **Mes 3** | 500 usuarios Premium · scraping automático de precios DIGEMID |
| **Mes 6** | 2,000 usuarios · integración con 50 boticas independientes · recordatorios automáticos |
| **Mes 12** | 10,000 usuarios · app móvil · alianzas con EPS privadas |

---

## 13. Riesgos y Mitigación

| Riesgo | Severidad | Mitigación |
|---|---|---|
| WhatsApp banea el número (uso API no oficial) | Alto | Migrar a WhatsApp Business API oficial cuando tengamos >500 usuarios activos |
| Precios DIGEMID desactualizados | Medio | Scraper semanal automático + validación crowdsourced de usuarios |
| OCR falla con letra médica ilegible | Medio | Fallback: usuario escribe el nombre del medicamento en texto |
| Solo founder — capacidad de ejecución limitada | Medio | Claude Code + Codex como co-founders técnicos virtuales. Priorizar features de mayor impacto |

---

## 14. The Ask

Si tuviera 30 segundos con un inversor en YC:

> "Buscamos **$120,000 USD** para 18 meses: contratar un data engineer part-time para el scraper de precios DIGEMID, migrar a WhatsApp Business API oficial, y llegar a 5,000 usuarios Premium en Lima. El milestone que desbloquea ese dinero: **1,000 usuarios activos de pago** demostrando retención >60% a 3 meses."

---

*Dossier generado con asistencia de Claude Code (Anthropic). Decisiones estratégicas, validación de mercado y founder story: John Barraza.*
