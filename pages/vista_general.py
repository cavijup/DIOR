import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def mostrar_vista_general(resultados, figuras, show_details):
    """
    Muestra la página de vista general con métricas y distribuciones principales.
    
    Args:
        resultados: Diccionario con los resultados del análisis
        figuras: Diccionario con las figuras generadas
        show_details: Booleano que indica si se deben mostrar detalles adicionales
    """
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
        mostrar_distribucion_demografica(resultados)

def mostrar_distribucion_demografica(resultados):
    """
    Muestra los detalles de distribución demográfica (comunas, nodos, etc.)
    
    Args:
        resultados: Diccionario con los resultados del análisis
    """
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
            
            fig_nodos = go.Figure(data=[
                go.Bar(
                    x=nodos["Nodo"],
                    y=nodos["Cantidad"],
                    marker_color='#4f7aee'
                )
            ])
            
            fig_nodos.update_layout(
                title="Distribución de Comedores por Nodo",
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