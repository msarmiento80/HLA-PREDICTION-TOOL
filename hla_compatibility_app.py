import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
import base64

st.set_page_config(page_title="Evaluador HLA para HSCT", layout="centered")
st.title("🧬 Evaluador de Compatibilidad HLA para Trasplante Alogénico")

st.header("1. Compatibilidad HLA")

# Checkboxes para disonancias HLA
disonancia_a = st.checkbox("¿Disonancia en HLA-A?")
disonancia_b = st.checkbox("¿Disonancia en HLA-B?")
disonancia_c = st.checkbox("¿Disonancia en HLA-C?")
disonancia_drb1 = st.checkbox("¿Disonancia en HLA-DRB1?")
disonancia_dqb1 = st.checkbox("¿Disonancia en HLA-DQB1?")
dpb1_no_permisivo = st.checkbox("¿Disonancia en HLA-DPB1 no permisiva?")
lider_tt = st.checkbox("¿Polimorfismo líder HLA-B es T/T?")

# Factores clínicos adicionales
st.header("2. Datos Clínicos del Receptor y Donante")

col1, col2 = st.columns(2)
with col1:
    edad_receptor = st.number_input("Edad del receptor (años)", min_value=0, max_value=100, value=40)
    grupo_rec = st.selectbox("Grupo sanguíneo del receptor", ["A", "B", "AB", "O"])

with col2:
    grupo_don = st.selectbox("Grupo sanguíneo del donante", ["A", "B", "AB", "O"])
    donante_femenino = st.checkbox("¿Donante es mujer?")
    donante_con_hijos = st.checkbox("¿Donante tiene hijos?")

st.divider()

st.header("3. Evaluación de Riesgo")

disonancias = sum([
    disonancia_a, disonancia_b, disonancia_c, disonancia_drb1, disonancia_dqb1
])
riesgo = "Bajo"
color = "green"
recomendacion = "Trasplante con riesgo inmunogenético bajo."

# Evaluación por número de disonancias
if disonancias == 1:
    riesgo = "Intermedio"
    color = "orange"
    recomendacion = "Existe una disonancia. Evaluar cuidadosamente el locus involucrado."
elif disonancias >= 2:
    riesgo = "Alto"
    color = "red"
    recomendacion = "Múltiples disonancias HLA. Alto riesgo de EICH y mortalidad relacionada."

# Penalizaciones adicionales
if disonancia_drb1 or disonancia_b:
    riesgo = "Alto"
    color = "red"
    recomendacion += " DRB1 o B son loci críticos a evitar."

if dpb1_no_permisivo:
    riesgo = "Alto" if riesgo != "Alto" else riesgo
    color = "red"
    recomendacion += " HLA-DPB1 no permisivo agrava el riesgo."

if lider_tt:
    riesgo = "Alto" if riesgo != "Alto" else riesgo
    color = "red"
    recomendacion += " El polimorfismo T/T del líder HLA-B incrementa el riesgo de EICH."

if edad_receptor >= 50:
    recomendacion += " Edad avanzada del receptor es un factor de riesgo adicional."

if donante_femenino and donante_con_hijos:
    recomendacion += " Donante mujer con hijos: mayor riesgo de EICH por aloimunización previa."

if grupo_rec != grupo_don:
    recomendacion += " Incompatibilidad ABO entre donante y receptor requiere manejo específico."

# Resultado final
st.subheader("Resultado")
st.markdown(f"**Riesgo Inmunogenético:** :{color}[{riesgo}]")
st.info(recomendacion)

# Visualización
st.subheader("Visualización del Riesgo")
fig, ax = plt.subplots(figsize=(1, 3))
colors = ["green", "yellow", "orange", "red"]
labels = ["Bajo", "Intermedio", "Moderado-Alto", "Alto"]
pos = labels.index("Alto" if riesgo == "Alto" else "Moderado-Alto" if riesgo == "Intermedio" else "Bajo")

for i, c in enumerate(colors):
    ax.bar(0, 1, bottom=i, color=c)
ax.plot([0], [pos + 0.5], marker="o", markersize=20, color="black")
ax.axis("off")
st.pyplot(fig)

# Generación de PDF
st.subheader("4. Generar Informe PDF")

if st.button("📄 Generar y descargar PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Informe de Compatibilidad HLA para Trasplante Alogénico", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"""
Edad del receptor: {edad_receptor}
Grupo sanguíneo receptor: {grupo_rec}
Grupo sanguíneo donante: {grupo_don}
Donante mujer: {'Sí' if donante_femenino else 'No'}
Donante con hijos: {'Sí' if donante_con_hijos else 'No'}

Disonancias:
 - HLA-A: {'Sí' if disonancia_a else 'No'}
 - HLA-B: {'Sí' if disonancia_b else 'No'}
 - HLA-C: {'Sí' if disonancia_c else 'No'}
 - HLA-DRB1: {'Sí' if disonancia_drb1 else 'No'}
 - HLA-DQB1: {'Sí' if disonancia_dqb1 else 'No'}
 - HLA-DPB1 no permisivo: {'Sí' if dpb1_no_permisivo else 'No'}
 - Líder HLA-B T/T: {'Sí' if lider_tt else 'No'}

Riesgo Inmunogenético: {riesgo}
Recomendación Clínica: {recomendacion.strip()}
""")

    pdf_file_path = "/tmp/informe_hla.pdf"
    pdf.output(pdf_file_path)

    with open(pdf_file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_hla.pdf">📥 Descargar Informe PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

# Educación
st.header("5. Información Educativa")
with st.expander("¿Qué significan los factores considerados?"):
    st.markdown("""
    - **HLA-DRB1 / HLA-B**: Mayor impacto inmunogénico → evitar disonancias.
    - **DPB1 no permisivo**: Asociado a mayor EICH.
    - **Líder HLA-B T/T**: Incrementa el riesgo inmunológico.
    - **Edad > 50**: Mayor riesgo de mortalidad post-trasplante.
    - **Donante mujer con hijos**: Riesgo inmunológico elevado.
    - **Incompatibilidad ABO**: Posible hemólisis / rechazo injerto.
    """)

with st.expander("Referencias clínicas"):
    st.markdown("""
    - Lee SJ et al., *Blood*, 2007.
    - Petersdorf EW et al., *Blood*, 2015.
    - Zhao X-Y et al., *J Hematol Oncol*, 2020.
    - Fuchs EJ, Luznik L. *ASH Educ Program*, 2021.
    """)
