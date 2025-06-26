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
st.header(T("Incompatibilidad HLA", "HLA matching"))
dis_a = st.checkbox("HLA-A")
dis_b = st.checkbox("HLA-B")
dis_c = st.checkbox("HLA-C")
dis_drb1 = st.checkbox("HLA-DRB1")
dis_dqb1 = st.checkbox("HLA-DQB1")
dpb1_no_perm = st.checkbox("HLA-DPB1 no permisivo")
lider_tt = st.checkbox("Polimorfismo líder HLA-B T/T")

# --- DATOS DEL DONANTE ---
st.header(T("Datos del Donante", "Donor Information"))
edad_don = st.number_input(T("Edad del donante", "Donor age"), 8, 80, 30)
grupo_don = st.selectbox("Grupo sanguíneo donante", ["A", "B", "AB", "O"])
sexo_don = st.selectbox(T("Sexo del donante", "Donor sex"), ["Masculino", "Femenino"])
grupo_rec = st.selectbox("Grupo sanguíneo receptor", ["A", "B", "AB", "O"])
hijos_don = st.checkbox(T("Donante con hijos", "Donor has children"))

# --- EVALUACIÓN DE RIESGO ---
st.subheader(T("Resultado Inmunogenético", "Immunogenetic Result"))
n_dis = sum([dis_a, dis_b, dis_c, dis_drb1, dis_dqb1])
riesgo = "Bajo"
if dis_drb1 or dis_b or dpb1_no_perm or lider_tt or n_dis >= 2:
    riesgo = "Alto"
elif n_dis == 1:
    riesgo = "Intermedio"

color = {"Bajo": "🟢", "Intermedio": "🟠", "Alto": "🔴"}[riesgo]
st.info(f"{color} {T('Riesgo', 'Risk')}: **{riesgo}**")

# --- PRIORIDAD DEL DONANTE ---
st.subheader(T("Prioridad del Donante", "Donor Priority"))
prioridad = 1
if sexo_don == "Femenino" or edad_don > 45 or hijos_don or riesgo == "Alto":
    prioridad = 2
if n_dis >= 2 or lider_tt or dpb1_no_perm or (sexo_don == "Femenino" and hijos_don):
    prioridad = 3

msg = {
    1: T("Donante ideal. Varón joven sin disonancias críticas.", "Ideal donor. Young male, no critical mismatches."),
    2: T("Donante aceptable. Presenta factores moderados de riesgo.", "Acceptable donor. Some moderate-risk factors."),
    3: T("Donante de baja prioridad. Buscar alternativas si es posible.", "Low priority donor. Consider alternatives.")
}[prioridad]

st.success(f"🧬 {T('Prioridad', 'Priority')} {prioridad} — {msg}")

# --- GUARDAR REGISTRO LOCAL ---
if not os.path.exists("registros.csv"):
    with open("registros.csv", "w") as f:
        f.write("codigo,fecha,id_informe,riesgo,prioridad\n")
with open("registros.csv", "a") as f:
    f.write(f"{codigo},{fecha},{id_informe},{riesgo},{prioridad}\n")

# --- GENERAR PDF ---
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

{T('Riesgo inmunogenético', 'Immunogenetic Risk')}: {riesgo}
{T('Prioridad del donante', 'Donor Priority')}: {prioridad}
{T('Comentario', 'Comment')}: {msg}
""")
    path = "/tmp/reporte.pdf"
    pdf.output(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_hla.pdf">📥 {T("Descargar PDF", "Download PDF")}</a>'
        st.markdown(href, unsafe_allow_html=True)
