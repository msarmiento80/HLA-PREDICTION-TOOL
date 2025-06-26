import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Evaluador HLA para HSCT", layout="centered")
st.title("\U0001F9EC Evaluador de Compatibilidad HLA para Trasplante Alogénico")

st.header("1. Ingreso de Datos del Donante")

# Opción de carga desde archivo
st.subheader("\U0001F4C2 Cargar tipificación desde archivo (opcional)")
archivo = st.file_uploader("Subir archivo CSV con columnas: Locus, Estado (Igual/Diferente)", type="csv")

loci_discrepantes = []
num_discrepancias = 0

if archivo is not None:
    df = pd.read_csv(archivo)
    loci_discrepantes = df[df['Estado'].str.lower() == 'diferente']['Locus'].tolist()
    num_discrepancias = len(loci_discrepantes)
    st.success(f"Se detectaron {num_discrepancias} disonancias: {', '.join(loci_discrepantes)}")
else:
    # Compatibilidad básica manual
    col1, col2 = st.columns(2)

    with col1:
        num_discrepancias = st.selectbox("Número total de disonancias", [0, 1, 2, 3, 4, 5])
        loci_discrepantes = st.multiselect("¿Qué loci presentan disonancia?", ["HLA-A", "HLA-B", "HLA-C", "HLA-DRB1", "HLA-DQB1"])

with col2:
    dpb1_estado = st.radio("Estado de HLA-DPB1", ["Permisivo", "No permisivo", "No evaluado"])
    lider_hlab = st.radio("Polimorfismo del líder HLA-B", ["M/M", "M/T", "T/T", "Desconocido"])

# Factores adicionales
st.subheader("\U0001FA7A Factores clínicos adicionales")
enfermedad = st.selectbox("Tipo de enfermedad", ["Leucemia aguda", "Mielodisplasia", "Linfoma", "Otra"])
fuente_injerto = st.selectbox("Fuente del injerto", ["Médula ósea", "Sangre periférica", "Cordón umbilical"])

st.divider()

# Evaluación lógica
st.header("2. Evaluación Clínica")

riesgo = ""
recomendacion = ""
color = "gray"

if num_discrepancias == 0:
    riesgo = "Bajo"
    recomendacion = "Compatibilidad 10/10. Trasplante altamente recomendado."
    color = "green"
elif num_discrepancias == 1:
    riesgo = "Intermedio"
    if "HLA-DRB1" in loci_discrepantes or "HLA-B" in loci_discrepantes:
        recomendacion = "Evitar si es posible: disonancia inmunológicamente significativa."
        color = "orange"
    else:
        recomendacion = "Aceptable si no hay donante mejor."
        color = "yellow"
else:
    riesgo = "Alto"
    recomendacion = "Uso solo en ausencia de mejores opciones. Riesgo elevado de EICH y mortalidad."
    color = "red"

if dpb1_estado == "No permisivo":
    recomendacion += " Además, HLA-DPB1 no permisivo agrava el riesgo."
    if riesgo == "Bajo":
        riesgo = "Intermedio"
        color = "orange"
    elif riesgo == "Intermedio":
        riesgo = "Alto"
        color = "red"

if lider_hlab == "T/T":
    recomendacion += " El polimorfismo T/T en líder HLA-B está asociado a mayor riesgo de EICH."
    if riesgo == "Bajo":
        riesgo = "Intermedio"
        color = "orange"
    elif riesgo == "Intermedio":
        riesgo = "Alto"
        color = "red"

# Ajustes por enfermedad y fuente
if enfermedad == "Leucemia aguda" and riesgo == "Intermedio":
    recomendacion += " En leucemia aguda, se debe priorizar compatibilidad completa si es posible."

if fuente_injerto == "Sangre periférica" and riesgo == "Alto":
    recomendacion += " Sangre periférica podría aumentar el riesgo de EICH aún más."

# Resultado
st.subheader("Resultado de la Evaluación")
st.markdown(f"**Riesgo Inmunogenético:** :{color}[{riesgo}]")
st.info(recomendacion)

# Gráfico de semáforo
st.subheader("Visualización de Riesgo")
fig, ax = plt.subplots(figsize=(1, 3))
colors = ["green", "yellow", "orange", "red"]
labels = ["Bajo", "Intermedio", "Moderado-Alto", "Alto"]
pos = labels.index("Alto" if riesgo == "Alto" else "Moderado-Alto" if riesgo == "Intermedio" else "Bajo")

for i, c in enumerate(colors):
    ax.bar(0, 1, bottom=i, color=c)

ax.plot([0], [pos + 0.5], marker="o", markersize=20, color="black")
ax.axis("off")
st.pyplot(fig)

# Sección educativa
st.header("3. Información Educativa")
with st.expander("¿Qué significa cada disonancia?"):
    st.markdown("""
    - **HLA-DRB1 o HLA-B**: Mayor riesgo de EICH y rechazo. Evitar.
    - **HLA-A o HLA-C**: Riesgo intermedio.
    - **HLA-DQB1**: Menor impacto clínico.
    - **HLA-DPB1**: Solo usar disonancias permisivas.
    - **Líder HLA-B T/T**: Asociado con mayor EICH y menor recuperación inmune.
    """)

with st.expander("Referencias clínicas"):
    st.markdown("""
    - Lee SJ et al., *Blood*, 2007.
    - Petersdorf EW et al., *Blood*, 2015.
    - Pidala J et al., *BBMT*, 2014.
    - Zhao X-Y et al., *J Hematol Oncol*, 2020.
    - Fuchs EJ, Luznik L. *ASH Educ Program*, 2021.
    """)

# Exportar resultado
st.header("4. Exportar Evaluación")
if st.button("Descargar informe PDF (próximamente)"):
    st.warning("Funcionalidad en desarrollo. En versiones futuras podrás generar un informe clínico en PDF.")
