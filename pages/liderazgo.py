import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from analisis_dior import analisis_liderazgo_por_rol, generar_visualizaciones_liderazgo_por_rol

def mostrar_liderazgo(resultados, df):
    """
    Muestra la página de análisis comparativo de liderazgo por rol.
    
    Args:
        resultados: Diccionario con los resultados del análisis general
        df: DataFrame con los datos originales
    """
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
        mostrar_metricas_liderazgo(resultados_liderazgo)
        mostrar_visualizaciones_liderazgo(figuras_liderazgo)
        mostrar_detalle_por_comedor(resultados_liderazgo)

def mostrar_metricas_liderazgo(resultados_liderazgo):
    """
    Muestra las métricas generales del análisis de liderazgo.
    
    Args:
        resultados_liderazgo: Diccionario con los resultados del análisis de liderazgo
    """
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

def mostrar_visualizaciones_liderazgo(figuras_liderazgo):
    """
    Muestra las visualizaciones del análisis de liderazgo.
    
    Args:
        figuras_liderazgo: Diccionario con las figuras del análisis de liderazgo
    """
    # Mostrar visualizaciones
    st.subheader("Comparación Global de Percepción por Rol")
    
    if "comparacion_global" in figuras_liderazgo:
        st.plotly_chart(figuras_liderazgo["comparacion_global"], use_container_width=True)
    
    # Se ha eliminado la visualización de diferencias entre roles
    
    # Mostrar distribución de concordancia
    st.subheader("Concordancia entre Roles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if "distribucion_concordancia" in figuras_liderazgo:
            st.plotly_chart(figuras_liderazgo["distribucion_concordancia"], use_container_width=True)
    
    with col2:
        # Explicación de los niveles de concordancia
        mostrar_explicacion_concordancia(figuras_liderazgo)
    
    # Mostrar comedores con mayor diferencia
    st.subheader("Comedores con Mayor Diferencia de Percepción")
    
    if "top_comedores_diferencia" in figuras_liderazgo:
        st.plotly_chart(figuras_liderazgo["top_comedores_diferencia"], use_container_width=True)

def mostrar_explicacion_concordancia(figuras_liderazgo):
    """
    Muestra la explicación de los niveles de concordancia.
    
    Args:
        figuras_liderazgo: Diccionario con las figuras del análisis de liderazgo
    """
    # Extraer y mostrar información de concordancia
    if "resumen_concordancia" in figuras_liderazgo:
        resumen_concordancia = figuras_liderazgo["resumen_concordancia"]
        comedores_con_ambos_roles = sum(resumen_concordancia.values())
        
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
                <p>Entre los {comedores_con_ambos_roles} comedores que tienen ambos roles:</p>
                <ul>
                    <li><b>{resumen_concordancia.get("Alta", 0)}</b> comedores muestran alta concordancia</li>
                    <li><b>{resumen_concordancia.get("Media", 0)}</b> comedores muestran concordancia media</li>
                    <li><b>{resumen_concordancia.get("Baja", 0)}</b> comedores muestran baja concordancia</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_detalle_por_comedor(resultados_liderazgo):
    """
    Muestra la exploración detallada por comedor.
    
    Args:
        resultados_liderazgo: Diccionario con los resultados del análisis de liderazgo
    """
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
            crear_radar_comedor(detalles, comedor_seleccionado)

def crear_radar_comedor(detalles, comedor_seleccionado):
    """
    Crea un gráfico de radar para el comedor seleccionado.
    
    Args:
        detalles: Lista de diccionarios con los detalles del comedor
        comedor_seleccionado: Nombre del comedor seleccionado
    """
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