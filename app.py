import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import traceback

# Importar la función para cargar datos
from google_connection import load_data

# Importar las funciones de análisis existentes
from analisis_dior import ejecutar_analisis_completo, generar_visualizaciones

# Configuración de la página
st.set_page_config(
    page_title="Análisis DIOR",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 1rem;
        color: #4B5563;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<div class="main-header">Análisis de Clima Organizacional en Comedores Comunitarios</div>', unsafe_allow_html=True)

# Descripción
st.markdown("""
Este dashboard muestra el análisis del clima organizacional en los comedores comunitarios,
basado en la percepción de las gestoras y gestores sobre el relacionamiento, trabajo en equipo,
liderazgos y sentido de pertenencia.
""")

try:
    # Barra lateral con opciones
    st.sidebar.markdown('## Configuración')
    
    # Opciones de análisis
    tipo_analisis = st.sidebar.radio(
        "Seleccione tipo de análisis:",
        ["Vista General", "Dimensiones", "Correlaciones", "Clusters", "Comparativos"]
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
        value=False,
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
            
        # Mostrar el análisis seleccionado según la opción elegida
        if tipo_analisis == "Vista General":
            st.markdown('<div class="section-header">Dashboard Principal</div>', unsafe_allow_html=True)
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if "descriptivo" in resultados and "total_comedores" in resultados["descriptivo"]:
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-value">{resultados["descriptivo"]["total_comedores"]}</div>
                        <div class="metric-label">Comedores Analizados</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                if "dimensiones" in resultados and "dimension_mejor" in resultados["dimensiones"]:
                    mejor_dim = resultados["dimensiones"]["dimension_mejor"]
                    mejor_val = resultados["dimensiones"]["promedio_mejor"]
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-value">{mejor_dim}</div>
                        <div class="metric-label">Mejor Dimensión ({mejor_val:.2f})</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                if "dimensiones" in resultados and "dimension_peor" in resultados["dimensiones"]:
                    peor_dim = resultados["dimensiones"]["dimension_peor"]
                    peor_val = resultados["dimensiones"]["promedio_peor"]
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-value">{peor_dim}</div>
                        <div class="metric-label">Dimensión a Mejorar ({peor_val:.2f})</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col4:
                # Calcular promedio general
                if "datos_preparados" in resultados:
                    todas_preguntas = []
                    for dimension, preguntas in DIMENSIONES.items():
                        todas_preguntas.extend([p for p in preguntas if p in resultados["datos_preparados"].columns])
                    
                    if todas_preguntas:
                        prom_general = resultados["datos_preparados"][todas_preguntas].mean().mean()
                        interpretacion = interpretar_promedio(prom_general)
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-value">{prom_general:.2f}</div>
                            <div class="metric-label">Puntuación General ({interpretacion})</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Distribución general de respuestas
            st.subheader("Distribución General de Respuestas")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if "descriptivo" in resultados and "distribucion_respuestas" in resultados["descriptivo"]:
                    st.dataframe(resultados["descriptivo"]["distribucion_respuestas"], use_container_width=True)
            
            with col2:
                if "distribucion_respuestas" in figuras:
                    st.plotly_chart(figuras["distribucion_respuestas"], use_container_width=True)
            
            # Distribución demográfica
            if show_details:
                st.subheader("Distribución Demográfica")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if "distribucion_comunas" in figuras:
                        st.plotly_chart(figuras["distribucion_comunas"], use_container_width=True)
                
                with col2:
                    if "descriptivo" in resultados and "distribucion_nodos" in resultados["descriptivo"]:
                        nodos = resultados["descriptivo"]["distribucion_nodos"]
                        
                        fig_nodos = px.bar(
                            nodos,
                            x="Nodo",
                            y="Cantidad",
                            title="Distribución de Comedores por Nodo",
                            color="Cantidad",
                            color_continuous_scale="Viridis"
                        )
                        
                        fig_nodos.update_layout(xaxis_title="Nodo", yaxis_title="Número de Comedores")
                        st.plotly_chart(fig_nodos, use_container_width=True)
                        
        elif tipo_analisis == "Dimensiones":
            st.markdown('<div class="section-header">Análisis por Dimensiones</div>', unsafe_allow_html=True)
            
            # Puntuación promedio por dimensión
            st.subheader("Puntuación Promedio por Dimensión")
            
            # Mostrar gráfico de barras y radar para las dimensiones
            col1, col2 = st.columns(2)
            
            with col1:
                if "promedios_dimensiones" in figuras:
                    st.plotly_chart(figuras["promedios_dimensiones"], use_container_width=True)
            
            with col2:
                if "radar_dimensiones" in figuras:
                    st.plotly_chart(figuras["radar_dimensiones"], use_container_width=True)
            
            # Análisis detallado por dimensión
            st.subheader("Análisis Detallado por Dimensión")
            
            # Selector de dimensión
            if "dimensiones" in resultados and "analisis_preguntas" in resultados["dimensiones"]:
                analisis_preguntas = resultados["dimensiones"]["analisis_preguntas"]
                
                dimension_seleccionada = st.selectbox(
                    "Selecciona una dimensión para ver detalles:",
                    list(analisis_preguntas.keys())
                )
                
                if dimension_seleccionada:
                    preguntas = analisis_preguntas[dimension_seleccionada]
                    
                    # Mostrar promedios de las preguntas en esta dimensión
                    promedio_preguntas = {pregunta: datos["promedio"] for pregunta, datos in preguntas.items()}
                    df_promedio = pd.DataFrame({
                        "Pregunta": [p.replace("_", " ") for p in promedio_preguntas.keys()],
                        "Promedio": list(promedio_preguntas.values())
                    })
                    
                    fig_prom_dim = px.bar(
                        df_promedio,
                        x="Pregunta",
                        y="Promedio",
                        title=f"Promedios de Preguntas en {dimension_seleccionada}",
                        color="Promedio",
                        color_continuous_scale="YlGnBu",
                        text="Promedio"
                    )
                    
                    fig_prom_dim.update_traces(texttemplate="%{text:.2f}", textposition="outside")
                    fig_prom_dim.update_layout(
                        xaxis_title="Pregunta",
                        yaxis_title="Puntuación Promedio (1-3)",
                        yaxis=dict(range=[0, 3.2])
                    )
                    
                    st.plotly_chart(fig_prom_dim, use_container_width=True)
            
        elif tipo_analisis == "Correlaciones":
            st.markdown('<div class="section-header">Análisis de Correlaciones</div>', unsafe_allow_html=True)
            
            st.markdown("""
            Este análisis muestra las relaciones entre las diferentes dimensiones y preguntas.
            Una correlación cercana a 1 indica una relación positiva fuerte (cuando una variable aumenta, la otra también).
            Una correlación cercana a -1 indica una relación negativa fuerte (cuando una variable aumenta, la otra disminuye).
            """)
            
            # Matriz de correlación
            st.subheader("Matriz de Correlación entre Preguntas")
            
            if "matriz_correlacion" in figuras:
                st.plotly_chart(figuras["matriz_correlacion"], use_container_width=True)
            
            # Top correlaciones
            st.subheader("Correlaciones Más Significativas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Top Correlaciones Positivas")
                if "correlaciones" in resultados and "top_correlaciones_positivas" in resultados["correlaciones"]:
                    top_pos = resultados["correlaciones"]["top_correlaciones_positivas"]
                    
                    for _, row in top_pos.iterrows():
                        st.markdown(f"""
                        **{row['pregunta1_corta']} y {row['pregunta2_corta']}**: {row['correlacion']:.2f}
                        <br><small>{row['dimension1']} - {row['dimension2']}</small>
                        """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### Top Correlaciones Negativas")
                if "correlaciones" in resultados and "top_correlaciones_negativas" in resultados["correlaciones"]:
                    top_neg = resultados["correlaciones"]["top_correlaciones_negativas"]
                    
                    for _, row in top_neg.iterrows():
                        st.markdown(f"""
                        **{row['pregunta1_corta']} y {row['pregunta2_corta']}**: {row['correlacion']:.2f}
                        <br><small>{row['dimension1']} - {row['dimension2']}</small>
                        """, unsafe_allow_html=True)
                        
        elif tipo_analisis == "Clusters":
            st.markdown('<div class="section-header">Análisis de Clusters</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            Este análisis agrupa los comedores en {n_clusters} clusters (grupos) según la similitud en sus respuestas.
            Cada cluster representa un perfil diferente de clima organizacional.
            """)
            
            # Visualización de clusters en PCA
            st.subheader("Visualización de Clusters")
            
            if "clusters_pca" in figuras:
                st.plotly_chart(figuras["clusters_pca"], use_container_width=True)
            
            # Perfil por clusters
            st.subheader("Perfil de Clusters por Dimensión")
            
            if "perfiles_clusters" in figuras:
                st.plotly_chart(figuras["perfiles_clusters"], use_container_width=True)
            
            # Detalles de cada cluster
            st.subheader("Detalles por Cluster")
            
            if "clusters" in resultados and "perfiles_clusters" in resultados["clusters"]:
                perfiles = resultados["clusters"]["perfiles_clusters"]
                
                for cluster_id, perfil in perfiles.items():
                    with st.expander(f"Cluster {cluster_id} ({perfil['n_comedores']} comedores)"):
                        # Mostrar lista de comedores en el cluster
                        if "comedores" in perfil:
                            st.markdown("#### Comedores en este cluster:")
                            st.write(", ".join(perfil["comedores"]))
                        
                        # Mostrar promedios por dimensión
                        st.markdown("#### Puntuaciones por dimensión:")
                        
                        promedios_dim = pd.DataFrame({
                            "Dimensión": list(perfil["promedios_dimensiones"].keys()),
                            "Puntuación": list(perfil["promedios_dimensiones"].values())
                        })
                        
                        promedios_dim["Interpretación"] = promedios_dim["Puntuación"].apply(interpretar_promedio)
                        promedios_dim = promedios_dim.sort_values("Puntuación", ascending=False)
                        
                        st.dataframe(promedios_dim, use_container_width=True)
                        
        elif tipo_analisis == "Comparativos":
            st.markdown('<div class="section-header">Análisis Comparativo</div>', unsafe_allow_html=True)
            
            # Comparación por comuna
            st.subheader("Comparación por Comuna")
            
            if "comparacion_comunas" in figuras:
                st.plotly_chart(figuras["comparacion_comunas"], use_container_width=True)
            
            # Tabla detallada de comparación
            if "comparativo" in resultados and "comparacion_comunas" in resultados["comparativo"]:
                st.markdown("#### Tabla detallada de puntuaciones por comuna:")
                
                comp_comunas = resultados["comparativo"]["comparacion_comunas"]
                
                # Añadir una columna de promedio general
                comp_comunas["Promedio General"] = comp_comunas.mean(axis=1)
                
                # Estilo condicional
                st.dataframe(comp_comunas.style.background_gradient(cmap="YlGnBu"), use_container_width=True)

except Exception as e:
    st.error(f"Ha ocurrido un error en la aplicación: {str(e)}")
    st.code(traceback.format_exc())
    st.info("Recomendación: Verifique la conexión con Google Sheets y la estructura de los datos.")

# Importar variables DIMENSIONES y función interpretar_promedio de analisis_dior
from analisis_dior import DIMENSIONES, interpretar_promedio