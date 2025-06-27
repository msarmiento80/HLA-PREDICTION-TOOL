import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import datetime
import os
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
    .stApp {
        background-color: #f0f8ff;
        color: #000000 !important;
    }
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: #000000 !important;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stAlert, .st-info, .stWarning, .st-error {
        color: #000000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SELECTOR DE IDIOMA ---
idioma = st.selectbox("\U0001F310 Idioma / Language", ["Español", "English"])
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

# --- EVALUACIÓN DE RIESGO ---
riesgo = "Bajo"
if dis_drb1 or dis_b or dpb1_no_perm or lider_tt or sum([dis_a, dis_b, dis_c, dis_drb1, dis_dqb1]) >= 2:
    riesgo = "Alto"
elif sum([dis_a, dis_b, dis_c, dis_drb1, dis_dqb1]) == 1:
    riesgo = "Intermedio"
riesgo_gvhd = riesgo
riesgo_recaida = "Bajo" if riesgo == "Bajo" else ("Intermedio" if edad_don < 40 else "Alto")
riesgo_prend = "Bajo"
if dsa_valor > 5000:
    riesgo_prend = "Alto"
elif grupo_don != grupo_rec:
    riesgo_prend = "Intermedio"
elif grupo_don != grupo_rec and edad_don > 45:
    riesgo_prend = "Alto"
riesgo_dsa = "Negativo"
if dsa_valor > 2000:
    riesgo_dsa = "Positivo (>2000 MFI)"

st.subheader(T("Evaluación de Riesgos Adicionales", "Additional Risk Evaluation"))
st.markdown(f"""
**{T('Riesgo de GVHD', 'GVHD Risk')}:** {riesgo_gvhd}  
**{T('Riesgo de recaída', 'Relapse Risk')}:** {riesgo_recaida}  
**{T('Riesgo de fallo de prendimiento', 'Graft failure risk')}:** {riesgo_prend}  
**{T('Anticuerpos anti-HLA (DSA)', 'Anti-HLA antibodies (DSA)')}:** {riesgo_dsa}
""")

# --- PRIORIZACIÓN DEL DONANTE ---
prioridad = ""
if dsa_valor > 5000:
    prioridad = T("Prioridad 3: Donante subóptimo", "Priority 3: Suboptimal donor")
elif riesgo == "Bajo" and edad_don <= 35 and not lider_tt and grupo_don == grupo_rec and sexo_don == "Masculino":
    prioridad = T("Prioridad 1: Donante ideal", "Priority 1: Optimal donor")
elif riesgo == "Intermedio" or edad_don <= 50:
    prioridad = T("Prioridad 2: Donante aceptable", "Priority 2: Acceptable donor")
else:
    prioridad = T("Prioridad 3: Donante subóptimo", "Priority 3: Suboptimal donor")

st.subheader(T("Prioridad del Donante", "Donor Priority"))
st.markdown(f"**{prioridad}**")

# --- RECOMENDACIÓN CLÍNICA ---
recomendacion = ""
if riesgo_prend == "Alto" and dsa_valor > 5000:
    recomendacion = T("Se recomienda evitar este donante debido al alto riesgo de fallo de prendimiento asociado a anticuerpos anti-HLA elevados (>5000 MFI). Si se considera imprescindible, debe evaluarse desensibilización pre-trasplante.",
                      "Avoid this donor due to high graft failure risk associated with elevated anti-HLA antibodies (>5000 MFI). If this donor must be used, consider pre-transplant desensitization strategies.")
elif riesgo == "Alto":
    recomendacion = T("Buscar alternativas si es posible; alto riesgo por incompatibilidades HLA.", "Seek alternatives if possible; high risk due to HLA incompatibilities.")
elif riesgo == "Intermedio":
    recomendacion = T("Evaluar en comité; riesgo intermedio.", "Evaluate in committee; intermediate risk.")
else:
    recomendacion = T("Proceder si no existen otras contraindicaciones.", "Proceed if no other contraindications exist.")

st.subheader(T("Recomendación Clínica", "Clinical Recommendation"))
st.info(recomendacion)

# --- TABLA DE FACTORES INMUNOGENÉTICOS ---
st.subheader(T("\U0001F4CA Factores Inmunogenéticos Clave", "\U0001F4CA Key Immunogenetic Factors"))
data = {
    "Ranking": [
        "1️⃣",
        "2️⃣",
        "3️⃣",
        "4️⃣",
        "5️⃣",
        "6️⃣",
        "7️⃣",
        "8️⃣",
        "9️⃣",
        "🔟"
    ],
    "Impacto clínico": [
        "↑ Acute GVHD, ↓ OS, ↑ TRM",
        "↑ GVHD, graft failure, ↓ survival",
        "↑ GVHD, ↑ TRM",
        "↑ chronic GVHD, moderate TRM",
        "Limited effect alone; augments DRB1",
        "↑ relapse if mismatch (T/T donor)",
        "Emerging evidence; CD4 repertoire",
        "↓ relapse, NK alloreactivity (AML)",
        "Allele mismatch worse than antigen",
        "GVHD (GVH), graft loss (HVG)"
    ],
    "N° Pacientes": ["12000", "18000", "5000", "4000", "6000", "7000", "3000", "3500", "10000", "4000"],
    "Fuerza Evidencia": ["Muy Alta", "Muy Alta", "Alta", "Alta", "Media", "Media", "Baja", "Media", "Alta", "Media"],
    "Referencia": [
        "Lee SJ et al. (2007)",
        "Morishima Y et al. (2015)",
        "Fleischhauer K et al. (2012)",
        "Petersdorf EW et al. (2001)",
        "Kawase T et al. (2007)",
        "Pidala J et al. (2020)",
        "Madbouly AS et al. (2016)",
        "Ruggeri L et al. (2002)",
        "Petersdorf EW et al. (2001)",
        "Dehn J et al. (2014)"
    ]
}
df_tabla = pd.DataFrame(data)
st.dataframe(df_tabla.set_index("Ranking"), use_container_width=True)
