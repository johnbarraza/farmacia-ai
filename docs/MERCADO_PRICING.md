# SaludApp Peru — Mercado, Pricing & Revenue

## 1. QUIÉN SUFRE (target preciso)

**Paciente crónico limeño, 45-65 años, 2-3 medicamentos mensuales, paga de su bolsillo.**

| Variable | Dato | Fuente |
|---|---|---|
| Población Lima Metro | 11.3 millones | INEI Censo 2017 + proyección 2025 |
| Prevalencia diabetes + HTA en adultos | 12.4% | INEI ENDES 2023 |
| Pacientes crónicos Lima Metro | ~840,000 adultos | Cálculo propio sobre ENDES |
| Compran en farmacia privada | ~60% (504,000) | SUSALUD — cobertura SIS/EsSalud es ~40% |
| **Target inicial (SAM)** | **500,000 pacientes** | Lima, compra mensual, bolsillo propio |
| Gasto mensual promedio en medicinas | S/80–150 | INEI ENAHO — módulo salud |
| Mercado anual de bolsillo | S/720M | 500K × ~S/120 × 12 |

---

## 2. TAM / SAM / SOM

```
TAM: 2.4M pacientes crónicos que compran en farmacia privada en Perú
     → S/3,460M/año en medicamentos de bolsillo

SAM: 500K pacientes en Lima Metro (misma ciudad, misma logística)
     → S/720M/año

SOM: 1,000 usuarios activos en 12 meses
     → Validación del hook de ahorro
     → Revenue: ~S/100K (B2B + premium)
```

**Por qué Lima primero:**
- 5-10 farmacias por km² → comparación de precios tiene sentido
- 4G ubicuo → OCR funciona sin offline-first (MVP)
- Pacientes con smartphone → WhatsApp + app
- Densidad de farmacias → crowdsourcing de precios arranca rápido

**Expansión geográfica post-Lima:**

| Año | Ciudad | Nuevos usuarios | Razón |
|---|---|---|---|
| 1 | Lima Metro | 1,000 | Mercado denso, 5 farmacias/cuadra |
| 2 | Arequipa + Trujillo | 5,000 | Mismas cadenas (Inkafarma, Mifarma) |
| 3 | Perú urbano (top 10 ciudades) | 25,000 | Cobertura nacional de farmacias |
| 4 | Colombia (Bogotá, Medellín) | 100,000 | Mismo problema, mismas cadenas |
| 5 | LATAM (MX, CL, CO) | 500,000 | Escala regional |

---

## 3. CÓMO GANA DINERO (pricing)

### Planes B2C

| Plan | Precio | ¿Qué incluye? | ¿Quién paga? |
|---|---|---|---|
| **Gratuito** | S/0 | Comparador precios, recordatorios, FINDRISC, 1 perfil | 95% de usuarios |
| **Familiar** | S/15/mes | + Alertas WhatsApp (3 contactos) + perfil compartido | Hijos de adultos mayores |
| **Premium** | S/25/mes | + Watch sync + exportar PDF + voz avanzado + sin ads | Early adopters |

### Planes B2B

| Producto | Precio | Buyer | Value prop |
|---|---|---|---|
| **Farmacia Partner** | S/500/mes | Boticas independientes, cadenas chicas | Leads: pacientes derivados a tu farmacia |
| **Farmacia Destacada** | S/1,200/mes | Cadenas medianas | Listing top + badge "Más barato" + analytics |
| **EPS Dashboard** | S/2,000/mes | Rímac, Pacífico, Sanitas | Adherencia real de afiliados + alertas de riesgo |
| **MINSA Insights** | S/8,000/mes | DIGEMID, SUSALUD | Datos anonimizados de precios + adherencia poblacional |

---

## 4. PROYECCIÓN DE REVENUE (3 años)

### Año 1 — Validación (1,000 usuarios)

| Fuente | Cálculo | Anual |
|---|---|---|
| Premium (5% conversión) | 50 × S/20 avg × 12 | S/12,000 |
| Farmacias Partner (10) | 10 × S/500 × 12 | S/60,000 |
| EPS piloto (1) | 1 × S/2,000 × 12 | S/24,000 |
| **TOTAL Año 1** | | **S/96,000 (~$25,600)** |

### Año 2 — Crecimiento (10,000 usuarios)

| Fuente | Cálculo | Anual |
|---|---|---|
| Premium (5%) | 500 × S/22 avg × 12 | S/132,000 |
| Farmacias (30) | 30 × S/600 avg × 12 | S/216,000 |
| EPS (3 contratos) | 3 × S/2,000 × 12 | S/72,000 |
| MINSA (1 piloto) | 1 × S/5,000 × 12 | S/60,000 |
| **TOTAL Año 2** | | **S/480,000 (~$128,000)** |

### Año 3 — Escala (50,000 usuarios + LATAM entry)

| Fuente | Cálculo | Anual |
|---|---|---|
| Premium (5%) | 2,500 × S/22 avg × 12 | S/660,000 |
| Farmacias (100) | 100 × S/600 avg × 12 | S/720,000 |
| EPS (10) | 10 × S/2,000 × 12 | S/240,000 |
| MINSA / B2G | | S/120,000 |
| Colombia entry | | S/150,000 |
| **TOTAL Año 3** | | **S/1,890,000 (~$504,000)** |

---

## 5. SUSTITUTOS (cómo lo resuelven hoy)

| Sustituto | % que lo usa | Costo para el usuario | Por qué ganamos |
|---|---|---|---|
| **No pregunta** (compra la marca que le recetaron) | ~68% | 77-87% más caro | App muestra automáticamente |
| **Pregunta al farmacéutico** | ~20% | Depende de honestidad | App es imparcial, no empleado |
| **WhatsApp de la farmacia** | ~8% | Gratis, lento (respuesta en horas) | App es instantáneo + geolocalizado |
| **OPM-DIGEMID web** | <2% | Gratis, pero sin geo ni app | App tiene UX mobile + ubicación |
| **Camina entre farmacias** | ~5% | 20-40 min por farmacia | App muestra todas en 1 pantalla |
| **Google / Facebook groups** | ~3% | Gratis, info desactualizada | Precios en tiempo real |

**Fuente de %: estimación propia basada en comportamiento observado. Requiere validación con encuesta.**

---

## 6. COSTOS

| Costo | Mensual (1K users) | Mensual (10K users) | Nota |
|---|---|---|---|
| Gemini API (OCR) | $0.50 | $5 | ~$0.001/imagen con Gemini Flash |
| DeepSeek API (fallback) | $0.10 | $1 | ~$0.0005/request |
| Streamlit Cloud | $0 | $0 | Free tier |
| Infra (VPS eventual) | $0 | $40 | Contabo VPS S/150/mes |
| Dominio | $0 | $1 | saludapp.pe ~$12/año |
| **TOTAL** | **<$1/mes** | **~$47/mes** | Margen bruto >95% |

---

## 7. MÉTRICAS CLAVE

| Métrica | Target Año 1 | Target Año 2 |
|---|---|---|
| Usuarios activos (MAU) | 1,000 | 10,000 |
| Recetas escaneadas/mes | 3,000 | 30,000 |
| Boletas de confirmación/mes | 500 | 8,000 |
| Tasa conversión premium | 5% | 5% |
| Churn mensual | <5% | <3% |
| CAC (customer acquisition cost) | S/0 (orgánico) | S/5 (referidos) |
| LTV premium user | S/480 (24 meses) | S/600 (30 meses) |
| Farmacias partner | 10 | 50 |
| Contratos EPS | 1 piloto | 3 pagos |

---

## 8. FUENTES

| Fuente | Dato usado |
|---|---|
| **INEI ENDES 2023** | Prevalencia diabetes 4.8%, HTA 8.1% en adultos peruanos |
| **INEI ENAHO 2023** | Gasto bolsillo salud: S/47/mes promedio, S/120 medicinas crónicos |
| **SUSALUD** | 40% población con SIS/EsSalud, 60% depende de farmacia privada |
| **DIGEMID** | Precios oficiales de medicamentos (diferencia marca/genérico: 77-87%) |
| **OPS Perú 2019** | 68% pacientes no conoce alternativa genérica |
| **MINSA** | 4M+ peruanos con enfermedad crónica no transmisible |
| **BCRP** | Salario mínimo S/1,130 (2026), PBI per cápita ~$8,400 |
| **Banco Mundial** | Gasto salud out-of-pocket Perú: 28% del gasto total en salud |