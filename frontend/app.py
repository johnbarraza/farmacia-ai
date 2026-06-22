"""
SaludApp Peru — Streamlit Frontend (Clean v2)
"""

import os, json, sys, base64
from datetime import datetime, date
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# Cargar keys del .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
# Fallback: cargar del .env de hw7_ds si existe
hw7_env = os.path.join(os.path.dirname(__file__), '..', '..', 'hw7_ds', '.env')
if os.path.exists(hw7_env):
    load_dotenv(hw7_env, override=False)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ai.health_agents import extract_medicines_from_image, buscar_precio_farmacia
from backend.app.health_models import RiskModel, FindriscInput

# ── Config ──
st.set_page_config(page_title="SaludApp", page_icon="💊", layout="wide",
                   initial_sidebar_state="collapsed")

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

@st.cache_data
def load_farmacias():
    return json.loads(Path(DATA_DIR, "farmacias_lima.json").read_text(encoding="utf-8"))

@st.cache_data
def load_medicamentos():
    return json.loads(Path(DATA_DIR, "medicamentos.json").read_text(encoding="utf-8"))["medicamentos"]

farmacias = load_farmacias()
medicamentos_db = load_medicamentos()

# ── CSS Premium Minimalista ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap');

.stApp { background: #0F111A; }
.main { background: #0F111A; color: #FFFFFF; }
h1,h2,h3 { font-family: 'Space Grotesk', sans-serif !important; color: #FFFFFF !important; }
p,li,span,div { font-family: 'Inter', sans-serif !important; color: #C5C6C7; }

/* Sidebar minimal */
section[data-testid="stSidebar"] {
    background: #0B0C10 !important; border-right: 1px solid #1F2833 !important;
}
section[data-testid="stSidebar"] * { color: #FFFFFF !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0; background: #0F111A; border-bottom: 1px solid #1F2833; }
.stTabs [data-baseweb="tab"] {
    background: transparent; border: none; color: #8696A0;
    padding: 12px 24px; font-family: 'Inter', sans-serif; font-size: 14px;
}
.stTabs [aria-selected="true"] {
    background: transparent !important; color: #45F3FF !important;
    font-weight: 600 !important; border-bottom: 2px solid #45F3FF !important;
}

/* Cards */
.card {
    background: #1A1C28; border: 1px solid #2D3142;
    border-radius: 16px; padding: 24px; margin: 12px 0;
}

/* Buttons */
.stButton>button {
    font-family: 'Space Grotesk', sans-serif !important;
    background: #45F3FF !important; color: #0F111A !important;
    border-radius: 50px !important; border: none !important;
    font-weight: 700 !important; padding: 12px 32px !important;
    font-size: 15px !important;
}

/* WhatsApp bubbles */
.whatsapp-container {
    max-width: 480px; margin: 0 auto;
    background: #0B141A; border-radius: 20px; overflow: hidden;
}
.whatsapp-header {
    background: #1F2C33; padding: 14px 20px;
    display: flex; align-items: center; gap: 12px;
}
.whatsapp-body { padding: 16px; min-height: 380px; background: #0B141A; }
.msg-out {
    background: #005C4B; color: #E9EDEF; padding: 10px 14px;
    border-radius: 8px 8px 0 8px; margin: 4px 0 8px 50px;
    max-width: 75%; float: right; clear: both; font-size: 14px;
}
.msg-in {
    background: #1F2C33; color: #E9EDEF; padding: 10px 14px;
    border-radius: 0 8px 8px 8px; margin: 4px 50px 8px 0;
    max-width: 80%; float: left; clear: both; font-size: 14px;
}
.msg-in b { color: #45F3FF; }
.clearfix::after { content: ''; display: table; clear: both; }

/* Price cards */
.price-green { border-left: 4px solid #00FF88 !important; }
.price-red { border-left: 4px solid #FF3333 !important; }
.price-amber { border-left: 4px solid #FFAA00 !important; }

/* Risk score */
.risk-circle {
    width: 140px; height: 140px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto; font-family: 'Space Grotesk', sans-serif;
}

/* Input */
.stTextInput>div>div>input, .stSelectbox>div>div>div {
    background: #1A1C28 !important; border: 1px solid #2D3142 !important;
    border-radius: 12px !important; color: white !important; padding: 10px !important;
}

/* Metrica */
div[data-testid="stMetric"] {
    background: #1A1C28; border: 1px solid #2D3142; border-radius: 12px; padding: 16px;
}
div[data-testid="stMetric"] label { color: #8696A0 !important; }
div[data-testid="stMetric"] div { color: #45F3FF !important; font-family: 'Space Grotesk', sans-serif !important; }

/* Success/Warning/Error */
.stSuccess { background: #0D2818 !important; border-color: #00FF88 !important; }
.stInfo { background: #0D1A28 !important; border-color: #45F3FF !important; }
.stWarning { background: #281A0D !important; border-color: #FFAA00 !important; }

/* Hide Streamlit junk */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar minimal ──
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:20px 0;">
        <div style="font-size:40px;">💊</div>
        <h3 style="margin:8px 0;color:#45F3FF;">SaludApp</h3>
        <small style="color:#8696A0;">GoodRx para Perú</small>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <small style="color:#8696A0;line-height:1.8;">
    🏪 <b>4,200+</b> farmacias en Perú<br>
    💊 <b>1,500+</b> genéricos DIGEMID<br>
    📲 <b>95%</b> de peruanos usa WhatsApp<br>
    💳 <b>15M+</b> usa Yape/Plin<br>
    </small>
    """, unsafe_allow_html=True)
    st.markdown("---")

# ── Tabs ──
t1, t2, t3, t4 = st.tabs(["📲 WhatsApp", "💊 Precios", "📊 Riesgo", "🔮 Futuro"])

# ═══════════════════════════════════════════════════════
# TAB 1: WHATSAPP — el hero
# ═══════════════════════════════════════════════════════
with t1:
    st.markdown('<div class="whatsapp-container">', unsafe_allow_html=True)

    # Header — estilo WhatsApp real
    st.markdown("""
    <div class="whatsapp-header">
        <div style="position:relative;">
            <div style="width:44px;height:44px;border-radius:50%;background:#00A884;
                 display:flex;align-items:center;justify-content:center;font-size:22px;">💊</div>
            <div style="width:12px;height:12px;border-radius:50%;background:#00FF88;
                 border:2px solid #1F2C33;position:absolute;bottom:0;right:0;"></div>
        </div>
        <div style="flex:1;">
            <b style="color:#E9EDEF;font-size:15px;">SaludApp</b><br>
            <small style="color:#8696A0;">en línea · responde al instante</small>
        </div>
        <div style="color:#8696A0;font-size:18px;">⋮</div>
    </div>
    """, unsafe_allow_html=True)

    # Chat
    st.markdown('<div class="whatsapp-body">', unsafe_allow_html=True)

    if "chat" not in st.session_state:
        st.session_state.chat = [
            ("in", "👋 ¡Hola! Soy tu asistente de salud.<br><br>📸 <b>Mandame una foto de tu receta</b> y te digo al instante:<br>• Qué medicamentos tenés que tomar<br>• 💰 Dónde comprarlos más barato<br>• 🔔 Recordatorios automáticos<br><br>También podés escribirme: <b>PRECIOS</b>, <b>RIESGO</b>, <b>FAMILIAR</b>"),
        ]
        st.session_state.wa_meds = None
        st.session_state.wa_ahorro = 0

    for role, text in st.session_state.chat:
        cls = "msg-out" if role == "out" else "msg-in"
        st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)
    st.markdown('<div class="clearfix"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Input area
    st.markdown('<div style="background:#1F2C33;padding:10px 16px;display:flex;gap:8px;align-items:center;border-radius:0 0 20px 20px;">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        uploaded = st.file_uploader("📎", type=["jpg","jpeg","png"], key="wa_upload", label_visibility="collapsed")
    with c2:
        user_text = st.text_input("Mensaje", placeholder="Escribí tu respuesta...", key="wa_text", label_visibility="collapsed")
    with c3:
        send = st.button("📤", key="wa_send", width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Procesar mensaje ──
    if send:

        # Texto
        if user_text.strip():
            txt = user_text.strip().upper()
            st.session_state.chat.append(("out", user_text))

            if txt in ("1","RECORDATORIOS","RECORDATORIO"):
                st.session_state.chat.append(("in",
                    "✅ <b>Recordatorios activados</b><br><br>"
                    "☀️ 8:00 AM — Metformina 500mg (con comida)<br>"
                    "🌙 8:00 PM — Metformina 500mg (con comida)<br>"
                    "🌙 9:00 PM — Atorvastatina 20mg<br><br>"
                    "Te aviso cada día. Sin falta. 🔔"))
            elif txt in ("2","MAPA","MAPA COMPLETO","FARMACIAS"):
                st.session_state.chat.append(("in",
                    "🗺️ <b>Mapa de farmacias cercanas</b><br><br>"
                    "Abrí la pestaña <b>'💊 Precios'</b> para ver el mapa interactivo "
                    "con todas las farmacias y sus precios.<br><br>"
                    "💚 Verde = más barato | 🔴 Rojo = más caro"))
            elif txt in ("3","RIESGO","RIESGO DE SALUD","SALUD"):
                st.session_state.chat.append(("in",
                    "📊 <b>Riesgo de salud</b><br><br>"
                    "Abrí la pestaña <b>'📊 Riesgo'</b> para calcular tu riesgo "
                    "de diabetes tipo 2 con el test FINDRISC (validado OMS).<br><br>"
                    "Sin análisis de sangre. Sin costo."))
            elif txt in ("4","REPORTE","PDF","MEDICO"):
                st.session_state.chat.append(("in",
                    "📄 <b>Reporte para tu médico</b><br><br>"
                    "Abrí la pestaña <b>'📊 Riesgo'</b> y bajá tu reporte completo: "
                    "medicamentos, citas, riesgo, adherencia.<br><br>"
                    "Formato PDF listo para llevar a tu consulta."))
            elif txt in ("FAMILIAR","ALERTAS","HIJA","HIJO"):
                st.session_state.chat.append(("in",
                    "👨‍👩‍👧 <b>Plan Familiar</b><br><br>"
                    "Tu familiar recibe alertas si olvidás tomar tus pastillas.<br><br>"
                    "7 días GRATIS. Después S/11.90 al mes.<br>"
                    "¿WhatsApp de tu contacto?<br>"
                    "Respondé: FAMILIAR +51 987 654 321"))
            elif txt.startswith("FAMILIAR +51"):
                st.session_state.chat.append(("in",
                    "✅ <b>¡Listo!</b> Tu contacto recibirá alertas si olvidás tus pastillas.<br><br>"
                    "Los primeros 7 días son <b>GRATIS</b>.<br>"
                    "Después: S/11.90 al mes vía Yape.<br><br>"
                    "💳 ¿Activar pago ahora? Respondé: <b>YAPE</b>"))
            elif txt in ("YAPE","PAGO","PAGAR"):
                st.session_state.chat.append(("in",
                    "💳 <b>Pago con Yape o Plin</b><br><br>"
                    "Abrí este link para pagar:<br>"
                    "🔗 https://yape.saludapp.pe/pay/11.90<br><br>"
                    "Cuando pagues, respondé: <b>YA</b>"))
            elif txt in ("YA","LISTO","PAGADO"):
                st.session_state.chat.append(("in",
                    "✅ <b>¡Pago confirmado!</b> Plan Familiar activado.<br><br>"
                    "Tu familiar ya recibe alertas. Vos ya tenés:<br>"
                    "• Historial médico completo<br>"
                    "• PDF para tu médico<br>"
                    "• Recordatorios avanzados<br>"
                    "• Seguimiento de adherencia<br><br>"
                    "¡Gracias por confiar en SaludApp! 💊"))
            elif txt in ("HOLA","HI","HOLA!"):
                st.session_state.chat.append(("in",
                    "👋 ¡Hola! Mandame una 📸 <b>foto de tu receta</b> y te digo "
                    "dónde comprar cada pastilla más barato."))
            else:
                st.session_state.chat.append(("in",
                    "No entendí. Intentá con:<br>"
                    "📸 <b>Foto de receta</b> — para ver precios<br>"
                    "1️⃣ <b>RECORDATORIOS</b> — activar alarmas<br>"
                    "2️⃣ <b>MAPA</b> — ver farmacias cercanas<br>"
                    "3️⃣ <b>RIESGO</b> — calcular riesgo de diabetes<br>"
                    "4️⃣ <b>REPORTE</b> — PDF para tu médico<br>"
                    "<b>FAMILIAR</b> — alertas a tu familia"))

        # Foto
        if uploaded:
            st.session_state.chat.append(("out", "📸 <i>[Foto de receta]</i>"))
            with st.spinner("Procesando receta con IA..."):
                img_bytes = uploaded.read()
                ext = (uploaded.name or "img.jpg").rsplit(".",1)[-1].lower()
                img_type = "jpeg" if ext in ("jpg","jpeg") else ext
                result = extract_medicines_from_image(img_bytes, img_type)

                meds = result.get("medicamentos", [])
                fecha = result.get("fecha_documento","")
                medico = result.get("medico_nombre","")
                establecimiento = result.get("establecimiento","")

                respuesta = "✅ Receta procesada"
                if fecha: respuesta += f" · {fecha}"
                if medico: respuesta += f"<br>👨‍⚕️ Dr(a). {medico}"
                if establecimiento: respuesta += f" · 🏥 {establecimiento}"
                respuesta += f"<br><br><b>{len(meds)} medicamentos:</b>"

                ahorro_total = 0
                medicamentos_encontrados = []
                for i, m in enumerate(meds[:5], 1):
                    nombre = m.get("nombre","?")
                    dosis = f" {m['dosis']}" if m.get("dosis") else ""
                    frecuencia = f" · {m['frecuencia']}" if m.get("frecuencia") else ""
                    respuesta += f"<br>{i}️⃣ <b>{nombre}</b>{dosis}{frecuencia}"

                    med_id = nombre.lower().replace(" ","_").replace("á","a").replace("é","e").replace("í","i")
                    for db_med in medicamentos_db:
                        if nombre.lower()[:8] in db_med["nombre"].lower():
                            med_id = db_med["id"]; break
                    precios = buscar_precio_farmacia(med_id, farmacias)
                    if precios:
                        barato = precios[0]; caro = precios[-1]
                        ahorro_total += caro["precio"] - barato["precio"]
                        respuesta += f"<br>   💚 S/{barato['precio']:.2f} en <b>{barato['nombre'][:25]}</b>"

                st.session_state.wa_meds = meds
                st.session_state.wa_ahorro = ahorro_total

                if ahorro_total > 0.01:
                    respuesta += f"<br><br>──────────────<br>💵 <b>Ahorrás ~S/{ahorro_total:.2f}</b> en esta compra"
                else:
                    respuesta += f"<br><br>──────────────<br>📊 Estos medicamentos no están en nuestra base todavía.<br>Tus datos nos ayudan a mejorar. ¡Cada receta cuenta!"

                respuesta += ("<br><br>¿Qué querés hacer?<br>"
                    "1️⃣ <b>RECORDATORIOS</b> (gratis)<br>"
                    "2️⃣ <b>MAPA</b> de farmacias →<br>"
                    "3️⃣ <b>RIESGO</b> de salud →<br>"
                    "4️⃣ <b>REPORTE</b> para tu médico →<br>"
                    "<b>FAMILIAR</b> para alertas a tus contactos")
                st.session_state.chat.append(("in", respuesta))

        if user_text.strip() or uploaded:
            st.rerun()

    # Métricas dinámicas después del chat
    if st.session_state.get("wa_ahorro", 0) > 0:
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        ahorro = st.session_state.wa_ahorro
        ahorro_mes = ahorro * 4
        c1.metric("💰 Ahorro esta compra", f"S/ {ahorro:.2f}")
        n_meds = len(st.session_state.get("wa_meds", []))
        c2.metric("💊 Medicamentos encontrados", n_meds)
        c3.metric("🏪 Farmacias comparadas", "15 (demo)")
    elif len(st.session_state.get("chat",[])) <= 2:
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("🏪 Farmacias en Perú", "4,200+")
        c2.metric("💊 Genéricos DIGEMID", "1,500+")
        c3.metric("⚡ Respuesta OCR", "< 3 seg")

    st.caption("💡 En producción: el usuario comparte su ubicación por WhatsApp. Streamlit no tiene acceso al GPS del navegador. Los precios son reales (DIGEMID). Cobertura demo: 15 farmacias en Lima.")

# ═══════════════════════════════════════════════════════
# TAB 2: PRECIOS — mapa + ranking
# ═══════════════════════════════════════════════════════
with t2:
    st.markdown("### 💊 Comparador de precios de medicamentos")

    col1, col2 = st.columns([1, 2])
    with col1:
        med_buscar = st.selectbox("Medicamento", options=[m["id"] for m in medicamentos_db],
            format_func=lambda x: next((m["nombre"] for m in medicamentos_db if m["id"]==x), x))

        med_info = next((m for m in medicamentos_db if m["id"] == med_buscar), None)
        if med_info:
            ahorro_pct = int((1 - med_info['precio_generico_min'] / med_info['precio_marca']) * 100)
            st.markdown(f"""
            <div class="card">
                <h4>{med_info['nombre']}</h4>
                <small>{med_info['grupo']} · {med_info['frecuencia_tipica']}</small><br><br>
                💚 <b style="color:#00FF88;font-size:1.2em;">Genérico S/{med_info['precio_generico_min']:.2f}–{med_info['precio_generico_max']:.2f}</b><br>
                🔴 <b style="color:#FF3333;">Marca S/{med_info['precio_marca']:.2f}</b> ({med_info['marca_referencia']})<br><br>
                <b style="color:#45F3FF;">Ahorro: hasta {ahorro_pct}%</b><br>
                <small style="color:#8696A0;">vs precio de marca · ahorro real: S/{med_info['precio_marca']-med_info['precio_generico_min']:.2f}/pastilla</small>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        resultados = buscar_precio_farmacia(med_buscar, farmacias)
        if resultados:
            barato = resultados[0]; caro = resultados[-1]
            # Centro aproximado en Lima (Miraflores/San Isidro)
            centro_lat, centro_lng = -12.0931, -77.0353

            m = folium.Map(location=[centro_lat, centro_lng], zoom_start=13,
                          tiles="CartoDB dark_matter", width="100%", height="100%")
            # Marcador de "Tu ubicación aproximada"
            folium.Marker(
                location=[centro_lat, centro_lng],
                popup=folium.Popup("📍 Tu ubicación (aprox.)", max_width=200),
                tooltip="📍 Tu ubicación",
                icon=folium.Icon(color="blue", icon="home", prefix="fa")
            ).add_to(m)
            # Farmacias
            for f in resultados:
                color = "green" if f["precio"] <= barato["precio"]*1.03 else "red" if f["precio"] >= caro["precio"]*0.97 else "orange"
                dist_km = round(((f["lat"]-centro_lat)**2+(f["lng"]-centro_lng)**2)**0.5*111, 1)
                folium.Marker(
                    location=[f["lat"], f["lng"]],
                    popup=folium.Popup(f"<b>{f['nombre']}</b><br>S/ {f['precio']:.2f}<br>~{dist_km} km", max_width=200),
                    tooltip=f"{f['nombre']} S/{f['precio']:.2f}",
                    icon=folium.Icon(color=color, icon="plus-sign", prefix="glyphicon")
                ).add_to(m)
            st_folium(m, width=700, height=420, returned_objects=[])

            st.caption("📍 Demo centrado en San Isidro. En producción: el paciente comparte su ubicación por WhatsApp y el mapa se centra ahí. Streamlit no puede acceder al GPS del navegador.")

            # Ranking
            df = pd.DataFrame(resultados)[["nombre","cadena","distrito","precio"]]
            df.columns = ["Farmacia","Cadena","Distrito","Precio"]
            df["Precio"] = df["Precio"].apply(lambda x: f"S/ {x:.2f}")
            st.dataframe(df, width="stretch", hide_index=True)

# ═══════════════════════════════════════════════════════
# TAB 3: RIESGO — FINDRISC
# ═══════════════════════════════════════════════════════
with t3:
    st.markdown("### 📊 Riesgo de Diabetes Tipo 2")

    col1, col2 = st.columns(2)
    with col1:
        with st.form("findrisc"):
            edad_r = st.radio("Edad", ["Menor 45","45-54","55-64","Mayor 64"], horizontal=True)
            imc_r = st.radio("IMC", ["Normal (<25)","Sobrepeso (25-30)","Obesidad (>30)"], horizontal=True)
            cintura_r = st.radio("Cintura (cm)", ["<94","94-102",">102"] if True else [], horizontal=True)
            act = st.checkbox("Actividad física ≥30 min/día", True)
            frutas = st.checkbox("Frutas/verduras diario", True)
            hta = st.checkbox("Medicación hipertensión", False)
            glucosa = st.checkbox("Glucosa alta anterior", False)
            fam = st.selectbox("Familiar con diabetes", ["Ninguno","Abuelo/tío","Padre/hermano/hijo"])
            if st.form_submit_button("Calcular riesgo", width="stretch"):
                mapper = {"Menor 45":"menor_45","45-54":"45_54","55-64":"55_64","Mayor 64":"mayor_64"}
                mapper2 = {"Normal (<25)":"menor_25","Sobrepeso (25-30)":"25_30","Obesidad (>30)":"mayor_30"}
                mapper3 = {"<94":"menor_94","94-102":"94_102",">102":"mayor_102"}
                mapper4 = {"Ninguno":"ninguno","Abuelo/tío":"abuelo_tio_primo","Padre/hermano/hijo":"padre_hermano_hijo"}
                inp = FindriscInput(edad=mapper[edad_r], imc=mapper2[imc_r],
                    sexo="M", cintura_hombre=mapper3.get(cintura_r),
                    actividad_fisica=act, frutas_verduras_diario=frutas,
                    medicacion_hipertension=hta, glucosa_alta_antes=glucosa,
                    familiar_diabetes=mapper4[fam])
                st.session_state.riesgo = RiskModel().assess(inp)
                st.rerun()

    with col2:
        if "riesgo" in st.session_state:
            r = st.session_state.riesgo
            st.markdown(f"""
            <div style="text-align:center;">
                <div class="risk-circle" style="background:{r.color}20;border:3px solid {r.color};margin:20px auto;">
                    <div>
                        <div style="font-size:3em;font-weight:700;color:{r.color};">{r.score}</div>
                        <div style="font-size:0.9em;color:{r.color};">/26</div>
                    </div>
                </div>
                <h3 style="color:{r.color};">Riesgo {r.nivel}</h3>
                <p>{r.riesgo_porcentaje}</p>
                <div class="card">
                    <p style="color:#C5C6C7;text-align:left;">{r.recomendacion}</p>
                    <small style="color:#8696A0;">📋 {r.siguiente_paso}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👈 Respondé el cuestionario FINDRISC. Sin análisis de sangre. Sin costo.")

# ═══════════════════════════════════════════════════════
# TAB 4: FUTURO — EHR simulation
# ═══════════════════════════════════════════════════════
with t4:
    st.markdown("### 🔮 Cuando tengamos 10,000 pacientes peruanos...")

    if st.button("🧬 Ejecutar simulación", width="stretch"):
        from ai.ehr_simulator import simular_pipeline_completo
        with st.spinner("Simulando BEHRT → MOTOR → Delphi con datos peruanos..."):
            r = simular_pipeline_completo(42)
            p = r["paciente"]
            b = r["behrt"]
            m = r["motor"]
            d = r["delphi"]

        st.markdown(f"""
        <div class="card">
            <h4>👤 Paciente #{p['id']} · {p['edad']} años · {p['sexo']}</h4>
            <small>{' · '.join(dx['nombre'] for dx in p['diagnosticos_actuales'])}</small>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            preds = "<br>".join(f"• {px['codigo']} {px['nombre']}: <b>{px['probabilidad']:.1%}</b>"
                                for px in b.get("predicciones_12m",[])[:3])
            st.markdown(f"""
            <div class="card" style="border-top: 3px solid #45F3FF;">
                <h4>🧬 BEHRT</h4>
                <small>¿Qué enfermedad desarrollará?</small><br><br>
                {preds}
            </div>
            """, unsafe_allow_html=True)
        with c2:
            evs = "<br>".join(f"• {ev['evento'][:40]}<br><b>{ev['probabilidad_12m']:.1%}</b>"
                              for ev in m.get("eventos_competitivos",[])[:2])
            st.markdown(f"""
            <div class="card" style="border-top: 3px solid #FFAA00;">
                <h4>⏱️ MOTOR</h4>
                <small>¿Cuándo se hospitalizará?</small><br><br>
                {evs}
            </div>
            """, unsafe_allow_html=True)
        with c3:
            tray = "<br>".join(f"📅 {t['anno']} · {t['condiciones_acumuladas']} cond. · S/{t['costo_estimado_soles']:,}"
                               for t in d.get("trayectoria_5_annos",[])[:3])
            st.markdown(f"""
            <div class="card" style="border-top: 3px solid #7B1FA2;">
                <h4>🔮 Delphi</h4>
                <small>Trayectoria a 5 años</small><br><br>
                {tray}
            </div>
            """, unsafe_allow_html=True)

        st.info("📋 Estos modelos se entrenan con datos acumulados de SaludApp. El endpoint no cambia — solo se reemplaza el motor interno.")

    st.markdown("""
    ---
    | Fase | Pacientes | Modelo | ¿Qué predice? |
    |---|---|---|---|
    | **Hoy** | 0 | FINDRISC | Riesgo diabetes (8 preguntas) |
    | Fase 2 | 1K+ | XGBoost/Cox | Riesgo desde features tabulares |
    | Fase 3 | 5K+ | BEHRT / FEMR | Próximo diagnóstico probable |
    | Fase 4 | 10K+ | MOTOR | Cuándo ocurrirá cada evento |
    | Fase 5 | 100K+ | Delphi propio | Trayectoria completa a 5+ años |
    """)
