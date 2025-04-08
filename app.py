import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import traceback

# Importar la función para cargar datos
from google_connection import load_data

# Importar las funciones de análisis
from analisis_dior import mostrar_analisis
from correlacion import mostrar_analisis_correlacion
from clusters import mostrar_analisis_clusters

# Importar configuración
from config import APP_TITLE, APP_ICON, APP_LAYOUT

# Configurar la página de Streamlit
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT
)

# Título principal
st.title(APP_TITLE)

try:
    # Cargar los datos
    df = load_data()
    
    if df is None or df.empty:
        st.error("No se pudieron cargar datos. Verifique la conexión con Google Sheets.")
    else:
        st.success(f"Datos cargados correctamente. {len(df)} registros encontrados.")
        
        # Opciones de análisis
        tipo_analisis = st.sidebar.radio(
            "Seleccione tipo de análisis:",
            ["Vista previa básica", "Mapa de Correlaciones", "Análisis de Clusters"]
        )
        
        # Mostrar el análisis seleccionado
        if tipo_analisis == "Vista previa básica":
            mostrar_analisis(df)
        elif tipo_analisis == "Mapa de Correlaciones":
            mostrar_analisis_correlacion(df)
        elif tipo_analisis == "Análisis de Clusters":
            mostrar_analisis_clusters(df)
            
except Exception as e:
    st.error(f"Ha ocurrido un error en la aplicación: {str(e)}")
    st.code(traceback.format_exc())
    st.info("Recomendación: Verifique la estructura de los archivos y las importaciones del proyecto.")