
# 🧬 HLA Compatibility Evaluator

**Evaluador clínico para compatibilidad HLA y priorización de donantes en trasplante alogénico de células madre hematopoyéticas.**

Desarrollado por el Programa de Trasplante Hematopoyético del Adulto, Pontificia Universidad Católica de Chile.

![App Screenshot](README_screenshot.png)

---

## 🔍 Características principales

- Evaluación inmunogenética personalizada
- Compatibilidad HLA detallada (A, B, C, DRB1, DQB1, DPB1)
- Análisis de polimorfismo líder HLA-B (T/T, M/T, M/M)
- Variables clínicas del donante: sexo, edad, hijos, grupo ABO
- Cálculo automático de riesgo y prioridad (1–3)
- Generación de informe PDF bilingüe
- Registro automático en CSV local
- Accesible en versión móvil y de escritorio

---

## ▶️ ¿Cómo usar esta app?

### Opción 1: Online

Accede directamente desde Streamlit Cloud:  
🔗 [Abrir la app](https://hla-prediction-tool-fwcc25cmzg6j3eewphmkac.streamlit.app/)

### Opción 2: Local

1. Clona este repositorio:

```bash
git clone https://github.com/tuusuario/hla-prediction-tool.git
cd hla-prediction-tool
```

2. Instala dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta la app:

```bash
streamlit run hla_compatibility_app.py
```

---

## 🏥 Créditos

**Desarrollado por:**  
Dr. Augusto Ochoa Ughini  
Programa de Trasplante Hematopoyético del Adulto  
Pontificia Universidad Católica de Chile

---

## 📄 Licencia

Este proyecto es de uso clínico-institucional con fines educativos y de apoyo a decisiones. Uso académico permitido.
