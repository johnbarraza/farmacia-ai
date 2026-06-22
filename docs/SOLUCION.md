# SaludApp — Dolor, Solución, Aporte, Riesgos

## 1. DOLOR

> **Un paciente crónico en Lima gasta hasta 87% de más en medicamentos sin saber que el genérico equivalente está a 200 metros. Son S/150–238 perdidos cada mes — hasta 21% del salario mínimo.**

| Variable | Dato | Fuente |
|---|---|---|
| Pacientes crónicos en Lima que compran de su bolsillo | ~500,000 | INEI ENDES + SUSALUD |
| Diferencia marca vs genérico | 77–87% | DIGEMID lista oficial |
| No saben que existe alternativa genérica | 68% | OPS Perú 2019 |
| Hogares que no pudieron comprar medicinas recetadas | 17% | INEI ENDES 2023 |
| Usan OPM-DIGEMID (web del gobierno) | <2% | No tiene app, no tiene geo |

---

## 2. ALTERNATIVAS (cómo lo resuelven hoy)

| Alternativa | % | Qué hace | Problema |
|---|---|---|---|
| **Compra la marca sin preguntar** | 68% | Lo que dice la receta | Pierde 80% de plata |
| **Pregunta al farmacéutico** | 20% | "¿Hay genérico?" | Depende de honestidad del empleado. La cadena gana más vendiendo la marca |
| **WhatsApp de la farmacia** | 8% | Manda foto, pide precio | Lento (horas). Sin comparación. Sin ubicación |
| **Camina entre farmacias** | 5% | Va a 2-3 locales | 20-40 min cada una. Sin garantía de stock |
| **OPM-DIGEMID** | <2% | Web del MINSA con precios declarados | Escritorio. Sin geo. Precios declarados≠reales |
| **GoodRx (USA)** | 0% en Perú | Muestra precios en farmacias cercanas | **No opera en Perú. Nadie lo hace** |

---

## 3. SOLUCIÓN

```
📲 Paciente manda foto de su receta por WhatsApp
    ↓
🤖 Gemini OCR extrae medicamentos, dosis, médico, hospital
    ↓
💰 App responde con precios reales en farmacias CERCANAS:
   "Losartan 50mg tableta:
    💚 Boticas Arcángel S/0.50 (200m, Jesús María)
    🟠 Mifarma Miraflores S/0.60 (450m)
    🔴 Inkafarma San Isidro S/0.65 (800m)
    Ahorrás S/15.30 este mes"
    ↓
🔔 Recordatorios diarios automáticos (gratis)
    ↓
👨‍👩‍👧 Alerta familiar si olvida (Premium S/7.90/mes)
```

**Qué NO hacemos:** cambiar medicamentos, recomendar dosis, diagnosticar.
**Qué SÍ hacemos:** mostrar precios del MISMO principio activo, misma dosis, misma forma farmacéutica.

---

## 4. NUESTRO APORTE (por qué nosotros y no otros)

| Competidor | Limitación | Nuestra ventaja |
|---|---|---|
| **OPM-DIGEMID** | Web vieja, precios declarados, sin app, sin ubicación | WhatsApp + precios reales crowdsourced + mapa |
| **Apps de farmacias** | Solo sus precios, sin comparación | Todas las farmacias en una pantalla |
| **WhatsApp grupos** | Manual, lento, impreciso | Automático, instantáneo, verificable |
| **Google/Apple Health** | Datos de wearable, sin precios de medicamentos | Conectamos receta → precio → compra → adherencia |
| **GoodRx (USA, $2.6B)** | No opera en Perú ni LATAM | **Llegamos primero a un mercado sin competencia** |

**Nuestro moat real:** el primer dataset longitudinal de precios reales de medicamentos + adherencia en Perú. Eso no lo tiene nadie. Eso no se copia sin tiempo.

---

## 5. PRICING (inspirado en GoodRx)

**GoodRx gana dinero así:** farmacias pagan comisión por cliente enviado + suscripción Gold ($9.99/mes) + PBM fees + ads.

**Nosotros, adaptado a Perú:**

### B2C

| Plan | Precio | Cuándo lo vendés |
|---|---|---|
| **Gratuito** | S/0 | Precios, 3 farmacias cercanas, recordatorio básico. *Siempre gratis.* |
| **Premium** | S/7.90/mes | **Después de mostrar ahorro:** historial completo, PDF para médico, tracking de adherencia, sin ads. "Te ahorré S/51 este mes. ¿Activar Premium por S/7.90?" |
| **Familiar** | S/11.90/mes | 3–5 perfiles, alertas al cuidador, reporte familiar mensual |

### B2B

| Producto | Precio | Cuándo lo vendés |
|---|---|---|
| **Farmacia — Piloto** | **GRATIS** 3 meses | 10 boticas independientes. Sin compromiso |
| **Farmacia — Básico** | S/99/mes | Después del piloto. Listing + analytics básico |
| **Farmacia — Lead** | S/2–5 por lead confirmado | Solo pagan si el paciente va y compra |
| **Farmacia — Destacado** | S/299/mes | Listing patrocinado CLARAMENTE ETIQUETADO, separado del ranking por precio |
| **EPS Dashboard** | S/2,000/mes | **Solo después de 6+ meses de datos.** Adherencia de afiliados + alertas de riesgo poblacional. Sin datos, no se vende |

**Regla #1 del ranking:** menor precio primero. SIEMPRE. Si una farmacia paga, aparece en sección separada etiquetada "Patrocinado". Nunca mezclado.

---

## 6. RIESGOS Y MITIGACIÓN

| Riesgo | Severidad | Mitigación |
|---|---|---|
| **Regulación DIGEMID** | 🔴 ALTO | Solo mostramos MISMO DCI + misma dosis + misma forma. Exactamente lo que DIGEMID permite. NUNCA sugerimos cambiar medicamento, dosis, o principio activo. Losartan 50mg tableta → Losartan 50mg tableta genérico. Nada más. |
| **Privacidad (Ley 29733)** | 🔴 ALTO | Consentimiento explícito en primera interacción. Datos almacenados en Perú. Anonimización para B2B. Política de eliminación. No compartimos datos identificables con farmacias. |
| **Confianza en el ranking** | 🟠 MEDIO | Ranking por MENOR PRECIO siempre. Si hay patrocinado: etiqueta "Patrocinado" en sección aparte. Si el usuario reporta precio incorrecto: se marca y se verifica. |
| **Stock real vs precio declarado** | 🟠 MEDIO | Fase 1: precios de referencia OPM-DIGEMID. Fase 2: crowdsourced de boletas reales de usuarios. Fase 3: farmacias partner confirman stock. Usuario puede reportar "no había" o "precio distinto". |
| **Chicken-and-egg inicial** | 🟠 MEDIO | Los primeros 50 usuarios no verán precios crowdsourced — solo DIGEMID. El valor inicial es el recordatorio + orden. Los precios mejoran con cada boleta subida. |
| **WhatsApp como dependencia** | 🟡 BAJO | Hermes Agent es open-source. Si Meta bloquea, migramos a la app Flutter. WhatsApp es canal de adquisición, no core tech. |
| **Competencia de cadenas grandes** | 🟡 BAJO | Inkafarma/Mifarma ya tienen apps pero solo muestran SUS precios. No les conviene mostrar que la botica de la esquina es más barata. Ese es nuestro espacio. |

---

## 7. FRAMING PARA YC SUMMER 2026

**Lo que YC pide:** *"Intelligent agents analyzing personalized health data to assess disease risk and democratize access to treatments."*

**Nuestro framing:**

> *"Personalized medicine is useless if the patient can't afford the drug and can't remember to take it. In Peru, 68% of chronic patients overpay 80% because they don't know generics exist. Before AI can predict disease risk, someone has to solve LAYER 1: affordability + adherence. SaludApp is GoodRx for Latin America — with a health data layer underneath."*

**Stack de 3 capas:**

```
LAYER 3 — PREDICCIÓN (2028+)
  MOTOR / Delphi propio entrenado con datos peruanos
  "Tu riesgo de ERC en 14 meses: 30%. Intervención sugerida: ajuste de Metformina."

LAYER 2 — PERSONALIZACIÓN (2027)
  BEHRT / CLMBR sobre secuencias de medicamentos, citas, síntomas
  "Tu perfil sugiere consulta endocrinológica este trimestre."

LAYER 1 — ACCESO + ADHERENCIA (AHORA)
  Precios transparentes + recordatorios + alertas familiares
  "Losartan 50mg: S/0.50 en Arcángel (200m). Ahorrás S/51/mes. Recordatorio 8am activado."
```

---

## 8. MÉTRICAS DE ÉXITO (12 meses)

| Métrica | Target |
|---|---|
| Usuarios activos | 1,000 |
| Recetas escaneadas/mes | 3,000 |
| Precios crowdsourced | 5,000+ boletas |
| Ahorro promedio demostrado | S/50+/mes por usuario |
| Conversión a Premium | 5% (desde ahorro, no desde onboarding) |
| Farmacias partner | 20 |
| Tasa de retención mensual | >70% |
| Net Promoter Score | >40 |

---

*SaludApp no reemplaza al médico. SaludApp hace que el tratamiento sea accesible, rastreable y transparente.*
