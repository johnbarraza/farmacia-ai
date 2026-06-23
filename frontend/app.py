"""FarmaciaAI — Streamlit Frontend"""

import os, json, sys, base64, time
from pathlib import Path
import streamlit as st

# set_page_config DEBE ser el primer comando Streamlit — antes de cualquier st.*
st.set_page_config(page_title="FarmaciaAI", page_icon="💊", layout="wide",
                   initial_sidebar_state="collapsed")

import folium
from streamlit_folium import st_folium
import pandas as pd

# Cargar secrets: primero .env local, luego st.secrets (Streamlit Cloud)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass

for key in ("GEMINI_API_KEY", "DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY"):
    if not os.getenv(key):
        try:
            val = st.secrets.get(key)
            if val:
                os.environ[key] = val
        except Exception:
            pass

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ai.health_agents import extract_medicines_from_image, buscar_precio_farmacia, fuzzy_med_id
from backend.app.health_models import RiskModel, FindriscInput

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

@st.cache_data
def load_farmacias():
    return json.loads(Path(DATA_DIR, "farmacias_lima.json").read_text(encoding="utf-8"))

@st.cache_data
def load_medicamentos():
    return json.loads(Path(DATA_DIR, "medicamentos.json").read_text(encoding="utf-8"))["medicamentos"]

@st.cache_data
def load_digemid():
    p = Path(DATA_DIR, "digemid_index.json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return []

farmacias    = load_farmacias()
meds_db      = load_medicamentos()
digemid_db   = load_digemid()

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap');

.stApp { background: #0F111A; }
h1,h2,h3,h4 { font-family:'Space Grotesk',sans-serif !important; color:#FFFFFF !important; }
/* scope to markdown content only — never touch Streamlit internal spans */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stCaptionContainer"] p { font-family:'Inter',sans-serif !important; color:#C5C6C7; }

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

/* ── Fix: file uploader "uploadpload" overlap ── */
[data-testid="stFileUploaderDropzoneInstructions"] { display:none !important; }
[data-testid="stFileUploaderDropzone"] {
    padding: 10px 8px !important;
    justify-content: center !important;
}
[data-testid="stFileUploaderDropzone"] button {
    width: 100% !important;
    background: #1A1C28 !important;
    color: #00D4FF !important;
    border: 1px dashed #00D4FF !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* ── Fix: expander text overlap in Riesgo tab ── */
details[data-testid="stExpander"] > summary {
    position: relative !important;
    z-index: 1 !important;
    padding: 10px 12px !important;
}
details[data-testid="stExpander"] > summary span {
    position: static !important;
    color: #C5C6C7 !important;
}
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
c1.metric("🏪 Farmacias en Lima", "4,200+")
c2.metric("💊 Registrados DIGEMID", f"{len(digemid_db):,}")
c3.metric("⚡ OCR con Gemini Vision", "< 5 seg")
st.caption("Demo activo: 15 farmacias con precios comparados · 20 medicamentos crónicos · Catálogo DIGEMID actualizado 19/06/2026")

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
                "👋 Hola! Soy **FarmaciaAI** 💊\n\n"
                "Te ayudo a **ahorrar en medicamentos** en Lima al instante.\n\n"
                "1️⃣ 📸 **Foto de receta** → precios comparados\n"
                "2️⃣ 🎤 **Audio** → describime el medicamento\n"
                "3️⃣ 🗺️ **MAPA** → farmacias cercanas\n"
                "4️⃣ 📊 **RIESGO** → test de diabetes (OMS)\n"
                "5️⃣ 👨‍👩‍👧 **FAMILIAR** → alertas a tu familia\n\n"
                "Subí una foto de tu receta o escribime para empezar 🚀"
            )}
        ]

    col_chat, col_upload = st.columns([3, 2])

    with col_upload:
        st.markdown("**📸 Subir receta**")

        engine = st.radio(
            "Motor OCR",
            ["Auto", "Gemini Vision", "PaddleOCR + DeepSeek", "Mock (demo)"],
            index=0,
            help="Auto usa la mejor opción disponible según tus API keys"
        )
        engine_map = {
            "Auto": "auto",
            "Gemini Vision": "gemini",
            "PaddleOCR + DeepSeek": "paddleocr+deepseek",
            "Mock (demo)": "mock"
        }

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
                t0 = time.time()
                with st.spinner(f"Procesando con {engine}..."):
                    img_bytes = uploaded.read()
                    ext = (uploaded.name or "img.jpg").rsplit(".", 1)[-1].lower()
                    img_type = "jpeg" if ext in ("jpg", "jpeg") else ext
                    result = extract_medicines_from_image(img_bytes, img_type, engine=engine_map[engine])
                elapsed = time.time() - t0
                meds = result.get("medicamentos", [])
                raw_ocr = result.get("_raw_ocr", "")
                fuente = result.get("fuente_ocr", engine)  # campo real del resultado
                es_mock = fuente == "demo_mock"
                motor_label = "⚠️ DEMO (PaddleOCR no instalado)" if es_mock else fuente

                if meds:
                    st.session_state.ocr_meds = meds
                    resp = f"✅ **{len(meds)} medicamento(s) encontrado(s):**\n\n"
                    ahorro = 0
                    for i, m in enumerate(meds[:5], 1):
                        nombre = m.get("nombre", "?")
                        dosis = f" {m['dosis']}" if m.get("dosis") else ""
                        frec  = f" · {m['frecuencia']}" if m.get("frecuencia") else ""
                        resp += f"**{i}. {nombre}{dosis}**{frec}\n"

                        med_id = fuzzy_med_id(nombre, meds_db)
                        precios = buscar_precio_farmacia(med_id, farmacias)
                        if precios:
                            b = precios[0]; c_p = precios[-1]
                            ahorro += c_p["precio"] - b["precio"]
                            resp += f"   💚 S/{b['precio']:.2f} en {b['nombre'][:28]} (~{b['dist_km']} km)\n"
                            resp += f"   🔴 S/{c_p['precio']:.2f} en {c_p['nombre'][:28]} (~{c_p['dist_km']} km)\n"
                        else:
                            resp += f"   ℹ️ No encontrado en DB — buscá en [Inkafarma](https://inkafarma.pe/buscador?keyword={nombre.replace(' ', '+')})\n"
                        resp += "\n"

                    if ahorro > 0.01:
                        resp += f"---\n💵 **Ahorrás ~S/{ahorro:.2f}** eligiendo la farmacia correcta\n\n"

                    filtrados = result.get("_filtrados_digemid", [])
                    if filtrados:
                        resp += f"⚠️ Filtrados (no son medicamentos DIGEMID): {', '.join(filtrados)}\n\n"

                    resp += "¿Querés activar **RECORDATORIOS** para estas pastillas?\nEscribí **SI** para activar."
                else:
                    resp = "❌ No pude leer los medicamentos. Intentá con mejor luz o cambiá el motor OCR."

                resp += f"\n\n`⏱ {elapsed:.1f}s · {motor_label}`"
                if es_mock:
                    resp += "\n> ⚠️ Datos de demo. Para OCR real usá Gemini Vision."

                if raw_ocr:
                    with st.expander("📄 Texto extraído por PaddleOCR"):
                        st.code(raw_ocr)

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
            elif txt in ("1", "2", "RECETA", "FOTO", "AUDIO"):
                resp = "📸 Subí la foto de tu receta en la sección derecha (📤 subir imagen). Te extraigo los medicamentos y comparo precios al instante."
            elif txt in ("PRECIOS", "PRECIO", "FARMACIA", "FARMACIAS", "DONDE", "3", "MAPA"):
                resp = "🗺️ Abrí la pestaña **💊 Comparar Precios** para ver el mapa interactivo con precios en tiempo real de 15 farmacias en Lima."
            elif txt in ("RIESGO", "DIABETES", "GLUCOSA", "AZUCAR", "4"):
                resp = "📊 Abrí la pestaña **📊 Riesgo Diabetes** para el test FINDRISC (validado OMS). Sin análisis de sangre. Resultado en 2 minutos."
            elif txt in ("RECORDATORIOS", "RECORDATORIO", "ALARMA", "ALARMAS"):
                resp = ("✅ **Recordatorios activados** (demo)\n\n"
                        "☀️ 8:00 AM — Pastilla con desayuno\n"
                        "🌙 9:00 PM — Pastilla con cena\n\n"
                        "En producción: te llega por WhatsApp todos los días.")
            elif txt in ("FAMILIAR", "FAMILIA", "HIJO", "HIJA", "ALERTAS", "5"):
                resp = ("👨‍👩‍👧 **Plan Familiar**\n\n"
                        "Tu familiar recibe una alerta si olvidás tomar tus pastillas.\n\n"
                        "7 días gratis → S/14.90/mes\n"
                        "¿Cuál es el número de WhatsApp de tu familiar?")
            elif txt in ("SI", "SÍ", "YES", "DALE", "OK RECORDATORIOS"):
                meds_rec = st.session_state.get("ocr_meds", [])
                if meds_rec:
                    nombres = [m.get("nombre", "?") for m in meds_rec[:5]]
                    lista = "\n".join(f"☀️ 8:00 AM — {n}" for n in nombres)
                    resp = (f"✅ **Recordatorios activados para {len(nombres)} medicamento(s):**\n\n"
                            f"{lista}\n\n"
                            f"En producción: te llego por WhatsApp todos los días. 🔔\n\n"
                            f"¿Querés también el **REPORTE** PDF para tu médico?")
                else:
                    resp = ("✅ **Recordatorios activados** (demo)\n\n"
                            "☀️ 8:00 AM — Pastilla con desayuno\n"
                            "🌙 9:00 PM — Pastilla con cena\n\n"
                            "En producción: te llega por WhatsApp todos los días. 🔔")
            elif txt in ("GRACIAS", "THANK", "GENIAL"):
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

    # Medicamentos detectados por OCR
    ocr_meds = st.session_state.get("ocr_meds", [])
    if ocr_meds:
        st.markdown("**📸 Medicamentos de tu última receta:**")
        cols = st.columns(len(ocr_meds[:5]))
        for i, (col, m) in enumerate(zip(cols, ocr_meds[:5])):
            nombre = m.get("nombre", "?")
            dosis  = m.get("dosis", "")
            with col:
                med_id = nombre.lower().replace(" ", "_")
                for db_m in meds_db:
                    if nombre.lower()[:6] in db_m["nombre"].lower():
                        med_id = db_m["id"]; break
                precios = buscar_precio_farmacia(med_id, farmacias)
                precio_str = f"S/{precios[0]['precio']:.2f}" if precios else "No en DB"
                st.markdown(f"""<div class="card" style="text-align:center;padding:12px;">
                    <b style="color:#00D4FF;">{nombre}</b><br>
                    <small style="color:#8696A0;">{dosis}</small><br><br>
                    <b style="color:#00FF88;font-size:1.1em;">{precio_str}</b><br>
                    <small style="color:#8696A0;">más barato</small>
                </div>""", unsafe_allow_html=True)
        st.markdown("---")

    # ── Filtros ──────────────────────────────────────────────────────────────
    todos_distritos = sorted(set(f["distrito"] for f in farmacias))
    todas_cadenas   = sorted(set(f["cadena"] for f in farmacias))

    fa, fb = st.columns([1, 1])
    with fa:
        distritos_sel = st.multiselect(
            "📍 Filtrar por distrito",
            options=todos_distritos,
            default=[],
            placeholder="Todos los distritos (15)"
        )
    with fb:
        cadenas_sel = st.multiselect(
            "🏪 Filtrar por cadena",
            options=todas_cadenas,
            default=[],
            placeholder="Todas las cadenas (7)"
        )

    farmacias_filtradas = [
        f for f in farmacias
        if (not distritos_sel or f["distrito"] in distritos_sel)
        and (not cadenas_sel or f["cadena"] in cadenas_sel)
    ]
    st.caption(f"Mostrando {len(farmacias_filtradas)} de 15 farmacias · "
               f"Distritos: {', '.join(distritos_sel) if distritos_sel else 'todos'}")

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
            unidad     = med_info.get("presentacion", "unidad").lower()
            caja30_min = med_info["precio_generico_min"] * 30
            caja30_max = med_info["precio_generico_max"] * 30
            caja30_marca = med_info["precio_marca"] * 30
            st.markdown(f"""
            <div class="card">
                <h4>{med_info['nombre']}</h4>
                <small style="color:#8696A0;">{med_info['grupo']} · {med_info['frecuencia_tipica']}</small>
                <hr style="border-color:#2D3142;">
                <p>💚 <b style="color:#00FF88;">Genérico: S/{med_info['precio_generico_min']:.2f}–{med_info['precio_generico_max']:.2f} / {unidad}</b><br>
                <small style="color:#8696A0;">Caja 30 {unidad}s ≈ S/{caja30_min:.2f}–{caja30_max:.2f}</small></p>
                <p>🔴 <b style="color:#FF4444;">Marca ({med_info['marca_referencia']}): S/{med_info['precio_marca']:.2f} / {unidad}</b><br>
                <small style="color:#8696A0;">Caja 30 ≈ S/{caja30_marca:.2f}</small></p>
                <p style="color:#00D4FF;font-size:1.1em;font-weight:700;">Ahorrás hasta {ahorro_pct}% comprando genérico</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        resultados = buscar_precio_farmacia(med_sel, farmacias_filtradas)
        if resultados:
            barato = resultados[0]
            caro   = resultados[-1]
            centro = [-12.0931, -77.0353]

            m_map = folium.Map(location=centro, zoom_start=13, tiles="CartoDB dark_matter")
            # CircleMarker evita el error de marker-icon.png en streamlit-folium
            folium.CircleMarker(
                centro, radius=10, color="#4FC3F7", fill=True, fill_color="#4FC3F7",
                popup="📍 Tu ubicación (demo)", tooltip="📍 Tu ubicación (demo)"
            ).add_to(m_map)

            color_map = {"green": "#00FF88", "red": "#FF4444", "orange": "#FFAA00"}
            for f in resultados:
                if f["precio"] <= barato["precio"] * 1.03:
                    fcolor, label = "green", "💚 Más barato"
                elif f["precio"] >= caro["precio"] * 0.97:
                    fcolor, label = "red", "🔴 Más caro"
                else:
                    fcolor, label = "orange", "🟡 Precio medio"
                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={f['lat']},{f['lng']}"
                popup_html = (
                    f"<b>{f['nombre']}</b><br>"
                    f"{label} — <b>S/ {f['precio']:.2f}</b><br>"
                    f"{f.get('direccion','')}<br>"
                    f"{f['horario']}<br><br>"
                    f"<a href='{maps_url}' target='_blank' style='color:#00D4FF;'>📍 Cómo llegar (Google Maps)</a>"
                )
                folium.CircleMarker(
                    [f["lat"], f["lng"]],
                    radius=9,
                    color=color_map[fcolor], fill=True, fill_color=color_map[fcolor], fill_opacity=0.85,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{f['nombre']} — S/{f['precio']:.2f}"
                ).add_to(m_map)

            st_folium(m_map, width=700, height=400, returned_objects=[])
            st.caption("💚 Verde = más barato · 🔴 Rojo = más caro · Clic en marcador → dirección + Google Maps")

            unidad_tabla = med_info.get("presentacion", "unidad").lower() if med_info else "unidad"
            df = pd.DataFrame(resultados)[["nombre", "cadena", "distrito", "direccion", "precio"]]
            df.columns = ["Farmacia", "Cadena", "Distrito", "Dirección", f"Precio/  {unidad_tabla}"]
            df[f"Precio/  {unidad_tabla}"] = df[f"Precio/  {unidad_tabla}"].apply(lambda x: f"S/ {x:.2f}")
            df["Maps"] = [f"https://www.google.com/maps/dir/?api=1&destination={r['lat']},{r['lng']}" for r in resultados]
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Maps": st.column_config.LinkColumn("📍 Google Maps", display_text="Cómo llegar")
                }
            )

    # ── Buscador DIGEMID ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔍 Buscador DIGEMID — Catálogo oficial de medicamentos Perú")
    st.caption(f"Base de datos DIGEMID actualizada 19/06/2026 · {len(digemid_db):,} productos registrados")

    query = st.text_input("Buscá por nombre o principio activo (IFA)", placeholder="ej: metformina, ibuprofeno, losartan...")
    if query and len(query) >= 3:
        q = query.upper().strip()
        results = [p for p in digemid_db if q in p["nombre"] or q in p["ifa"]][:50]
        if results:
            df_dig = pd.DataFrame(results)[["nombre", "concent", "ifa", "rubro"]]
            df_dig.columns = ["Producto", "Concentración", "Principio Activo (IFA)", "Rubro"]
            st.dataframe(df_dig, use_container_width=True, hide_index=True)
            st.caption(f"Mostrando {len(results)} de {sum(1 for p in digemid_db if q in p['nombre'] or q in p['ifa'])} coincidencias")
        else:
            st.info(f"No encontramos '{query}' en el catálogo DIGEMID.")

# ═══════════════════════════════════════════════════════
# TAB 3: RIESGO FINDRISC
# ═══════════════════════════════════════════════════════
with t3:
    st.markdown("### 📊 Test de Riesgo de Diabetes Tipo 2")
    st.caption("Cuestionario FINDRISC validado por la OMS. Sin análisis de sangre.")

    with st.expander("Sobre FINDRISC — ¿qué es y en qué se basa?"):
        st.markdown("""
**FINDRISC** (Finnish Diabetes Risk Score) es un cuestionario de 8 preguntas desarrollado por la
**Asociación Finlandesa de Diabetes** y validado por la OMS para detectar riesgo de diabetes tipo 2
sin necesidad de análisis de sangre.

| Puntaje | Riesgo | Probabilidad a 10 años |
|---|---|---|
| < 7 | Bajo | ~1% |
| 7–11 | Ligeramente elevado | ~4% |
| 12–14 | Moderado | ~17% |
| 15–20 | Alto | ~33% |
| > 20 | Muy alto | ~50% |

**Fuente:** Lindström J, Tuomilehto J. *The diabetes risk score: a practical tool to predict type 2 diabetes risk.*
Diabetes Care. 2003;26(3):725–731. [doi:10.2337/diacare.26.3.725](https://doi.org/10.2337/diacare.26.3.725)

Adoptado por la OMS y usado en más de 40 países. Sensibilidad: 78%, especificidad: 77% para detectar
diabetes no diagnosticada en población general.
        """)

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
