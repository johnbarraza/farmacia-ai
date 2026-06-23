# FarmaciaAI — Contenido del Pitch (7 min)
> Revisión pre-presentación · 23 Jun 2026 · John Svante Barraza Ratachi
> Slot: 09:05–09:15 am

---

## SLIDE 1 — PORTADA

**Título:** FarmaciaAI  
**Subtítulo:** Encontrá el medicamento más barato cerca tuyo  
**One-liner:** "Hacemos que el paciente crónico pague 60% menos **mediante** WhatsApp + OCR de recetas"  
**Demo:** farmacia-ai.streamlit.app · +51 994 809 887  

---

## SLIDE 2 — EL FOUNDER *(~40 seg)*

**Quién soy:**
- Economía 9° ciclo · Universidad del Pacífico
- Asistente de Investigación, **CIUP**
- Soy economista que construye productos de IA. El CIUP me enseñó a trabajar con datos reales. 3 apps desplegadas antes de este proyecto.

**Proyectos previos desplegados:**
- **MatriculaUp** — optimizador de matrícula UP
- **UPBlackboardSync** — material académico + LLMs
- **Sumaya** — finanzas personales web + Android

**¿Por qué yo?**
- **Economista:** entiendo la asimetría de información en precios
- **CIUP:** valido con datos MINSA, INEI, DIGEMID — no opiniones
- **Builder:** 3 apps reales para mi comunidad UP — ya sé hacer esto

**Solo founder — roles cubiertos con IA:**
| Rol | Herramienta |
|---|---|
| CTO | Claude Code |
| Diseño | Stitch / v0.dev |
| Research | Perplexity + Gemini |
| Clientes | TikTok + crewAI |

> 🗣️ **Qué decir en voz:** "Soy John, economista de noveno ciclo e investigador del CIUP. Ya construí tres apps para mi comunidad universitaria. Conozco el problema de primera mano — mi abuela es diabética."

---

## SLIDE 3 — EL PROBLEMA *(~1 min)*

**Historia:**
> "Mi abuela toma metformina todos los meses. En Inkafarma le cobran S/0.45 por tableta. A 3 cuadras, en Boticas y Salud, cuesta S/0.10. **4.5 veces más barata.** Nunca lo supo."

**¿Quién lo sufre?**
- **3.2M** diabéticos diagnosticados en Perú (MINSA 2024)
- Gasto mensual promedio: **S/180–240** en medicamentos
- Dispersión de precios: hasta **450%** para el mismo genérico
- El **74%** nunca compara precios

**¿Cómo lo resuelven hoy?**
- Inercia: misma farmacia siempre
- Google: precios desactualizados
- App DIGEMID: técnica, difícil de usar
- Ninguna lee la receta manuscrita

**Evidencia:** 5 entrevistas con pacientes crónicos documentadas (`docs/research/entrevistas.md`)

> 🗣️ **Qué decir:** "El problema no es que no haya información — DIGEMID la publica. El problema es que nadie se la lleva al paciente en el canal que ya usa."

---

## SLIDE 4 — LA SOLUCIÓN *(~1 min)*

**Flujo en 30 segundos:**
1. Usuario manda **foto de receta** por WhatsApp
2. **Gemini Vision** extrae medicamentos (OCR)
3. **DIGEMID** valida nombres (18,364 productos)
4. Compara precios en 15 farmacias de Lima
5. Responde con precio/unidad + **link Google Maps**

**El Insight:**
> WhatsApp tiene **94% de penetración** en Lima. El paciente crónico ya está ahí. **No necesita descargar nada.**

**Ejemplo de respuesta del bot:**
```
Metformina 500mg · 2 veces al día

Precios más baratos:
• S/0.35/tableta → Boticas y Salud
• S/0.45/tableta → Inkafarma

📍 Boticas y Salud San Borja
   Av. San Luis 2050, San Borja
   [Google Maps link]
```

---

## SLIDE 5 — ¿POR QUÉ AHORA? *(~40 seg)*

- **Gemini Vision** procesa recetas manuscritas en español a $0.0015/imagen (hace 18 meses imposible)
- **Baileys / OpenClaw** permite bots WhatsApp sin ser empresa aprobada por Meta
- **DeepSeek V3** cuesta 40× menos que GPT-4
- **DIGEMID** publicó observatorio de precios con datos abiertos
- **94%** limeños usa WhatsApp, solo **12%** usa apps de salud (IPSOS 2025)

**Stack del curso usado:**
| Herramienta | Lectura |
|---|---|
| Gemini Vision (OCR) | L14 |
| Folium + mapas GIS | L3-7 |
| Baileys / OpenClaw | L15 |
| DeepSeek V3 (LLM) | L10-11 |
| Claude Code (CTO) | L15 |

---

## SLIDE 6 — COMPETENCIA Y MOAT *(~30 seg)*

| | OCR | WhatsApp | Compara | Gratis |
|---|---|---|---|---|
| **FarmaciaAI** | ✅ | ✅ | ✅ | ✅ |
| Inkafarma App | ❌ | ❌ | ❌ | ✅ |
| App DIGEMID | ❌ | ❌ | ❌ | ✅ |
| Google | ❌ | ❌ | ❌ | ✅ |
| No busco / Excel | ❌ | ❌ | ❌ | ✅ |

**Moat:**
- Canal único: WhatsApp — cero fricción de descarga
- OCR de recetas manuscritas en español — nadie más
- DIGEMID integrado: 18,364 productos validados
- Datos propios: historial por cadena y distrito

---

## SLIDE 7 — ARQUITECTURA *(demo en vivo aquí)*

**Canal WhatsApp:**
Usuario → Bot Baileys → Gemini Vision OCR → DIGEMID 18,364 → Comparador → Respuesta + Maps

**Canal Web:**
farmacia-ai.streamlit.app → Filtros GIS → Tabla precios → Mapa Folium

**Stack:** DeepSeek V3 · Streamlit · Pandas · Folium · BeautifulSoup · Baileys

> 🗣️ **Hacer DEMO EN VIVO aquí:** abrir farmacia-ai.streamlit.app + mandar foto de receta por WhatsApp al +51 994 809 887

---

## SLIDE 8 — MERCADO Y MODELO *(~45 seg)*

**Tamaño de mercado:**
| | Mercado | USD/año |
|---|---|---|
| TAM | Farmacéutico Perú | $2.8B |
| SAM | Crónicos Lima | $480M |
| SOM | 40K usuarios 12m | $2.4M |
*Fuentes: MINSA 2024, INEI, IMS Health, IPSOS Perú 2025*

**Pricing:**
- **Free:** 3 consultas OCR/mes
- **Premium:** S/9.90/mes — ilimitado + recordatorios
- **Familiar:** S/14.90/mes — 4 perfiles

**Economía unitaria:**
- Costo variable: $0.12/usuario/mes
- Precio Premium: S/9.90 ≈ $2.70
- **Margen de contribución: ~95%**

**Go-to-Market:**
- 10 usuarios: familia + compañeros UP
- 100: Facebook "Diabéticos Unidos Perú"
- 1K: médicos endocrinólogos + TikTok

---

## SLIDE 9 — ROADMAP Y RIESGOS *(~30 seg)*

**Roadmap:**
| Plazo | Hito |
|---|---|
| 3 meses | 1,000 usuarios · scraper DIGEMID live |
| 6 meses | WhatsApp Business API oficial · 3K usuarios |
| 12 meses | 10K usuarios · expansión provincias |

**Riesgos y mitigación:**
1. **Legal scraping DIGEMID** → acuerdo con DIGEMID / API oficial
2. **Solo founder** → Claude Code como CTO; arquitectura modular
3. **Retención baja** → recordatorios de toma + perfil crónico

---

## SLIDE 10 — TRACCIÓN Y THE ASK *(~45 seg)*

**Tracción real:**
- ✅ Bot funcional en número real (+51 994 809 887)
- ✅ 5 entrevistas con pacientes crónicos documentadas
- ✅ Score **80/100** en pipeline YC propio
- ✅ Deploy live: farmacia-ai.streamlit.app
- ✅ 40+ commits en GitHub, CI configurado
- ✅ Catálogo DIGEMID 18,364 productos integrado

**The Ask: $120,000 USD** para 18 meses:
- Scraper precios DIGEMID en tiempo real
- WhatsApp Business API oficial
- Llegar a 5,000 usuarios Premium

**Milestone que desbloquea la siguiente ronda:**
> 1,000 usuarios activos de pago con retención >60% a 3 meses

> *"Make something people want." — Y Combinator*

---

## GUÍA Q&A — Preguntas esperadas

**"¿Por qué no usaron PaddleOCR del curso en lugar de Gemini?"**
> PaddleOCR funciona bien para texto impreso uniforme. Las recetas peruanas son mayormente manuscritas, con abreviaciones médicas y letra de médico. Gemini Vision maneja contexto multimodal — entiende "mtf 500" como metformina. Probamos ambas y Gemini tuvo mucha mejor precisión en recetas reales. Costo: $0.0015/imagen es negligible dado el margen del 95%.

**"¿Cómo van a retener usuarios?"**
> El paciente crónico compra medicamentos todos los meses. Retención natural. Añadimos recordatorios de toma + perfil de medicamentos guardado para que no tengan que mandar la receta cada vez.

**"¿Y si DIGEMID bloquea el scraping?"**
> Tenemos dos opciones: 1) acuerdo directo con DIGEMID como aliado (tienen incentivo — quieren que el público acceda a sus datos), 2) WhatsApp Business API nos conecta con farmacias directamente para precios en tiempo real.

**"¿Los commits son todos del 22 de junio?"**
> La fase de validación — torneo de ideas, pipeline YC, 16 startups evaluadas — vivió en github.com/JohnxBar/hw7_ds del 12 al 21 de junio. Las entrevistas tienen fecha 14-20 Jun en docs/research/entrevistas.md. Este repo es la implementación del MVP una vez validado el problema.

**"¿Necesitas realmente $120K?"**
> Sí: $24K founder 18 meses + $36K marketing + $13.5K WhatsApp API + $9K scraper + $6.5K hosting + $5K legal + $18K buffer. El número tiene desglose específico.

---

## CHECKLIST FINAL ANTES DE ENTRAR

- [ ] farmacia-ai.streamlit.app abierto en el navegador
- [ ] WhatsApp listo en el celular con foto de receta cargada
- [ ] PDF del pitch abierto como backup
- [ ] docs/expo/arquitectura.html abierto como diagrama backup
- [ ] Timer 7 minutos visible
- [ ] Conexión WiFi verificada / datos móviles como backup
