import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import traceback

# Importar la función para cargar datos
from google_connection import load_data

# Importar las funciones de análisis y variables necesarias
from analisis_dior import ejecutar_analisis_completo, generar_visualizaciones
# Importar las constantes y funciones necesarias
from analisis_dior import DIMENSIONES, interpretar_promedio
from analisis_dior import MAPEO_RESPUESTAS
from analisis_dior import analisis_liderazgo_por_rol, generar_visualizaciones_liderazgo_por_rol
from user_performance_analysis import analizar_desempeno_usuarios, generar_visualizaciones_desempeno

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
    
    # Opciones de análisis
    tipo_analisis = st.sidebar.radio(
        "Seleccione tipo de análisis:",
        ["Vista General", "Dimensiones", "Correlaciones", "Clusters", "Comparativos","Desempeño Usuarios"]
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
            
        # Mostrar el análisis seleccionado según la opción elegida
        if tipo_analisis == "Vista General":
            st.markdown('<div class="section-header">Comedores comunitarios</div>', unsafe_allow_html=True)
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            # Cantidad de comedores
            with col1:
                if "descriptivo" in resultados and "total_comedores" in resultados["descriptivo"]:
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-value">{resultados["descriptivo"]["total_comedores"]}</div>
                        <div class="metric-label">Comedores Analizados</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Cantidad de comunas
            with col2:
                if "descriptivo" in resultados and "distribucion_comunas" in resultados["descriptivo"]:
                    num_comunas = len(resultados["descriptivo"]["distribucion_comunas"])
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-value">{num_comunas}</div>
                        <div class="metric-label">Comunas</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Cantidad de nodos
            with col3:
                if "descriptivo" in resultados and "distribucion_nodos" in resultados["descriptivo"]:
                    num_nodos = len(resultados["descriptivo"]["distribucion_nodos"])
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-value">{num_nodos}</div>
                        <div class="metric-label">Nodos</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Cantidad de nichos
            with col4:
                if "descriptivo" in resultados and "distribucion_nichos" in resultados["descriptivo"]:
                    num_nichos = len(resultados["descriptivo"]["distribucion_nichos"])
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-value">{num_nichos}</div>
                        <div class="metric-label">Nichos</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    
                    
                    
                    
            
            # Distribución general de respuestas
        st.subheader("Distribución General de Respuestas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Crear gráfico de barras horizontales para las respuestas
            if "descriptivo" in resultados and "distribucion_respuestas" in resultados["descriptivo"]:
                dist = resultados["descriptivo"]["distribucion_respuestas"]
                
                # Crear gráfico de barras horizontales
                fig_barras = go.Figure()
                
                # Ordenar por valor de respuesta (1, 2, 3)
                orden_respuestas = {
                    "EN DESACUERDO": 1,
                    "NI DEACUERDO, NI EN DESACUERDO": 2,
                    "DE ACUERDO": 3
                }
                
                dist_ordenada = dist.copy()
                dist_ordenada["Orden"] = dist_ordenada["Respuesta"].map(orden_respuestas)
                dist_ordenada = dist_ordenada.sort_values("Orden")
                
                colores = {
                    "EN DESACUERDO": "#d62728",
                    "NI DEACUERDO, NI EN DESACUERDO": "#ffbb78",
                    "DE ACUERDO": "#2ca02c"
                }
                
                # Añadir barras para cada tipo de respuesta
                for idx, row in dist_ordenada.iterrows():
                    fig_barras.add_trace(go.Bar(
                        y=[row["Respuesta"]],
                        x=[row["Cantidad"]],
                        orientation='h',
                        name=row["Respuesta"],
                        marker_color=colores.get(row["Respuesta"], "#1f77b4"),
                        text=f"{row['Porcentaje']}%",
                        textposition='auto'
                    ))
                
                fig_barras.update_layout(
                    title="Distribución de Respuestas",
                    xaxis_title="Cantidad de Respuestas",
                    yaxis_title="",
                    showlegend=False,
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=20)  # Margen reducido
                )
                
                st.plotly_chart(fig_barras, use_container_width=True)
        
        with col2:
            # Análisis de texto sobre las respuestas - MEJORADO
            if "descriptivo" in resultados and "distribucion_respuestas" in resultados["descriptivo"]:
                dist = resultados["descriptivo"]["distribucion_respuestas"]
                
                # Encontrar la respuesta más común
                respuesta_max = dist.loc[dist["Cantidad"].idxmax()]
                
                # Calcular total de respuestas
                total_respuestas = dist["Cantidad"].sum()
                
                st.markdown(f"""
                <div class="analysis-container">
                    <div class="analysis-title">Análisis de Respuestas</div>
                    <div class="analysis-text">
                        <p>De un total de <span class="highlight-stat">{total_respuestas}</span> respuestas analizadas, la opción "<b>{respuesta_max['Respuesta']}</b>" 
                        fue la más seleccionada con <span class="highlight-stat">{respuesta_max['Cantidad']}</span> respuestas, 
                        representando el <span class="highlight-stat">{respuesta_max['Porcentaje']}%</span> del total.</p>
                        
                """, unsafe_allow_html=True)
                
                for idx, row in dist.iterrows():
                    st.markdown(f"""
                        <li><b>{row['Respuesta']}</b>: {row['Cantidad']} respuestas (<b>{row['Porcentaje']}%</b>)</li>
                    """, unsafe_allow_html=True)
                
                # Determinar interpretación general
                de_acuerdo = dist[dist["Respuesta"] == "DE ACUERDO"]["Porcentaje"].values[0] if "DE ACUERDO" in dist["Respuesta"].values else 0
                desacuerdo = dist[dist["Respuesta"] == "EN DESACUERDO"]["Porcentaje"].values[0] if "EN DESACUERDO" in dist["Respuesta"].values else 0
                
                interpretacion = ""
                color_interpretacion = ""
                if de_acuerdo > 60:
                    interpretacion = "muy favorable, con una fuerte tendencia positiva"
                    color_interpretacion = "#15803d"  # Verde oscuro
                elif de_acuerdo > 40:
                    interpretacion = "generalmente favorable, con una tendencia positiva"
                    color_interpretacion = "#65a30d"  # Verde claro
                elif desacuerdo > 60:
                    interpretacion = "desfavorable, con una tendencia negativa predominante"
                    color_interpretacion = "#b91c1c"  # Rojo oscuro
                elif desacuerdo > 40:
                    interpretacion = "parcialmente desfavorable, con una tendencia negativa"
                    color_interpretacion = "#dc2626"  # Rojo
                else:
                    interpretacion = "mixto, con opiniones divididas"
                    color_interpretacion = "#d97706"  # Amarillo/naranja
                
                st.markdown(f"""
                        </ul>
                        <p>Esto indica un clima organizacional <b style="color:{color_interpretacion}; font-size:1.1rem;">{interpretacion}</b> en los comedores comunitarios analizados.</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Distribución demográfica
        if show_details:
            st.markdown('<div class="section-header">Distribución Demográfica</div>', unsafe_allow_html=True)
            
            # Primera fila: Distribución por comuna
            col1, col2 = st.columns(2)
            
            with col1:
                # Tabla de distribución por comuna
                if "descriptivo" in resultados and "distribucion_comunas" in resultados["descriptivo"]:
                    comunas_df = resultados["descriptivo"]["distribucion_comunas"]
                    
                    # Ordenar por cantidad (de mayor a menor)
                    comunas_df = comunas_df.sort_values(by="Cantidad", ascending=False)
                    
                    # Calcular el porcentaje del total
                    total_comedores = comunas_df["Cantidad"].sum()
                    comunas_df["Porcentaje"] = round((comunas_df["Cantidad"] / total_comedores) * 100, 2)
                    
                    st.markdown('<div class="table-container"><div class="table-title">Distribución de Comedores por Comuna</div>', unsafe_allow_html=True)
                    
                    # Aplicar estilo a la tabla
                    st.dataframe(
                        comunas_df,
                        column_config={
                            "Comuna": "Comuna",
                            "Cantidad": st.column_config.NumberColumn("Cantidad de Comedores", format="%d"),
                            "Porcentaje": st.column_config.NumberColumn("Porcentaje", format="%.2f%%")
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # Análisis de texto sobre distribución por comuna - MEJORADO
                if "descriptivo" in resultados and "distribucion_comunas" in resultados["descriptivo"]:
                    comunas_df = resultados["descriptivo"]["distribucion_comunas"]
                    
                    # Ordenar por cantidad (de mayor a menor)
                    comunas_df = comunas_df.sort_values(by="Cantidad", ascending=False)
                    
                    # Obtener comuna con más comedores
                    comuna_max = comunas_df.iloc[0]
                    
                    # Obtener comuna con menos comedores
                    comuna_min = comunas_df.iloc[-1]
                    
                    # Calcular el porcentaje del total
                    total_comedores = comunas_df["Cantidad"].sum()
                    porcentaje_max = round((comuna_max["Cantidad"] / total_comedores) * 100, 2)
                    
                    # Calcular concentración (% de comedores en top 3 comunas)
                    top3_comunas = comunas_df.head(3)
                    porcentaje_top3 = round((top3_comunas["Cantidad"].sum() / total_comedores) * 100, 2)
                    
                    # Primera parte - MEJORADA
                    st.markdown(f"""
                    <div class="analysis-container">
                        <div class="analysis-title">Análisis de Distribución por Comuna</div>
                        <div class="analysis-text">
                            <p>La distribución de comedores por comuna muestra que <span class="highlight-stat">{comuna_max['Comuna']}</span> tiene la mayor 
                            concentración con <b>{comuna_max['Cantidad']}</b> comedores, representando el <span class="highlight-stat">{porcentaje_max}%</span> 
                            del total.</p>
                    """, unsafe_allow_html=True)

                    # Segunda parte - las tres comunas principales - MEJORADA
                    top3_str = ', '.join([f"<b>{comuna}</b>" for comuna in top3_comunas['Comuna'].tolist()])
                    concentracion = 'alta' if porcentaje_top3 > 50 else 'moderada'
                    st.markdown(f"""        
                            <p>Las tres comunas principales ({top3_str}) concentran el
                            <span class="highlight-stat">{porcentaje_top3}%</span> de todos los comedores, lo que indica una 
                            <b style="color: {'#b91c1c' if porcentaje_top3 > 50 else '#d97706'};">{concentracion}</b> concentración geográfica.</p>
                    """, unsafe_allow_html=True)

                    # Tercera parte - MEJORADA
                    st.markdown(f"""
                            <p>Por otro lado, <b>{comuna_min['Comuna']}</b> presenta la menor presencia con sólo 
                            <b>{comuna_min['Cantidad']}</b> comedores.</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                                        
            # Segunda fila: Distribución por nodo
            st.markdown("<br>", unsafe_allow_html=True)  # Espacio entre filas
            col3, col4 = st.columns(2)
            
            with col3:
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
                    
                    fig_nodos.update_layout(
                        xaxis_title="Nodo", 
                        yaxis_title="Número de Comedores",
                        margin=dict(l=20, r=20, t=40, b=20)  # Margen reducido
                    )
                    st.plotly_chart(fig_nodos, use_container_width=True)
            
            with col4:
                # Análisis de texto sobre distribución por nodo - MEJORADO
                if "descriptivo" in resultados and "distribucion_nodos" in resultados["descriptivo"]:
                    nodos_df = resultados["descriptivo"]["distribucion_nodos"]
                    
                    # Ordenar por cantidad (de mayor a menor)
                    nodos_df = nodos_df.sort_values(by="Cantidad", ascending=False)
                    
                    # Obtener nodo con más comedores
                    nodo_max = nodos_df.iloc[0]
                    
                    # Obtener nodo con menos comedores
                    nodo_min = nodos_df.iloc[-1]
                    
                    # Calcular el porcentaje del total
                    total_comedores = nodos_df["Cantidad"].sum()
                    porcentaje_max = round((nodo_max["Cantidad"] / total_comedores) * 100, 2)
                    
                    # Calcular la diferencia entre el máximo y mínimo
                    diferencia = nodo_max["Cantidad"] - nodo_min["Cantidad"]
                    
                    # Para la primera parte - MEJORADA
                st.markdown(f"""
                <div class="analysis-container">
                    <div class="analysis-title">Análisis de Distribución por Nodo</div>
                    <div class="analysis-text">
                        <p>El análisis por nodo muestra que <span class="highlight-stat">Nodo {nodo_max['Nodo']}</span> alberga la mayor cantidad con 
                        <b>{nodo_max['Cantidad']}</b> comedores, representando el <span class="highlight-stat">{porcentaje_max}%</span> del total.</p>
                """, unsafe_allow_html=True)

                # Segunda parte - MEJORADA
                st.markdown(f"""
                        <p>La diferencia entre el nodo más poblado (<b>Nodo {nodo_max['Nodo']}</b>) y el menos poblado 
                        (<b>Nodo {nodo_min['Nodo']}</b> con {nodo_min['Cantidad']} comedores) es de <span class="highlight-stat">{diferencia}</span> comedores.</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)                  
                        
                        
                        
                        
                        
                        
                        
                        
                        
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
                    
                    # --- INICIO: Código nuevo para mostrar comedores por pregunta ---

                    st.markdown("---") # Separador visual
                    st.subheader("Explorar Comedores por Pregunta Específica")

                    # Crear lista de preguntas para el selector (usando los nombres originales de las columnas)
                    lista_preguntas_originales = list(promedio_preguntas.keys())
                    # Crear nombres más legibles para el dropdown
                    nombres_legibles_preguntas = [p.replace("_", " ").replace(".", ". ", 1) for p in lista_preguntas_originales]

                    # Crear un mapeo de nombre legible a nombre original
                    mapeo_legible_original = dict(zip(nombres_legibles_preguntas, lista_preguntas_originales))

                    # Selector para la pregunta específica
                    pregunta_legible_seleccionada = st.selectbox(
                        "Selecciona una pregunta para ver los comedores que respondieron:",
                        nombres_legibles_preguntas,
                        key=f"select_pregunta_{dimension_seleccionada}" # Clave única para el widget
                    )

                    if pregunta_legible_seleccionada:
                        # Obtener el nombre original de la columna de la pregunta
                        pregunta_seleccionada_original = mapeo_legible_original[pregunta_legible_seleccionada]

                        # ---- CORRECCIÓN AQUÍ ----
                        # Acceder a df_prep desde el diccionario 'resultados'
                        df_preparado = resultados.get("datos_preparados")
                        # -------------------------

                        # Asegurarse de que df_preparado esté disponible y tenga las columnas necesarias
                        if df_preparado is not None and pregunta_seleccionada_original in df_preparado.columns and "NOMBRE_COMEDOR" in df_preparado.columns:

                            # Identificar las filas (comedores) que tienen una respuesta válida (1, 2 o 3)
                            comedores_respondieron = df_preparado[df_preparado[pregunta_seleccionada_original].isin([1, 2, 3])]

                            if not comedores_respondieron.empty:
                                st.markdown(f"**Comedores que respondieron a la pregunta '{pregunta_legible_seleccionada}':**")

                                # Mapeo inverso para mostrar la respuesta textual
                                MAPEO_INVERSO = {v: k for k, v in MAPEO_RESPUESTAS.items()} # Asegúrate que MAPEO_RESPUESTAS esté disponible o importado

                                # Seleccionar y renombrar columnas para mostrar
                                df_mostrar = comedores_respondieron[["NOMBRE_COMEDOR", pregunta_seleccionada_original]].copy()
                                df_mostrar.rename(columns={
                                    "NOMBRE_COMEDOR": "Nombre del Comedor",
                                    pregunta_seleccionada_original: "Respuesta Numérica"
                                }, inplace=True)

                                # Añadir respuesta textual
                                df_mostrar["Respuesta Textual"] = df_mostrar["Respuesta Numérica"].map(MAPEO_INVERSO)

                                # Mostrar en una tabla expandible o dataframe
                                with st.expander(f"Ver los {len(df_mostrar)} comedores"):
                                     st.dataframe(
                                        df_mostrar[["Nombre del Comedor", "Respuesta Numérica", "Respuesta Textual"]],
                                        hide_index=True,
                                        use_container_width=True
                                    )
                            else:
                                st.info(f"No se encontraron respuestas registradas para la pregunta '{pregunta_legible_seleccionada}'.")
                        else:
                            st.warning("No se pudo acceder a los datos de los comedores preparados para esta pregunta.")

                    # --- FIN: Código nuevo ---
            
                # Código para la sección "Correlaciones" en app.py que deberías reemplazar
        elif tipo_analisis == "Correlaciones":
            st.markdown('<div class="section-header">Análisis Comparativo de Liderazgo por Rol</div>', unsafe_allow_html=True)
            
            st.markdown("""
            Este análisis compara las percepciones sobre liderazgo entre gestores principales y auxiliares,
            enfocándose en las siguientes preguntas:
            
            - **2.1_LIDERAZGO_RESPESTUOSO**: Evaluación del respeto en el liderazgo
            - **2.2_OPORTUNIDAD_DE_PROPONER_IDEAS**: Oportunidades para proponer ideas
            - **2.3_ESPACIOS_ADECUADOS_RETROALIMENTACION**: Espacios para retroalimentación
            
            El objetivo es identificar si existen diferencias significativas en la percepción del liderazgo 
            según el rol desempeñado.
            """)
            
            # Ejecutar análisis de liderazgo por rol
            with st.spinner("Analizando datos de liderazgo por rol..."):
                # Asumimos que df_prep ya está disponible desde el código anterior
                resultados_liderazgo = analisis_liderazgo_por_rol(resultados["datos_preparados"])
                figuras_liderazgo = generar_visualizaciones_liderazgo_por_rol(resultados_liderazgo)
            
            if "error" in resultados_liderazgo:
                st.error(resultados_liderazgo["error"])
            else:
                # Mostrar métricas generales
                st.subheader("Disponibilidad de datos por rol")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total de comedores", 
                        resultados_liderazgo["total_comedores"]
                    )
                
                with col2:
                    st.metric(
                        "Con gestores principales", 
                        resultados_liderazgo["comedores_con_principal"]
                    )
                
                with col3:
                    st.metric(
                        "Con gestores auxiliares", 
                        resultados_liderazgo["comedores_con_auxiliar"]
                    )
                
                with col4:
                    st.metric(
                        "Con ambos roles", 
                        resultados_liderazgo["comedores_con_ambos_roles"],
                        delta=f"{resultados_liderazgo['comedores_con_ambos_roles'] / resultados_liderazgo['total_comedores'] * 100:.1f}%"
                    )
                
                # Mostrar visualizaciones
                st.subheader("Comparación Global de Percepción por Rol")
                
                if "comparacion_global" in figuras_liderazgo:
                    st.plotly_chart(figuras_liderazgo["comparacion_global"], use_container_width=True)
                
                if "diferencias_global" in figuras_liderazgo:
                    st.plotly_chart(figuras_liderazgo["diferencias_global"], use_container_width=True)
                
                # Mostrar distribución de concordancia
                st.subheader("Concordancia entre Roles")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if "distribucion_concordancia" in figuras_liderazgo:
                        st.plotly_chart(figuras_liderazgo["distribucion_concordancia"], use_container_width=True)
                
                with col2:
                    # Explicación de los niveles de concordancia
                    st.markdown(f"""
                    <div class="analysis-container">
                        <div class="analysis-title">Interpretación de Concordancia</div>
                        <div class="analysis-text">
                            <p>La concordancia indica qué tan similares son las percepciones entre gestores principales y auxiliares:</p>
                            <ul>
                                <li><b>Alta concordancia</b>: Diferencia promedio ≤ 0.5 puntos</li>
                                <li><b>Media concordancia</b>: Diferencia promedio entre 0.5 y 1 punto</li>
                                <li><b>Baja concordancia</b>: Diferencia promedio > 1 punto</li>
                            </ul>
                            <p>Entre los {resultados_liderazgo["comedores_con_ambos_roles"]} comedores que tienen ambos roles:</p>
                            <ul>
                                <li><b>{resultados_liderazgo["resumen_concordancia"]["Alta"]}</b> comedores muestran alta concordancia</li>
                                <li><b>{resultados_liderazgo["resumen_concordancia"]["Media"]}</b> comedores muestran concordancia media</li>
                                <li><b>{resultados_liderazgo["resumen_concordancia"]["Baja"]}</b> comedores muestran baja concordancia</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Mostrar comedores con mayor diferencia
                st.subheader("Comedores con Mayor Diferencia de Percepción")
                
                if "top_comedores_diferencia" in figuras_liderazgo:
                    st.plotly_chart(figuras_liderazgo["top_comedores_diferencia"], use_container_width=True)
                
                # Tabla detallada para exploración
                st.subheader("Exploración Detallada por Comedor")
                
                # Selector de comedor
                if "analisis_comedores" in resultados_liderazgo and resultados_liderazgo["analisis_comedores"]:
                    comedores = list(resultados_liderazgo["analisis_comedores"].keys())
                    comedor_seleccionado = st.selectbox("Selecciona un comedor para ver detalles:", comedores)
                    
                    if comedor_seleccionado and comedor_seleccionado in resultados_liderazgo["analisis_comedores"]:
                        datos_comedor = resultados_liderazgo["analisis_comedores"][comedor_seleccionado]
                        
                        # Mostrar concordancia global
                        st.markdown(f"""
                        <div style="background-color:#f0f2f6; padding:10px; border-radius:5px; margin-bottom:10px;">
                            <b>Concordancia global:</b> {datos_comedor["concordancia_global"]} 
                            (Diferencia promedio: {datos_comedor["diferencia_promedio"]:.2f} puntos)
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Crear tabla de detalles por pregunta
                        detalles = []
                        
                        for pregunta, datos in datos_comedor["analisis_preguntas"].items():
                            # Nombre más legible de la pregunta
                            nombre_legible = pregunta.replace("_", " ")
                            if pregunta == "2.1_LIDERAZGO_RESPESTUOSO":
                                nombre_legible = "Liderazgo Respetuoso"
                            elif pregunta == "2.2_OPORTUNIDAD_DE_PROPONER_IDEAS":
                                nombre_legible = "Oportunidad de Proponer Ideas"
                            elif pregunta == "2.3_ESPACIOS_ADECUADOS_RETROALIMENTACION":
                                nombre_legible = "Espacios para Retroalimentación"
                            
                            detalles.append({
                                "Pregunta": nombre_legible,
                                "Principal": f"{datos['promedio_principal']:.2f}",
                                "Auxiliar": f"{datos['promedio_auxiliar']:.2f}",
                                "Diferencia": f"{datos['diferencia']:.2f}",
                                "Concordancia": datos["concordancia"]
                            })
                        
                        # Convertir a DataFrame
                        df_detalles = pd.DataFrame(detalles)
                        
                        # Mostrar tabla con formato condicional
                        st.dataframe(
                            df_detalles,
                            column_config={
                                "Pregunta": "Pregunta",
                                "Principal": "Gestor Principal",
                                "Auxiliar": "Gestor Auxiliar",
                                "Diferencia": "Diferencia",
                                "Concordancia": st.column_config.TextColumn(
                                    "Nivel de Concordancia",
                                    help="Alta: diferencia ≤ 0.5, Media: diferencia ≤ 1, Baja: diferencia > 1"
                                )
                            },
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Crear un gráfico de radar para este comedor específico
                        import plotly.graph_objects as go
                        
                        # Datos para el radar
                        preguntas = [pregunta["Pregunta"] for pregunta in detalles]
                        valores_principal = [float(pregunta["Principal"]) for pregunta in detalles]
                        valores_auxiliar = [float(pregunta["Auxiliar"]) for pregunta in detalles]
                        
                        fig_radar = go.Figure()
                        
                        fig_radar.add_trace(go.Scatterpolar(
                            r=valores_principal,
                            theta=preguntas,
                            fill='toself',
                            name='Gestor Principal'
                        ))
                        
                        fig_radar.add_trace(go.Scatterpolar(
                            r=valores_auxiliar,
                            theta=preguntas,
                            fill='toself',
                            name='Gestor Auxiliar'
                        ))
                        
                        fig_radar.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 3]
                                )
                            ),
                            title=f"Comparación de Percepciones en {comedor_seleccionado}",
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig_radar, use_container_width=True)
                        
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
            
            # Tabla detallada de comparación
            if "comparativo" in resultados and "comparacion_comunas" in resultados["comparativo"]:
                st.markdown("#### Tabla detallada de puntuaciones por comuna:")
                
                comp_comunas = resultados["comparativo"]["comparacion_comunas"]
                
                # Añadir una columna de promedio general
                comp_comunas["Promedio General"] = comp_comunas.mean(axis=1)
                
                # Estilo condicional
                st.dataframe(comp_comunas.style.background_gradient(cmap="YlGnBu"), use_container_width=True)



# 3. Añadir la lógica para la nueva página de desempeño de usuarios
# Añadir este bloque de código al final de la estructura condicional que maneja los tipos de análisis
# (después del último "elif tipo_analisis == "Comparativos":")

        
        # Sección simplificada para mostrar solo hasta promedio de registros por día

        # Sección simplificada para mostrar solo hasta promedio de registros por día

        elif tipo_analisis == "Desempeño Usuarios":
            st.markdown('<div class="section-header">Análisis de Desempeño de Usuarios</div>', unsafe_allow_html=True)
            
            st.markdown("""
            Esta sección analiza el desempeño de los usuarios que realizaron los registros de visita a los comedores comunitarios,
            evaluando la cantidad de registros y eficiencia por día.
            """)
            
            # Ejecutar análisis de desempeño de usuarios
            with st.spinner("Analizando datos de usuarios... Por favor espera."):
                resultados_usuarios = analizar_desempeno_usuarios(df)
                figuras_usuarios = generar_visualizaciones_desempeno(resultados_usuarios)
            
            if "error" in resultados_usuarios:
                st.error(resultados_usuarios["error"])
            else:
                # Métricas principales
                st.subheader("Métricas Generales")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Total de Usuarios", 
                        resultados_usuarios["total_usuarios"]
                    )
                
                with col2:
                    st.metric(
                        "Total de Registros", 
                        resultados_usuarios["total_registros"]
                    )
                
                with col3:
                    # Promedio de registros por usuario
                    promedio_registros = resultados_usuarios["total_registros"] / resultados_usuarios["total_usuarios"] if resultados_usuarios["total_usuarios"] > 0 else 0
                    st.metric(
                        "Promedio de Registros/Usuario", 
                        f"{promedio_registros:.1f}"
                    )
                
                # Análisis de registros por usuario
                st.subheader("Cantidad de Registros por Usuario")
                
                if "registros_por_usuario" in figuras_usuarios:
                    st.plotly_chart(figuras_usuarios["registros_por_usuario"], use_container_width=True)
                
                # Tabla detallada de registros
                if "conteo_por_usuario" in resultados_usuarios:
                    conteo_df = resultados_usuarios["conteo_por_usuario"]
                    
                    with st.expander("Ver tabla detallada de registros por usuario"):
                        st.dataframe(
                            conteo_df,
                            column_config={
                                "Usuario": "Usuario",
                                "Cantidad de Registros": st.column_config.NumberColumn("Cantidad de Registros", format="%d"),
                                "Porcentaje del Total": st.column_config.NumberColumn("% del Total", format="%.2f%%")
                            },
                            use_container_width=True,
                            hide_index=True
                        )
                
                # Análisis de eficiencia por fecha
                st.subheader("Eficiencia por Día de Visita")
                
                if "eficiencia_por_usuario" in resultados_usuarios:
                    # Mostrar mensaje informativo sobre la columna de fecha utilizada
                    if "columna_fecha_usada" in resultados_usuarios:
                        st.info(f"Se utilizó la columna '{resultados_usuarios['columna_fecha_usada']}' para el análisis de fechas.")
                    
                    # Mostrar tabla de eficiencia por usuario
                    eficiencia_df = resultados_usuarios["eficiencia_por_usuario"]
                    
                    st.dataframe(
                        eficiencia_df,
                        column_config={
                            "Usuario": "Usuario",
                            "Dias de Visita": st.column_config.NumberColumn("Días de Visita", format="%d"),
                            "Cantidad de Registros": st.column_config.NumberColumn("Total de Registros", format="%d"),
                            "Promedio Registros por Día": st.column_config.NumberColumn("Promedio por Día", format="%.2f")
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Mostrar gráfico de eficiencia
                    if "eficiencia_por_dia" in figuras_usuarios:
                        st.plotly_chart(figuras_usuarios["eficiencia_por_dia"], use_container_width=True)
                else:
                    if "error_fecha" in resultados_usuarios:
                        st.warning(f"No se pudo realizar el análisis por fecha: {resultados_usuarios['error_fecha']}")
                    else:
                        st.warning("No hay datos suficientes para analizar la eficiencia por día de visita.")
                        
                
            
            
            
                    
except Exception as e:
    st.error(f"Ha ocurrido un error en la aplicación: {str(e)}")
    st.code(traceback.format_exc())
    st.info("Recomendación: Verifique la conexión con Google Sheets y la estructura de los datos.")

