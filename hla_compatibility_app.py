import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import datetime
import os
import random

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="HLA Evaluator",
    page_icon="favicon.png",
    layout="centered"
)

# --- ESTILO PERSONALIZADO ---
st.markdown(
    """
    <style>
    .stApp { background-color: #f0f8ff; }
    h1 { color: #003366; text-align: center; font-size: 28px; }
    h4 { text-align: center; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SELECTOR DE IDIOMA ---
idioma = st.selectbox("🌐 Idioma / Language", ["Español", "English"])
T = lambda es, en: es if idioma == "Español" else en

# --- TÍTULOS PRINCIPALES ---
st.title(T("Evaluador de Compatibilidad HLA", "HLA Compatibility Evaluator"))
st.markdown(f"<h4>{T('Programa de Trasplante Hematopoyético del Adulto - Pontificia Universidad Católica de Chile', 'Adult Hematopoietic Transplant Program - Pontifical Catholic University of Chile')}</h4>", unsafe_allow_html=True)

# --- CÓDIGO DE PACIENTE ---
codigo = st.text_input(T("Código del paciente", "Patient code"))
if not codigo:
    st.warning(T("Debe ingresar un código para continuar.", "Please enter a code to continue."))
    st.stop()

# --- FECHA E ID DE INFORME ---
fecha = datetime.date.today().strftime("%Y-%m-%d")
id_informe = f"TPH-{datetime.date.today().strftime('%Y%m%d')}-{random.randint(1000,9999)}"

# --- DATOS DE COMPATIBILIDAD HLA ---
st.header(T("Incompatibilidad HLA", "HLA Mismatching"))
dis_a = st.checkbox("HLA-A")
dis_b = st.checkbox("HLA-B")
dis_c = st.checkbox("HLA-C")
dis_drb1 = st.checkbox("HLA-DRB1")
dis_dqb1 = st.checkbox("HLA-DQB1")
dpb1_no_perm = st.checkbox("HLA-DPB1 no permisivo")
lider_tt = st.checkbox("Polimorfismo líder HLA-B T/T")

# --- DATOS DEL DONANTE ---
st.header(T("Datos del Donante", "Donor Information"))
edad_don = st.number_input(T("Edad del donante", "Donor age"), 0, 75, 30)
grupo_don = st.selectbox("Grupo sanguíneo donante", ["A", "B", "AB", "O"])
sexo_don = st.selectbox(T("Sexo del donante", "Donor sex"), ["Masculino", "Femenino"])
grupo_rec = st.selectbox("Grupo sanguíneo receptor", ["A", "B", "AB", "O"])
hijos_don = st.checkbox(T("Donante con hijos", "Donor has children"))

# --- NIVELES DE ANTI-HLA (DSA) ---
dsa_valor = st.number_input(T("Nivel de anticuerpos anti-HLA (DSA, MFI)", "Anti-HLA antibodies level (DSA, MFI)"), min_value=0, value=0)

# --- RIESGO DE GVHD, RECAÍDA, PRENDIMIENTO ---
st.subheader(T("Evaluación de Riesgos Adicionales", "Additional Risk Evaluation"))
riesgo = "Bajo"
if dis_drb1 or dis_b or dpb1_no_perm or lider_tt or sum([dis_a, dis_b, dis_c, dis_drb1, dis_dqb1]) >= 2:
    riesgo = "Alto"
elif sum([dis_a, dis_b, dis_c, dis_drb1, dis_dqb1]) == 1:
    riesgo = "Intermedio"
riesgo_gvhd = riesgo
riesgo_recaida = "Bajo" if riesgo == "Bajo" else ("Intermedio" if edad_don < 40 else "Alto")
riesgo_prend = "Bajo"  # Riesgo de fallo de prendimiento (graft failure)
if dsa_valor > 5000:
    riesgo_prend = "Alto"
elif grupo_don != grupo_rec:
    riesgo_prend = "Intermedio"
elif grupo_don != grupo_rec and edad_don > 45:
    riesgo_prend = "Alto"
if grupo_don != grupo_rec:
    riesgo_prend = "Intermedio"
if grupo_don != grupo_rec and edad_don > 45:
    riesgo_prend = "Alto"
riesgo_dsa = "Negativo"
if dsa_valor > 2000:
    riesgo_dsa = "Positivo (>2000 MFI)"

st.markdown(f"""
**{T('Riesgo de GVHD', 'GVHD Risk')}:** {riesgo_gvhd}  
**{T('Riesgo de recaída', 'Relapse Risk')}:** {riesgo_recaida}  
**{T('Riesgo de fallo de prendimiento', 'Graft failure risk')}:** {riesgo_prend}  
**{T('Anticuerpos anti-HLA (DSA)', 'Anti-HLA antibodies (DSA)')}:** {riesgo_dsa}
""")

# --- PRIORIZACIÓN DEL DONANTE ---
prioridad = ""
icono = ""
color = ""
if dsa_valor > 5000:
    prioridad = T("Prioridad 3: Donante subóptimo", "Priority 3: Suboptimal donor")
    icono = "❌"
    color = "#f8d7da"
elif riesgo == "Bajo" and edad_don <= 35 and not lider_tt and grupo_don == grupo_rec and sexo_don == "Masculino":
    prioridad = T("Prioridad 1: Donante ideal", "Priority 1: Optimal donor")
    icono = "✅"
    color = "#d0f0c0"
elif riesgo == "Intermedio" or edad_don <= 50:
    prioridad = T("Prioridad 2: Donante aceptable", "Priority 2: Acceptable donor")
    icono = "🟡"
    color = "#fff3cd"
else:
    prioridad = T("Prioridad 3: Donante subóptimo", "Priority 3: Suboptimal donor")
    icono = "❌"
    color = "#f8d7da"

st.subheader(T(" Prioridad del Donante", " Donor Priority"))
st.markdown(f"""
<div style='padding: 1rem; background-color:{color}; border-radius: 10px;'>
<b>{icono} {prioridad}</b>
</div>
""", unsafe_allow_html=True)

# --- ALERTA POR DSA ELEVADO ---
if dsa_valor > 5000:
    st.error(T("⚠️ Atención: Anticuerpos anti-HLA muy elevados (>5000 MFI). Evaluar desensibilización pre-trasplante.",
                 "⚠️ Warning: Highly elevated anti-HLA antibodies (>5000 MFI). Consider pre-transplant desensitization."))

# --- RECOMENDACIÓN CLÍNICA ---
recomendacion = ""
if riesgo_prend == "Alto" and dsa_valor > 5000:
    recomendacion = T("Se recomienda evitar este donante debido al alto riesgo de fallo de prendimiento asociado a anticuerpos anti-HLA elevados (>5000 MFI). Si se considera imprescindible, debe evaluarse desensibilización pre-trasplante.", "Avoid this donor due to high graft failure risk associated with elevated anti-HLA antibodies (>5000 MFI). If this donor must be used, consider pre-transplant desensitization strategies.")
elif riesgo == "Alto":
    recomendacion = T("Buscar alternativas si es posible; alto riesgo por incompatibilidades HLA.", "Seek alternatives if possible; high risk due to HLA incompatibilities.")
elif riesgo == "Intermedio":
    recomendacion = T("Evaluar en comité; riesgo intermedio.", "Evaluate in committee; intermediate risk.")
else:
    recomendacion = T("Proceder si no existen otras contraindicaciones.", "Proceed if no other contraindications exist.")

st.subheader(T("🩺 Recomendación Clínica", "🩺 Clinical Recommendation"))
st.info(recomendacion)

# --- AGREGAR A PDF ---
if 'pdf_info' not in st.session_state:
    st.session_state['pdf_info'] = {}
st.session_state['pdf_info'].update({
    "riesgo_gvhd": riesgo_gvhd,
    "riesgo_recaida": riesgo_recaida,
    "riesgo_prend": riesgo_prend,
    "riesgo_dsa": riesgo_dsa
})

# --- GENERAR PDF CON RIESGOS COMPLETOS ---
if st.button(T("📄 Generar PDF", "📄 Generate PDF")):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, T("Informe de Evaluación HLA", "HLA Evaluation Report"), ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"""{T('Código del paciente', 'Patient code')}: {codigo}
{T('Fecha', 'Date')}: {fecha}
{T('ID del informe', 'Report ID')}: {id_informe}

{T('Riesgo de GVHD', 'GVHD Risk')}: {riesgo_gvhd}
{T('Riesgo de recaída', 'Relapse Risk')}: {riesgo_recaida}
{T('Riesgo de fallo de prendimiento', 'Graft failure risk')}: {riesgo_prend}
{T('Anticuerpos anti-HLA (DSA)', 'Anti-HLA antibodies (DSA)')}: {riesgo_dsa}

{T('Prioridad del Donante', 'Donor Priority')}: " +
                     "{prioridad}
{T('Recomendación Clínica', 'Clinical Recommendation')}: {recomendacion}
""")
    path = "/tmp/informe_hla.pdf"
    pdf.output(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_hla.pdf">📥 {T("Descargar PDF", "Download PDF")}</a>'
        st.markdown(href, unsafe_allow_html=True)
