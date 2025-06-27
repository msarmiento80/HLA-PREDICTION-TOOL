import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import datetime
import os
import random
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

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
        color: #111111;
    }
    h1 {
        color: #003366;
        text-align: center;
        font-size: 28px;
    }
    h4 {
        text-align: center;
        color: #003366;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
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

# --- TABLA DE FACTORES ---
data = {
    "Ranking": ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"],
    "Factor": [
        "HLA-DRB1 mismatch",
        "HLA-A or HLA-B mismatch",
        "Non-permissive HLA-DPB1",
        "HLA-C mismatch",
        "HLA-DQB1 mismatch",
        "HLA-B leader (M/T)",
        "HLA-DQA1 mismatch",
        "KIR ligand mismatch",
        "Allelic vs Antigen mismatch",
        "Mismatch directionality"
    ],
    "Impact": [
        "↑ Acute GVHD, ↓ OS, ↑ TRM",
        "↑ GVHD, graft failure, ↓ survival",
        "↑ GVHD, ↑ TRM",
        "↑ chronic GVHD, moderate TRM",
        "Limited effect alone; augments DRB1",
        "↑ relapse if mismatch (M donor)",
        "Emerging evidence; CD4 repertoire",
        "↓ relapse, NK alloreactivity (AML)",
        "Allele mismatch worse than antigen",
        "GVHD (GVH), graft loss (HVG)"
    ]
}
df_tabla = pd.DataFrame(data)

st.subheader(T("📊 Factores Inmunogenéticos Clave", "📊 Key Immunogenetic Factors"))
st.dataframe(df_tabla, use_container_width=True)

# --- GUARDAR IMAGEN DE LA TABLA ---
fig, ax = plt.subplots(figsize=(8, 4))
ax.axis('off')
tabla = ax.table(cellText=df_tabla.values, colLabels=df_tabla.columns, loc='center', cellLoc='center')
tabla.auto_set_font_size(False)
tabla.set_fontsize(8)
tabla.scale(1, 1.5)
img_path = f"/tmp/tabla_factores_{codigo}_{fecha}.png"
plt.savefig(img_path, bbox_inches='tight')
plt.close()

# --- GENERAR PDF (INCLUYENDO LA TABLA COMO IMAGEN Y REFERENCIAS) ---
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

{T('La tabla de factores inmunogenéticos clave se adjunta a continuación.', 'Key immunogenetic factors table is attached below.')}
""")
    pdf.image(img_path, x=10, w=190)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, T("Referencias (formato APA)", "References (APA format)"), ln=True)
    pdf.set_font("Arial", '', 10)
    referencias = [
        "Lee SJ, et al. (2007). Blood, 110(13), 4576–4583.",
        "Morishima Y, et al. (2015). Blood, 125(7), 1189–1197.",
        "Fleischhauer K, et al. (2012). Blood, 119(9), 2196–2203.",
        "Petersdorf EW, et al. (2001). Blood, 98(10), 2922–2929.",
        "Kawase T, et al. (2007). Blood, 110(13), 4576–4583.",
        "Pidala J, et al. (2020). J Clin Oncol, 38(14), 1390–1398.",
        "Madbouly AS, et al. (2016). Blood, 127(22), 2498–2506.",
        "Ruggeri L, et al. (2002). Science, 295(5562), 2097–2100.",
        "Petersdorf EW, et al. (2001). N Engl J Med, 344(9), 620–628.",
        "Dehn J, et al. (2014). Biol Blood Marrow Transplant, 20, S1–S136."
    ]
    for ref in referencias:
        pdf.multi_cell(0, 8, f"- {ref}")

    path = f"/tmp/informe_hla_{codigo}_{fecha}.pdf"
    pdf.output(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_hla_{codigo}_{fecha}.pdf">📥 {T("Descargar PDF", "Download PDF")}</a>'
        st.markdown(href, unsafe_allow_html=True)
