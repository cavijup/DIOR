"""
Aplicación principal para el Análisis de Clima Organizacional en Comedores Comunitarios.

Este script es el punto de entrada principal de la aplicación Streamlit.
Gestiona la carga de datos, la configuración de la interfaz de usuario
y la navegación entre las diferentes páginas de análisis.

Autor: Equipo de DIOR Analytics
Versión: 1.0
"""

import pandas as pd
import streamlit as st
import traceback
import os

# Importar la función para cargar datos
from google_connection import load_data

# Importar las funciones de análisis
from analisis_dior import ejecutar_analisis_completo, generar_visualizaciones

# Configuración de la página
st.set_page_config(
    page_title="Análisis DIOR",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS personalizados
def cargar_estilos_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1.5rem;
        background-color: #4ade80;  /* Color verde */
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
        background-color: #f0f9ff;
        padding: 0.8rem;
        border-left: 5px solid #2563EB;
        border-radius: 0 8px 8px 0;
    }

    .metric-container {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease;
    }

    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1E3A8A;
    }

    .metric-label {
        font-size: 1rem;
        color: #4B5563;
        margin-top: 0.5rem;
    }

    .analysis-container {
        background-color: #f0f9ff;  /* Color de fondo más claro */
        border-radius: 10px;
        padding: 1.8rem;  /* Padding incrementado */
        height: 100%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);  /* Sombra más pronunciada */
        border-left: 5px solid #3b82f6;  /* Borde izquierdo para destacar */
        margin-bottom: 1rem;
    }

    .analysis-title {
        font-size: 1.3rem;  /* Tamaño de fuente incrementado */
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1.2rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #dbeafe;  /* Línea divisoria para el título */
    }

    .analysis-text {
        font-size: 1.05rem;  /* Tamaño de fuente incrementado */
        color: #374151;
        line-height: 1.6;  /* Mayor espaciado entre líneas para mejor legibilidad */
    }

    .analysis-text p {
        margin-bottom: 0.8rem;  /* Espacio entre párrafos */
    }

    .analysis-text b {
        color: #1E3A8A;  /* Destacar texto en negrita */
        font-weight: 600;
    }

    .table-container {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    .table-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e5e7eb;
    }

    /* Estilo para destacar elementos importantes en el análisis */
    .highlight-stat {
        font-size: 1.1rem;
        font-weight: 500;
        color: #1d4ed8;
        background-color: #dbeafe;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        display: inline-block;
        margin: 0 0.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Cargar estilos CSS
    cargar_estilos_css()
    
    # Título principal
    st.markdown('<div class="main-header">Análisis de Clima Organizacional en Comedores Comunitarios</div>', unsafe_allow_html=True)

    # Descripción
    st.markdown("""
    Análisis del clima organizacional en los comedores comunitarios,
    basado en la percepción de las gestoras y gestores sobre el relacionamiento, trabajo en equipo,
    liderazgos y sentido de pertenencia.
    """)

    try:
        # Barra lateral con opciones de configuración
        st.sidebar.markdown('## Configuración')
        
        # Número de clusters para el análisis (configuración global)
        n_clusters = st.sidebar.slider(
            "Número de clusters",
            min_value=2,
            max_value=5,
            value=3,
            help="Selecciona el número de grupos para el análisis de clusters"
        )
        
        # Mostrar detalles avanzados (configuración global)
        show_details = st.sidebar.checkbox(
            "Mostrar detalles avanzados",
            value=True,
            help="Activa esta opción para ver análisis más detallados"
        )
        
        # Guardar en session_state para que estén disponibles en todas las páginas
        st.session_state["n_clusters"] = n_clusters
        st.session_state["show_details"] = show_details
        
        # Cargar los datos desde Google Sheets (solo si no están ya cargados)
        if "df" not in st.session_state:
            with st.spinner("Cargando datos de Google Sheets..."):
                df = load_data()
            
                if df is None or df.empty:
                    st.error("No se pudieron cargar datos. Verifique la conexión con Google Sheets.")
                    st.stop()
                else:
                    st.success(f"Datos cargados correctamente. {len(df)} registros encontrados.")
                    st.session_state["df"] = df
        else:
            df = st.session_state["df"]
            
        # Ejecutar análisis inicial (solo si no se ha ejecutado antes o cambia n_clusters)
        cache_key = f"resultados_{n_clusters}"
        if cache_key not in st.session_state:
            with st.spinner("Analizando datos... Por favor espera."):
                resultados = ejecutar_analisis_completo(df_datos=df, n_clusters=n_clusters)
                figuras = generar_visualizaciones(resultados)
                
                # Guardar resultados en la sesión
                st.session_state[cache_key] = (resultados, figuras)
        else:
            resultados, figuras = st.session_state[cache_key]
            
        # Guardar las referencias actuales para uso fácil en la página principal
        st.session_state["resultados_actuales"] = resultados
        st.session_state["figuras_actuales"] = figuras
            
        # En la página principal, mostrar la vista general por defecto
        mostrar_vista_general(resultados, figuras, show_details)
                
    except Exception as e:
        st.error(f"Ha ocurrido un error en la aplicación: {str(e)}")
        st.code(traceback.format_exc())
        st.info("Recomendación: Verifique la conexión con Google Sheets y la estructura de los datos.")

# Esta función se ha importado desde pages/vista_general.py
# Proporcionamos una versión simplificada para que el archivo principal sea independiente
def mostrar_vista_general(resultados, figuras, show_details):
    """
    Muestra la página de vista general con métricas y distribuciones principales.
    
    Esta es una versión simplificada para la página principal. La versión completa
    está en el archivo pages/vista_general.py
    
    Args:
        resultados: Diccionario con los resultados del análisis
        figuras: Diccionario con las figuras generadas
        show_details: Booleano que indica si se deben mostrar detalles adicionales
    """
    st.markdown('<div class="section-header">Vista General del Clima Organizacional</div>', unsafe_allow_html=True)
    
    # Métricas principales
    if "descriptivo" in resultados and "total_comedores" in resultados["descriptivo"]:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Comedores Analizados", resultados["descriptivo"]["total_comedores"])
        
        if "distribucion_comunas" in resultados["descriptivo"]:
            with col2:
                st.metric("Comunas", len(resultados["descriptivo"]["distribucion_comunas"]))
        
        if "distribucion_nodos" in resultados["descriptivo"]:
            with col3:
                st.metric("Nodos", len(resultados["descriptivo"]["distribucion_nodos"]))
        
        if "distribucion_nichos" in resultados["descriptivo"]:
            with col4:
                st.metric("Nichos", len(resultados["descriptivo"]["distribucion_nichos"]))
    
    # Mostrar gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        if "distribucion_respuestas" in figuras:
            st.plotly_chart(figuras["distribucion_respuestas"], use_container_width=True)
    
    with col2:
        if "promedios_dimensiones" in figuras:
            st.plotly_chart(figuras["promedios_dimensiones"], use_container_width=True)
    
    # Mostrar instrucciones para navegar a más análisis
    st.info("👈 Utilice el menú de navegación en la barra lateral para explorar análisis más detallados")

if __name__ == "__main__":
    main()