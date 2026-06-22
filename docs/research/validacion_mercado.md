# Validación de Mercado — FarmaciaAI

Fuentes secundarias que respaldan el problema y el tamaño del mercado.

---

## Dispersión de precios — DIGEMID Observatorio

El Observatorio de Precios de Medicamentos de DIGEMID (junio 2026) muestra:

| Medicamento | Precio mín (S/) | Precio máx (S/) | Dispersión |
|---|---|---|---|
| Metformina 500mg (c/u) | 0.10 | 0.48 | 380% |
| Atorvastatina 20mg (c/u) | 0.85 | 3.20 | 276% |
| Losartán 50mg (c/u) | 0.58 | 1.90 | 228% |
| Omeprazol 20mg (c/u) | 0.25 | 0.95 | 280% |
| Amoxicilina 500mg (c/u) | 0.72 | 2.40 | 233% |

*Fuente: DIGEMID — Observatorio de Precios de Medicamentos, Lima Metropolitana, junio 2026.*

---

## Prevalencia de enfermedades crónicas en Perú

- **Diabetes:** 3.2M diagnosticados (MINSA 2024). Prevalencia 9.8% en mayores de 18 años.
- **Hipertensión:** 4.1M (MINSA 2024). 35% de los mayores de 40 años.
- **Dislipidemia:** 2.8M (ENSUSALUD 2023).
- **Superpoblación Lima:** 11.2M habitantes — concentra el 34% de todos los pacientes crónicos del país.

*Fuentes: MINSA NOTI, ENSUSALUD 2023, INEI Perú en cifras 2024.*

---

## Estructura del mercado farmacéutico peruano

- **Mercado total:** $2.8B USD/año (ALAFARPE 2024).
- **Canal retail privado:** 71% del mercado.
- **Concentración:** InRetail (Inkafarma + Mifarma + BTL) controla >55% de puntos de venta formales.
- **Farmacias independientes:** ~18,000 boticas en todo el Perú, ~4,200 en Lima.
- **Penetración digital:** <8% de farmacias independientes tienen presencia digital activa.

*Fuentes: ALAFARPE, DIGEMID Registro de Establecimientos Farmacéuticos 2024.*

---

## Penetración de WhatsApp en Perú

- 94% de usuarios de internet en Perú usa WhatsApp (We Are Social + Hootsuite 2026).
- 78% de mayores de 50 años usa WhatsApp regularmente.
- WhatsApp es la app #1 en tiempo de uso en Perú, superando Facebook e Instagram.

*Fuente: We Are Social Digital Report Perú 2026.*

---

## Validación con pipeline de agentes YC

La idea fue evaluada con el pipeline de validación propio del repositorio [startup-validator-yc](https://github.com/JohnxBar/startup-validator-yc):

- **Score:** 80/100
- **Decisión:** Conditional Go
- **Simulation gate:** 0.30 (bajo — indica mercado no saturado con solución digital en WhatsApp)
- **Fortalezas identificadas:** problema verificable, canal correcto, timing favorable, founder-market fit
- **Gaps a resolver:** datos de precios en tiempo real, escalabilidad del bot

*Ver output completo: `startup-validator-yc/ai/validation_agents/outputs/saludapp-peru-*/`*
