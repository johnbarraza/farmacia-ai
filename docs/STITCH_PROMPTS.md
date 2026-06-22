# Stitch Prompts — SaludApp Peru

## Configuración inicial

En Stitch, elegir: **Mobile App → Flutter** · Dark theme · Spanish (Peru)

---

## Prompt 1: VIBE + CONCEPTO GENERAL

```
A mobile health app for Peruvian patients with chronic diseases (diabetes,
hypertension). The user uploads a photo of their medical prescription and
the app shows where to buy each medicine cheapest nearby.

VIBE: minimalist, premium, dark mode, intuitive. Like a beautifully designed
productivity timer crossed with a medical app. Cyan and green accents on
deep dark backgrounds. Rounded cards with soft shadows. Large readable
typography. One action per screen. Feels calm, trustworthy, premium.

The app has 6 main screens connected in a linear flow:
1. Scan Prescription (camera)
2. Save Money (price comparison)
3. Confirm Purchase (receipt upload)
4. Reminders (daily pill schedule)
5. My Health (risk score + history)
6. Future (AI predictions)

Start by creating the overall design system and Screen 1.
```

---

## Prompt 2: SCREEN 1 — ESCANEAR RECETA

```
Screen 1: "Scan Prescription" — the entry point of the app.

A minimalist camera screen. Top: subtle text "Fotografía tu receta médica"
in Spanish. Center: a large rounded square camera viewfinder with soft
cyan border. Below: three options in a row with icons:
- "📷 Tomar foto" (primary, cyan filled button)
- "🎤 Dictar receta" (secondary, outlined)
- "📁 Galería" (secondary, outlined)

At the very bottom, small text: "Funciona sin internet · Tus datos son tuyos"
with a lock icon. Background: dark (#0F111A). All text in Spanish. Use
the Space Grotesk font for headings.
```

---

## Prompt 3: SCREEN 2 — AHORRAR (PRICE COMPARISON)

```
Screen 2: "Ahorrar" — price comparison after scanning a prescription.

Header displays the scanned medicine name prominently: "💊 Losartan 50mg"

Below, a highlighted card with green left border and subtle green tint
background. This is the CHEAPEST option:
- Pharmacy name: "Boticas Arcángel"
- Price: "S/ 0.33" in large bold green text
- Badge: "AHORRAS 49%" in green
- Subtitle: "Av. Brasil 1520, Jesús María · 200m"
- Small: "⏰ Abierto hasta 11pm"

Below the green card, a compact list of other options (not highlighted):
- "Inkafarma San Isidro — S/0.65" (red, more expensive)
- "Mifarma Miraflores — S/0.60" (amber)

At bottom: "💰 Ahorro mensual: S/51.30" in large cyan text.
Two action buttons side by side:
- "🗺️ VER MAPA" (outlined)
- "✅ YA COMPRÉ" (filled cyan)

Dark background. Cards have rounded corners (12px). Clean typography.
```

---

## Prompt 4: SCREEN 3 — CONFIRMAR COMPRA

```
Screen 3: "Confirmar Compra" — confirming the purchase with a receipt.

Top question: "¿Compraste en Boticas Arcángel?" in friendly Spanish.

Center: an illustration or placeholder area showing a receipt icon with
a dashed border, labeled "📸 Sube la boleta para confirmar el precio real".

Below: a green checkmark card confirming:
- "✅ Precio confirmado: S/0.33"
- "📊 Tu dato ayuda a otros pacientes"
- "💊 Adherencia registrada"

One primary button at bottom: "✅ CONFIRMAR" (green, filled, wide).

Dark background (#0F111A). Clean, simple, no clutter. Feels satisfying —
like checking off a task in a premium to-do app.
```

---

## Prompt 5: SCREEN 4 — RECORDATORIOS (DAILY VIEW)

```
Screen 4: "Recordatorios" — daily pill reminder schedule.

Header: "Hoy, 21 de junio" with a subtle sun icon.

Two time-segmented cards below each other:

First card (morning, left cyan border):
- "☀️ 8:00 AM"
- "Metformina 500mg" in bold
- Subtitle: "Con comida"
- A circular checkmark icon on the right (green, already taken)
- Status: "✅ Tomada"

Second card (evening, amber border):
- "🌙 8:00 PM"
- "Atorvastatina 20mg" in bold
- Subtitle: "Sin comida"
- A circular countdown-style icon on the right (pending)
- Status: "⏳ Pendiente"

Below the cards, a subtle info row:
- "👨‍👩‍👧 Tu hija María recibe alerta si olvidas"

At bottom: a voice input button "🎤 'Tomé mi pastilla'" with microphone icon,
rounded pill shape, cyan outline.

Dark background. Timer/clock aesthetic. Space Grotesk for med names.
```

---

## Prompt 6: SCREEN 5 — MI SALUD (DASHBOARD)

```
Screen 5: "Mi Salud" — personal health dashboard.

Top greeting: "Hola, Juan" in large friendly text.

Three metric cards stacked vertically:

Card 1 — Risk Score (left border colored by severity: amber for moderate):
- "🩺 Riesgo de Diabetes Tipo 2"
- Large number: "14/26" in bold
- Label: "Riesgo Moderado"
- Subtitle: "Última HbA1c: 6.8% (controlado)"
- Mini progress bar showing risk level

Card 2 — Adherence (green left border):
- "💊 Adherencia este mes"
- Horizontal bar chart: "████████░░ 87%"
- Subtitle: "Mejor que el mes pasado ↑"

Card 3 — Report (neutral):
- "📄 Reporte para tu médico"
- "Descargar PDF →" link

Bottom subtle text: "6 meses de datos acumulados · 42 registros"

Dark background. Cards rounded (12px) with soft shadows. Dashboard feel.
```

---

## Prompt 7: SCREEN 6 — FUTURO (AI PREDICTIONS)

```
Screen 6: "Tu Futuro" — AI health predictions.

Top: a subtle glowing gradient background (dark purple/blue radial blur)
to convey "AI / future" feeling.

Main card in center with glowing cyan border:
- "🧬 Predicción personalizada"
- "Con tus datos + 10,000 pacientes peruanos"
- "⏱️ En ~14 meses: 30% probabilidad de complicación renal"
- "💡 Intervención sugerida: ajuste de Metformina"
- "🔒 Datos anonimizados · Modelo entrenado en Perú"

Below: smaller text "Este modelo se activa con ≥10K pacientes usando SaludApp.
Hoy usamos FINDRISC (validado OMS)."

Footer tagline: "Tu data construye el primer modelo de salud peruano."

Dark background with subtle AI/tech aesthetic. Premium, forward-looking feel.
```

---

## Prompt 8: THEME REFINEMENT

```
Apply a consistent dark premium theme across all 6 screens:
- Background: #0F111A (deep navy/black)
- Cards: #1A1C28 with 1px border #2D3142, 12px border radius
- Accent: #45F3FF (cyan) for primary actions, savings, active state
- Success: #00FF88 (green) for completed pills, confirmed purchases, lowest price
- Warning: #FFAA00 (amber) for pending pills, moderate risk
- Danger: #FF3333 (red) for high risk, expensive options
- Text: #FFFFFF for headings, #C5C6C7 for body
- Fonts: Space Grotesk (headings) + Inter (body) + JetBrains Mono (prices/data)
- All buttons: fully rounded (50px), minimum height 48px
- All cards: soft shadow 0px 2px 8px rgba(0,0,0,0.15)
- Input fields: dark background #1A1C28, 2px border #2D3142, rounded 8px
- Icons: use SF Symbols or Material Icons rounded style
- Every screen: minimal, one primary action, no navigation clutter
```

---

## Prompt 9: NAVIGATION + FLOW

```
Add a subtle bottom navigation bar to all screens with 4 icons:
- 📸 (Scan — screen 1)
- 💰 (Save — screens 2-3)
- 🔔 (Reminders — screen 4)
- 📊 (Health — screens 5-6)

The nav bar is dark (#0F111A), icons are white/gray, active icon is cyan.
No text labels, icons only. Height: 56px.

The primary flow is LINEAR (user goes 1→2→3→4→5) but the nav bar allows
jumping between sections. Screen 6 (Future) is accessed from a subtle
link in Screen 5, not the nav bar.

Add a subtle transition animation between screens (slide right).
```

---

## Prompt 10: SPANISH LANGUAGE

```
Switch all text in the app to Spanish (Peru). Keep the same design, fonts,
colors. Ensure all labels, buttons, placeholders, and helper text are in
natural Peruvian Spanish (not neutral/Spain Spanish). Use "tú" not "usted".

Examples of correct Peruvian Spanish:
- "Saca foto a tu receta" not "Tome una fotografía"
- "Ahorras S/51 al mes" not "Ahorra usted"
- "¿Ya compraste?" not "¿Ya ha comprado?"
- "chamba" not needed (keep professional), but use natural shortenings
  like "pa'" only where appropriate for friendly tone.
```

---

## Orden de ejecución en Stitch

1. **Prompt 1** — genera el design system + Screen 1 base
2. **Prompt 8** — afina el theme antes de seguir (evita re-trabajo)
3. **Prompt 2** — Screen 1 refinado
4. **Prompt 3** — Screen 2 (la más importante — el hook de ahorro)
5. **Prompt 4** — Screen 3
6. **Prompt 5** — Screen 4
7. **Prompt 6** — Screen 5
8. **Prompt 7** — Screen 6 (pitch closer)
9. **Prompt 9** — Navegación
10. **Prompt 10** — Idioma español peruano

**Cada prompt = 1 cambio claro. No mezclar screens. Deja que Stitch procese antes del siguiente.**
