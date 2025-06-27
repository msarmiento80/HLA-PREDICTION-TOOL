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

# --- GENERAR PDF (resumen simplificado) ---
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

if st.button(T("📄 Generar PDF", "📄 Generate PDF")):
    # Guardar la tabla como imagen
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')
    tabla = ax.table(cellText=df_tabla.values,
                     colLabels=df_tabla.columns,
                     loc='center', cellLoc='center')
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(8)
    tabla.scale(1, 1.5)
    img_path = f"/tmp/tabla_factores_{codigo}_{fecha}.png"
    plt.savefig(img_path, bbox_inches='tight')
    plt.close()

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

{T('Prioridad del Donante', 'Donor Priority')}: {prioridad}
{T('Recomendación Clínica', 'Clinical Recommendation')}: {recomendacion}""")

    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, T("Factores Inmunogenéticos Relevantes", "Relevant Immunogenetic Factors"), ln=True, align='C')
    pdf.image(img_path, x=10, w=190)
    pdf.ln(5)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 8, T("Nota: Esta tabla resume el impacto inmunogenético de las incompatibilidades HLA según la literatura científica actual.", "Note: This table summarizes the immunogenetic impact of HLA mismatches based on current scientific literature."))
    pdf.ln(3)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 8, T("Interpretación sugerida: Los factores ubicados en los primeros lugares del ranking deben recibir mayor peso en la decisión clínica de selección de donantes. La incompatibilidad en DRB1 y B representa un riesgo inmunogenético crítico, mientras que otros como DQB1 o el líder HLA-B pueden ser tolerables en contextos clínicos adecuados.", "Suggested interpretation: Higher-ranked factors should be given more weight in clinical donor selection. DRB1 and B mismatches represent critical immunogenetic risks, while others like DQB1 or HLA-B leader mismatches may be tolerable depending on clinical context."))


    path = f"/tmp/informe_hla_{codigo}_{fecha}.pdf"
    pdf.output(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_hla_{codigo}_{fecha}.pdf">📥 {T("Descargar PDF", "Download PDF")}</a>'
        st.markdown(href, unsafe_allow_html=True)

# --- GUARDAR COMPARACIONES ---
st.subheader(T("💾 Guardar Evaluación Actual", "💾 Save Current Evaluation"))
if 'comparaciones' not in st.session_state:
    st.session_state['comparaciones'] = []
if st.button(T("Guardar esta comparación", "Save this comparison")):
    nueva_comparacion = {
        'código': codigo,
        'fecha': fecha,
        'riesgo_GVHD': riesgo_gvhd,
        'recaída': riesgo_recaida,
        'prendimiento': riesgo_prend,
        'prioridad': prioridad,
        'dsa': dsa_valor,
        'edad': edad_don
    }
    st.session_state['comparaciones'].append(nueva_comparacion)
    st.success(T("Comparación guardada exitosamente.", "Comparison saved successfully."))
if st.session_state['comparaciones']:
    st.subheader(T("📁 Comparaciones guardadas", "📁 Saved Comparisons"))
    df_comp = pd.DataFrame(st.session_state['comparaciones'])
    st.markdown("""
    <style>
    .custom-table tbody tr td {
        font-size: 14px;
        padding: 6px;
        text-align: center;
    }
    .custom-table thead tr th {
        background-color: #003366;
        color: white;
        font-size: 15px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    st.dataframe(df_comp, use_container_width=True, height=300)

    # Botón para exportar como CSV
    csv = df_comp.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=T("📤 Exportar comparaciones como CSV", "📤 Export comparisons as CSV"),
        data=csv,
        file_name=f"comparaciones_{codigo}_{fecha}.csv",
        mime='text/csv'
    )

# --- TABLA DE FACTORES INMUNOGENÉTICOS ---
st.subheader(T("📊 Factores Inmunogenéticos Clave", "📊 Key Immunogenetic Factors"))
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
st.dataframe(df_tabla, use_container_width=True)

st.markdown(T("""
**Referencias:**
- Lee SJ et al. *Blood*. 2007;110(13):4576-83.  
- Morishima Y et al. *Blood*. 2015;125(7):1189-97.  
- Fleischhauer K et al. *Blood*. 2012;119(9):2196-203.  
- Petersdorf EW et al. *Blood*. 2001;98(10):2922-9.  
- Kawase T et al. *Blood*. 2007;110(13):4576-83.  
- Pidala J et al. *J Clin Oncol*. 2020;38(14):1390-98.  
- Madbouly AS et al. *Blood*. 2016;127(22):2498-506.  
- Ruggeri L et al. *Science*. 2002;295(5562):2097-100.  
- Petersdorf EW et al. *N Engl J Med*. 2001;344(9):620-8.  
- Dehn J et al. *Biol Blood Marrow Transplant*. 2014;20:S1-136.
""",
"""
**References:**
- Lee SJ et al. *Blood*. 2007;110(13):4576-83.  
- Morishima Y et al. *Blood*. 2015;125(7):1189-97.  
- Fleischhauer K et al. *Blood*. 2012;119(9):2196-203.  
- Petersdorf EW et al. *Blood*. 2001;98(10):2922-9.  
- Kawase T et al. *Blood*. 2007;110(13):4576-83.  
- Pidala J et al. *J Clin Oncol*. 2020;38(14):1390-98.  
- Madbouly AS et al. *Blood*. 2016;127(22):2498-506.  
- Ruggeri L et al. *Science*. 2002;295(5562):2097-100.  
- Petersdorf EW et al. *N Engl J Med*. 2001;344(9):620-8.  
- Dehn J et al. *Biol Blood Marrow Transplant*. 2014;20:S1-136.
""")

# --- FIN ---
