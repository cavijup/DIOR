import pandas as pd
import streamlit as st
import traceback

# Importar la función para cargar datos
from google_connection import load_data

# Importar páginas
from pages.vista_general import mostrar_vista_general
from pages.dimensiones import mostrar_dimensiones
from pages.liderazgo import mostrar_liderazgo
from pages.clusters import mostrar_clusters
from pages.desempeno_usuarios import mostrar_desempeno_usuarios



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
        # Barra lateral con opciones
        st.sidebar.markdown('## Configuración')
        
        # Opciones de análisis (removida la opción "Comparativos")
        tipo_analisis = st.sidebar.radio(
            "Seleccione tipo de análisis:",
            ["Vista General", "Dimensiones", "Liderazgo", "Clusters", "Desempeño Usuarios"]
        )
        
        # Número de clusters para el análisis
        n_clusters = st.sidebar.slider(
            "Número de clusters",
            min_value=2,
            max_value=5,
            value=3,
            help="Selecciona el número de grupos para el análisis de clusters"
        )
        
        # Mostrar detalles avanzados
        show_details = st.sidebar.checkbox(
            "Mostrar detalles avanzados",
            value=True,
            help="Activa esta opción para ver análisis más detallados"
        )
        
        # Cargar los datos desde Google Sheets
        with st.spinner("Cargando datos de Google Sheets..."):
            df = load_data()
        
        if df is None or df.empty:
            st.error("No se pudieron cargar datos. Verifique la conexión con Google Sheets.")
        else:
            st.success(f"Datos cargados correctamente. {len(df)} registros encontrados.")
            
            # Ejecutar análisis
            with st.spinner("Analizando datos... Por favor espera."):
                resultados = ejecutar_analisis_completo(df_datos=df, n_clusters=n_clusters)
                figuras = generar_visualizaciones(resultados)
                
            # Mostrar la página seleccionada según la opción elegida
            if tipo_analisis == "Vista General":
                mostrar_vista_general(resultados, figuras, show_details)
            elif tipo_analisis == "Dimensiones":
                mostrar_dimensiones(resultados, figuras)
            elif tipo_analisis == "Liderazgo":
                mostrar_liderazgo(resultados, df)
            elif tipo_analisis == "Clusters":
                mostrar_clusters(resultados, figuras, n_clusters)
            elif tipo_analisis == "Desempeño Usuarios":
                mostrar_desempeno_usuarios(df)
                
    except Exception as e:
        st.error(f"Ha ocurrido un error en la aplicación: {str(e)}")
        st.code(traceback.format_exc())
        st.info("Recomendación: Verifique la conexión con Google Sheets y la estructura de los datos.")

if __name__ == "__main__":
    main()