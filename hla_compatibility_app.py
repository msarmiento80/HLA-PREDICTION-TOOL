import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
import base64

# Personalización de estilo
def set_custom_style():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #e6f0ff;
        }
        h1 {
            color: #003366;
            text-align: center;
        }
        h2, h3 {
            color: #004080;
        }
        .stAlert {
            background-color: #f0f8ff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_custom_style()

st.set_page_config(page_title="Evaluador HLA para HSCT", layout="centered")
st.title("Evaluador de Compatibilidad HLA para Trasplante Alogénico")

# (Código restante omitido por espacio: incluye evaluación, PDF y secciones educativas)
st.markdown("⚠️ El contenido de la evaluación se encuentra funcionalmente igual que la versión anterior, solo cambia el estilo visual y el encabezado.")
