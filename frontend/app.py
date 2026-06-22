"""FarmaciaAI — Streamlit Frontend"""

import os, json, sys, base64
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ai.health_agents import extract_medicines_from_image, buscar_precio_farmacia
from backend.app.health_models import RiskModel, FindriscInput

st.set_page_config(page_title="FarmaciaAI", page_icon="💊", layout="wide",
                   initial_sidebar_state="collapsed")

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

@st.cache_data
def load_farmacias():
    return json.loads(Path(DATA_DIR, "farmacias_lima.json").read_text(encoding="utf-8"))

@st.cache_data
def load_medicamentos():
    return json.loads(Path(DATA_DIR, "medicamentos.json").read_text(encoding="utf-8"))["medicamentos"]

farmacias    = load_farmacias()
meds_db      = load_medicamentos()

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap');

.stApp { background: #0F111A; }
h1,h2,h3,h4 { font-family:'Space Grotesk',sans-serif !important; color:#FFFFFF !important; }
p,li,span { font-family:'Inter',sans-serif !important; color:#C5C6C7; }

.stTabs [data-baseweb="tab-list"] { background:#0F111A; border-bottom:1px solid #1F2833; }
.stTabs [data-baseweb="tab"] { background:transparent; color:#8696A0; padding:12px 24px; font-family:'Inter',sans-serif; }
.stTabs [aria-selected="true"] { color:#00D4FF !important; font-weight:600 !important; border-bottom:2px solid #00D4FF !important; }

.stButton>button {
    background:#00D4FF !important; color:#0F111A !important;
    border-radius:50px !important; border:none !important;
    font-weight:700 !important; font-family:'Space Grotesk',sans-serif !important;
}
.stButton>button:hover { background:#00AACC !important; }

.card {
    background:#1A1C28; border:1px solid #2D3142;
    border-radius:16px; padding:20px; margin:10px 0;
}

/* Chat nativo */
[data-testid="stChatMessage"] {
    background:#1A1C28 !important; border-radius:12px !important;
    border:1px solid #2D3142 !important; margin:6px 0 !important;
}
[data-testid="stChatInput"] textarea {
    background:#1A1C28 !important; border:1px solid #2D3142 !important;
    color:white !important; border-radius:12px !important;
}

div[data-testid="stMetric"] {
    background:#1A1C28; border:1px solid #2D3142; border-radius:12px; padding:16px;
}
div[data-testid="stMetric"] label { color:#8696A0 !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#00D4FF !important; font-family:'Space Grotesk',sans-serif !important; }

.stTextInput>div>div>input, .stSelectbox>div>div>div {
    background:#1A1C28 !important; border:1px solid #2D3142 !important;
    color:white !important; border-radius:12px !important;
}
.stSelectbox [data-baseweb="select"] { background:#1A1C28 !important; }

.price-best  { border-left:4px solid #00FF88 !important; }
.price-worst { border-left:4px solid #FF4444 !important; }
.price-mid   { border-left:4px solid #FFAA00 !important; }

.risk-circle {
    width:140px; height:140px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    margin:0 auto; font-family:'Space Grotesk',sans-serif;
}
#MainMenu, footer, header[data-testid="stHeader"] { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:16px 0 8px;">
    <h2 style="margin:0;">💊 FarmaciaAI</h2>
    <p style="margin:0;color:#8696A0;font-size:14px;">
        Encontrá el medicamento más barato cerca tuyo · Lima, Perú
    </p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("🏪 Farmacias Lima", "15 (demo)")
c2.metric("💊 Medicamentos", "20 genéricos")
c3.metric("⚡ OCR receta", "< 3 seg")

st.markdown("---")

t1, t2, t3, t4 = st.tabs(["💬 Demo Chat", "💊 Comparar Precios", "📊 Riesgo Diabetes", "🔮 Roadmap IA"])

# ═══════════════════════════════════════════════════════
# TAB 1: CHAT — usando componentes nativos de Streamlit
# ═══════════════════════════════════════════════════════
with t1:

    # Inicializar historial
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": (
                "👋 Hola! Soy **FarmaciaAI**, tu asistente de salud.\n\n"
                "📸 Subí una foto de tu receta y te digo dónde comprar más barato.\n\n"
                "O escribime:\n"
                "- **PRECIOS** → comparar medicamentos\n"
                "- **RIESGO** → test de diabetes\n"
                "- **RECORDATORIOS** → activar alarmas\n"
                "- **FAMILIAR** → alertas para tu familia"
            )}
        ]

    col_chat, col_upload = st.columns([3, 1])

    with col_upload:
        st.markdown("**📸 Subir receta**")
        uploaded = st.file_uploader(
            "Foto de receta médica",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
            key="receipt_upload"
        )
        if uploaded:
            st.image(uploaded, caption="Receta cargada", use_column_width=True)
            if st.button("🔍 Analizar receta", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "📸 [Foto de receta]"})
                with st.spinner("Procesando con Gemini Vision..."):
                    img_bytes = uploaded.read()
                    ext = (uploaded.name or "img.jpg").rsplit(".", 1)[-1].lower()
                    img_type = "jpeg" if ext in ("jpg", "jpeg") else ext
                    result = extract_medicines_from_image(img_bytes, img_type)
                    meds = result.get("medicamentos", [])

                    if meds:
                        resp = f"✅ **{len(meds)} medicamento(s) encontrado(s):**\n\n"
                        ahorro = 0
                        for i, m in enumerate(meds[:5], 1):
                            nombre = m.get("nombre", "?")
                            dosis = f" {m['dosis']}" if m.get("dosis") else ""
                            resp += f"**{i}. {nombre}{dosis}**\n"
                            med_id = nombre.lower().replace(" ", "_")
                            for db_m in meds_db:
                                if nombre.lower()[:6] in db_m["nombre"].lower():
                                    med_id = db_m["id"]; break
                            precios = buscar_precio_farmacia(med_id, farmacias)
                            if precios:
                                b = precios[0]; c_p = precios[-1]
                                ahorro += c_p["precio"] - b["precio"]
                                resp += f"   💚 S/{b['precio']:.2f} en {b['nombre'][:30]}\n"
                                resp += f"   🔴 S/{c_p['precio']:.2f} en {c_p['nombre'][:30]}\n"
                            resp += "\n"
                        if ahorro > 0.01:
                            resp += f"---\n💵 **Ahorrás ~S/{ahorro:.2f}** eligiendo la farmacia correcta\n\n"
                        resp += "¿Querés activar **RECORDATORIOS** para estas pastillas?"
                    else:
                        resp = "❌ No pude leer la receta. Intentá con una foto con mejor luz y enfoque."

                st.session_state.messages.append({"role": "assistant", "content": resp})
                st.rerun()

    with col_chat:
        # Mostrar historial
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="💊" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])

        # Input de texto
        if prompt := st.chat_input("Escribí tu mensaje o una palabra clave..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            txt = prompt.strip().upper()

            # Respuestas deterministas
            if txt in ("HOLA", "HI", "HELLO", "BUENAS"):
                resp = ("👋 ¡Hola! Podés:\n\n"
                        "📸 Subir foto de receta (columna derecha)\n"
                        "💊 Ir a **Comparar Precios**\n"
                        "📊 Ir a **Riesgo Diabetes**\n"
                        "O escribirme: **PRECIOS**, **RIESGO**, **RECORDATORIOS**, **FAMILIAR**")
            elif txt in ("PRECIOS", "PRECIO", "FARMACIA", "FARMACIAS", "DONDE", "2", "MAPA"):
                resp = "🗺️ Abrí la pestaña **💊 Comparar Precios** para ver el mapa interactivo con precios en tiempo real de 15 farmacias en Lima."
            elif txt in ("RIESGO", "DIABETES", "GLUCOSA", "AZUCAR", "3"):
                resp = "📊 Abrí la pestaña **📊 Riesgo Diabetes** para el test FINDRISC (validado OMS). Sin análisis de sangre. Resultado en 2 minutos."
            elif txt in ("RECORDATORIOS", "RECORDATORIO", "ALARMA", "ALARMAS", "1"):
                resp = ("✅ **Recordatorios activados** (demo)\n\n"
                        "☀️ 8:00 AM — Pastilla con desayuno\n"
                        "🌙 9:00 PM — Pastilla con cena\n\n"
                        "En producción: te llega por WhatsApp todos los días.")
            elif txt in ("FAMILIAR", "FAMILIA", "HIJO", "HIJA", "ALERTAS"):
                resp = ("👨‍👩‍👧 **Plan Familiar**\n\n"
                        "Tu familiar recibe una alerta si olvidás tomar tus pastillas.\n\n"
                        "7 días gratis → S/14.90/mes\n"
                        "¿Cuál es el número de WhatsApp de tu familiar?")
            elif txt in ("GRACIAS", "THANK", "OK", "GENIAL"):
                resp = "😊 ¡De nada! Si necesitás algo más, aquí estoy."
            elif txt in ("REPORTE", "PDF", "INFORME", "4"):
                resp = "📄 Abrí la pestaña **📊 Riesgo** → completá el test → descargá el PDF para tu médico."
            else:
                resp = ("No entendí bien. Probá con:\n\n"
                        "- **PRECIOS** → comparar farmacias\n"
                        "- **RIESGO** → test de diabetes\n"
                        "- **RECORDATORIOS** → alarmas de pastillas\n"
                        "- **FAMILIAR** → alertas a tu familia\n\n"
                        "O subí una 📸 foto de tu receta (columna derecha).")

            st.session_state.messages.append({"role": "assistant", "content": resp})
            with st.chat_message("assistant", avatar="💊"):
                st.markdown(resp)

# ═══════════════════════════════════════════════════════
# TAB 2: PRECIOS
# ═══════════════════════════════════════════════════════
with t2:
    st.markdown("### 💊 Comparador de Precios de Medicamentos")
    st.caption("Compará precios de genéricos en 15 farmacias de Lima. Fuente: DIGEMID.")

    col1, col2 = st.columns([1, 2])
    with col1:
        med_sel = st.selectbox(
            "Seleccioná el medicamento",
            options=[m["id"] for m in meds_db],
            format_func=lambda x: next((m["nombre"] for m in meds_db if m["id"] == x), x)
        )
        med_info = next((m for m in meds_db if m["id"] == med_sel), None)
        if med_info:
            ahorro_pct = int((1 - med_info["precio_generico_min"] / med_info["precio_marca"]) * 100)
            st.markdown(f"""
            <div class="card">
                <h4>{med_info['nombre']}</h4>
                <small style="color:#8696A0;">{med_info['grupo']} · {med_info['frecuencia_tipica']}</small>
                <hr style="border-color:#2D3142;">
                <p>💚 <b style="color:#00FF88;">Genérico: S/{med_info['precio_generico_min']:.2f}–{med_info['precio_generico_max']:.2f}</b></p>
                <p>🔴 <b style="color:#FF4444;">Marca ({med_info['marca_referencia']}): S/{med_info['precio_marca']:.2f}</b></p>
                <p style="color:#00D4FF;font-size:1.1em;font-weight:700;">Ahorrás hasta {ahorro_pct}%</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        resultados = buscar_precio_farmacia(med_sel, farmacias)
        if resultados:
            barato = resultados[0]
            caro   = resultados[-1]
            centro = [-12.0931, -77.0353]

            m_map = folium.Map(location=centro, zoom_start=13, tiles="CartoDB dark_matter")
            folium.Marker(centro,
                popup="📍 Tu ubicación (demo)",
                tooltip="📍 Tu ubicación",
                icon=folium.Icon(color="blue", icon="home", prefix="fa")
            ).add_to(m_map)

            for f in resultados:
                if f["precio"] <= barato["precio"] * 1.03:
                    color = "green"
                elif f["precio"] >= caro["precio"] * 0.97:
                    color = "red"
                else:
                    color = "orange"
                folium.Marker(
                    [f["lat"], f["lng"]],
                    popup=folium.Popup(f"<b>{f['nombre']}</b><br>S/ {f['precio']:.2f}", max_width=200),
                    tooltip=f"{f['nombre']} — S/{f['precio']:.2f}",
                    icon=folium.Icon(color=color, icon="plus-sign", prefix="glyphicon")
                ).add_to(m_map)

            st_folium(m_map, width=700, height=400, returned_objects=[])
            st.caption("💚 Verde = más barato · 🔴 Rojo = más caro · 📍 Ubicación demo (San Isidro)")

            df = pd.DataFrame(resultados)[["nombre", "cadena", "distrito", "precio"]]
            df.columns = ["Farmacia", "Cadena", "Distrito", "Precio (S/)"]
            df["Precio (S/)"] = df["Precio (S/)"].apply(lambda x: f"S/ {x:.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════
# TAB 3: RIESGO FINDRISC
# ═══════════════════════════════════════════════════════
with t3:
    st.markdown("### 📊 Test de Riesgo de Diabetes Tipo 2")
    st.caption("Cuestionario FINDRISC validado por la OMS. Sin análisis de sangre.")

    col1, col2 = st.columns(2)
    with col1:
        with st.form("findrisc_form"):
            edad_r    = st.radio("Edad", ["Menor 45", "45-54", "55-64", "Mayor 64"], horizontal=True)
            imc_r     = st.radio("IMC", ["Normal (<25)", "Sobrepeso (25-30)", "Obesidad (>30)"], horizontal=True)
            cintura_r = st.radio("Cintura (cm)", ["<94", "94-102", ">102"], horizontal=True)
            act       = st.checkbox("Actividad física ≥ 30 min/día", value=True)
            frutas    = st.checkbox("Frutas/verduras diario", value=True)
            hta       = st.checkbox("Medicación para hipertensión")
            glucosa   = st.checkbox("Glucosa alta en análisis anteriores")
            fam       = st.selectbox("Familiar con diabetes",
                            ["Ninguno", "Abuelo/tío/primo", "Padre/hermano/hijo"])
            submitted = st.form_submit_button("Calcular mi riesgo →", use_container_width=True)

        if submitted:
            m_edad    = {"Menor 45": "menor_45", "45-54": "45_54", "55-64": "55_64", "Mayor 64": "mayor_64"}
            m_imc     = {"Normal (<25)": "menor_25", "Sobrepeso (25-30)": "25_30", "Obesidad (>30)": "mayor_30"}
            m_cintura = {"<94": "menor_94", "94-102": "94_102", ">102": "mayor_102"}
            m_fam     = {"Ninguno": "ninguno", "Abuelo/tío/primo": "abuelo_tio_primo", "Padre/hermano/hijo": "padre_hermano_hijo"}
            inp = FindriscInput(
                edad=m_edad[edad_r], imc=m_imc[imc_r], sexo="M",
                cintura_hombre=m_cintura.get(cintura_r),
                actividad_fisica=act, frutas_verduras_diario=frutas,
                medicacion_hipertension=hta, glucosa_alta_antes=glucosa,
                familiar_diabetes=m_fam[fam]
            )
            st.session_state.riesgo = RiskModel().assess(inp)
            st.rerun()

    with col2:
        if "riesgo" in st.session_state:
            r = st.session_state.riesgo
            st.markdown(f"""
            <div style="text-align:center;padding:20px 0;">
                <div class="risk-circle" style="background:{r.color}20;border:3px solid {r.color};">
                    <div>
                        <div style="font-size:3em;font-weight:700;color:{r.color};">{r.score}</div>
                        <div style="font-size:0.85em;color:{r.color};">/26 puntos</div>
                    </div>
                </div>
                <h3 style="color:{r.color};margin-top:16px;">Riesgo {r.nivel}</h3>
                <p style="color:#C5C6C7;">{r.riesgo_porcentaje}</p>
            </div>
            <div class="card">
                <p style="color:#C5C6C7;">{r.recomendacion}</p>
                <small style="color:#8696A0;">📋 {r.siguiente_paso}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👈 Completá el cuestionario para ver tu resultado.")

# ═══════════════════════════════════════════════════════
# TAB 4: ROADMAP IA
# ═══════════════════════════════════════════════════════
with t4:
    st.markdown("### 🔮 Roadmap de Modelos de IA")
    st.markdown("""
    <div class="card">
        <p style="color:#C5C6C7;">
            FarmaciaAI empieza con reglas simples y escala a modelos más sofisticados
            a medida que acumula datos de pacientes peruanos reales.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
| Fase | Pacientes | Modelo | ¿Qué predice? | Estado |
|---|---|---|---|---|
| **Ahora** | 0–1K | FINDRISC (OMS) | Riesgo diabetes en 8 preguntas | ✅ Live |
| Fase 2 | 1K–5K | XGBoost / Cox | Riesgo desde historial de recetas | 🔨 Building |
| Fase 3 | 5K–10K | BEHRT / CLMBR | Próximo diagnóstico probable | 📋 Planned |
| Fase 4 | 10K–50K | MOTOR | Cuándo ocurrirá cada evento | 📋 Planned |
| Fase 5 | 100K+ | Delphi propio | Trayectoria completa a 5+ años | 🔮 Vision |
    """)

    st.markdown("---")
    st.markdown("### 🧬 Simulación (datos sintéticos)")
    if st.button("▶️ Simular pipeline BEHRT → MOTOR → Delphi", use_container_width=True):
        from ai.ehr_simulator import simular_pipeline_completo
        with st.spinner("Simulando con datos sintéticos peruanos..."):
            r = simular_pipeline_completo(42)
            p = r["paciente"]; b = r["behrt"]; mo = r["motor"]; d = r["delphi"]

        st.markdown(f"""
        <div class="card">
            <h4>👤 Paciente #{p['id']} · {p['edad']} años · {p['sexo']}</h4>
            <small style="color:#8696A0;">{' · '.join(dx['nombre'] for dx in p['diagnosticos_actuales'])}</small>
        </div>
        """, unsafe_allow_html=True)

        ca, cb, cc = st.columns(3)
        with ca:
            preds = "\n".join(f"- {px['codigo']} {px['nombre']}: **{px['probabilidad']:.1%}**"
                              for px in b.get("predicciones_12m", [])[:3])
            st.markdown(f"""<div class="card" style="border-top:3px solid #00D4FF;">
                <h4>🧬 BEHRT</h4><small>¿Qué enfermedad?</small><br><br>{preds}</div>""",
                unsafe_allow_html=True)
        with cb:
            evs = "\n".join(f"- {ev['evento'][:35]}: **{ev['probabilidad_12m']:.1%}**"
                            for ev in mo.get("eventos_competitivos", [])[:2])
            st.markdown(f"""<div class="card" style="border-top:3px solid #FFAA00;">
                <h4>⏱️ MOTOR</h4><small>¿Cuándo?</small><br><br>{evs}</div>""",
                unsafe_allow_html=True)
        with cc:
            tray = "\n".join(f"- {t['anno']}: {t['condiciones_acumuladas']} cond · S/{t['costo_estimado_soles']:,}"
                             for t in d.get("trayectoria_5_annos", [])[:3])
            st.markdown(f"""<div class="card" style="border-top:3px solid #AA44FF;">
                <h4>🔮 Delphi</h4><small>Trayectoria 5 años</small><br><br>{tray}</div>""",
                unsafe_allow_html=True)

        st.info("Estos modelos se entrenan con datos acumulados de FarmaciaAI. El endpoint de la API no cambia — solo se reemplaza el motor interno.")
