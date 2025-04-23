import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def generar_analisis_descriptivo_comuna(comunas_df):
    """
    Genera un análisis descriptivo textual de la distribución por comuna.
    
    Args:
        comunas_df: DataFrame con la distribución de comedores por comuna (debe tener columnas 'Comuna' y 'Cantidad')
        
    Returns:
        str: Texto HTML con el análisis descriptivo
    """
    if comunas_df.empty:
        return "<p>No hay datos suficientes para analizar la distribución por comuna.</p>"
    
    # Ordenar comunas por cantidad (de mayor a menor)
    comunas_ordenadas = comunas_df.sort_values("Cantidad", ascending=False)
    
    # Obtener número total de comedores y comunas
    total_comedores = comunas_ordenadas["Cantidad"].sum()
    total_comunas = len(comunas_ordenadas)
    
    # Obtener las comunas más visitadas (top 3 o todas si hay menos de 3)
    top_comunas = comunas_ordenadas.head(3)
    
    # Construir la descripción de las comunas principales
    if len(top_comunas) > 0:
        principal = top_comunas.iloc[0]
        porcentaje_principal = round((principal["Cantidad"] / total_comedores) * 100, 1)
        
        # Construir la lista de comunas secundarias (2da y 3ra más visitadas)
        comunas_secundarias = ""
        if len(top_comunas) > 1:
            secundarias = top_comunas.iloc[1:]
            
            lista_secundarias = []
            for i, comuna in secundarias.iterrows():
                porcentaje = round((comuna["Cantidad"] / total_comedores) * 100, 1)
                lista_secundarias.append(f"la Comuna {comuna['Comuna']} con {comuna['Cantidad']} comedores ({porcentaje}%)")
            
            if len(lista_secundarias) == 1:
                comunas_secundarias = f"seguida de {lista_secundarias[0]}"
            else:
                comunas_secundarias = f"seguida de {', '.join(lista_secundarias[:-1])} y {lista_secundarias[-1]}"
    
    # Construir el análisis completo
    analisis = f"""
    <div class="analysis-container">
        <div class="analysis-title">Análisis Descriptivo de Comunas</div>
        <div class="analysis-text">
            <p>En este trabajo de investigación sobre el clima organizacional en comedores comunitarios, 
            se visitaron un total de <span class="highlight-stat">{total_comedores}</span> comedores distribuidos 
            en <span class="highlight-stat">{total_comunas}</span> comunas diferentes.</p>
            
            <p>La comuna que concentra el mayor número de comedores es la <b>Comuna {principal['Comuna']}</b>, 
            donde se visitaron <span class="highlight-stat">{principal['Cantidad']}</span> comedores, 
            representando el <span class="highlight-stat">{porcentaje_principal}%</span> del total de la muestra, 
            {comunas_secundarias}.</p>
    """
    
    # Analizar concentración geográfica
    top3_cantidad = top_comunas["Cantidad"].sum()
    porcentaje_top3 = round((top3_cantidad / total_comedores) * 100, 1)
    
    if porcentaje_top3 > 70:
        concentracion = "alta"
        color = "#b91c1c"  # Rojo
    elif porcentaje_top3 > 50:
        concentracion = "moderada"
        color = "#d97706"  # Naranja
    else:
        concentracion = "baja"
        color = "#15803d"  # Verde
    
    analisis += f"""
            <p>Las {len(top_comunas)} comunas principales concentran el 
            <span class="highlight-stat">{porcentaje_top3}%</span> de todos los comedores evaluados, 
            lo que indica una <b style="color: {color};">{concentracion}</b> concentración geográfica 
            en el estudio realizado.</p>
    """
    
    # Añadir información sobre la comuna menos representada
    if len(comunas_ordenadas) > 3:
        menor = comunas_ordenadas.iloc[-1]
        porcentaje_menor = round((menor["Cantidad"] / total_comedores) * 100, 1)
        
        analisis += f"""
            <p>Por otro lado, la <b>Comuna {menor['Comuna']}</b> es la que presenta menor participación 
            en el estudio con <b>{menor['Cantidad']}</b> comedores, representando apenas el 
            <span class="highlight-stat">{porcentaje_menor}%</span> del total.</p>
        """
    
    analisis += """
        </div>
    </div>
    """
    
    return analisis

def generar_analisis_descriptivo_nodo(nodos_df):
    """
    Genera un análisis descriptivo textual de la distribución por nodo.
    
    Args:
        nodos_df: DataFrame con la distribución de comedores por nodo (debe tener columnas 'Nodo' y 'Cantidad')
        
    Returns:
        str: Texto HTML con el análisis descriptivo
    """
    if nodos_df.empty:
        return "<p>No hay datos suficientes para analizar la distribución por nodo.</p>"
    
    # Ordenar nodos por cantidad (de mayor a menor)
    nodos_ordenados = nodos_df.sort_values("Cantidad", ascending=False)
    
    # Obtener número total de comedores y nodos
    total_comedores = nodos_ordenados["Cantidad"].sum()
    total_nodos = len(nodos_ordenados)
    
    # Obtener los nodos principales (todos, ordenados por cantidad)
    principal = nodos_ordenados.iloc[0]
    porcentaje_principal = round((principal["Cantidad"] / total_comedores) * 100, 1)
    
    # Obtener el nodo menos representado
    menor = nodos_ordenados.iloc[-1]
    porcentaje_menor = round((menor["Cantidad"] / total_comedores) * 100, 1)
    
    # Calcular diferencia entre el mayor y menor
    diferencia = principal["Cantidad"] - menor["Cantidad"]
    
    # Construir descripción de nodos secundarios
    nodos_secundarios = ""
    if len(nodos_ordenados) > 1:
        secundarios = nodos_ordenados.iloc[1:min(3, len(nodos_ordenados))]
        
        lista_secundarios = []
        for i, nodo in secundarios.iterrows():
            porcentaje = round((nodo["Cantidad"] / total_comedores) * 100, 1)
            lista_secundarios.append(f"el Nodo {nodo['Nodo']} con {nodo['Cantidad']} comedores ({porcentaje}%)")
        
        if len(lista_secundarios) == 1:
            nodos_secundarios = f"seguido de {lista_secundarios[0]}"
        else:
            nodos_secundarios = f"seguido de {', '.join(lista_secundarios[:-1])} y {lista_secundarios[-1]}"
    
    # Construir el análisis completo
    analisis = f"""
    <div class="analysis-container">
        <div class="analysis-title">Análisis Descriptivo de Nodos</div>
        <div class="analysis-text">
            <p>En cuanto a la distribución por nodos organizativos, los <span class="highlight-stat">{total_comedores}</span> 
            comedores visitados se distribuyen en <span class="highlight-stat">{total_nodos}</span> nodos diferentes.</p>
            
            <p>El <b>Nodo {principal['Nodo']}</b> concentra la mayor cantidad de comedores con 
            <span class="highlight-stat">{principal['Cantidad']}</span> comedores, representando el 
            <span class="highlight-stat">{porcentaje_principal}%</span> del total, {nodos_secundarios}.</p>
    """
    
    # Analizar distribución y concentración
    top3_cantidad = nodos_ordenados.head(min(3, len(nodos_ordenados)))["Cantidad"].sum()
    porcentaje_top3 = round((top3_cantidad / total_comedores) * 100, 1)
    
    if porcentaje_top3 > 80:
        concentracion = "muy alta"
        color = "#7f1d1d"  # Rojo oscuro
    elif porcentaje_top3 > 60:
        concentracion = "alta"
        color = "#b91c1c"  # Rojo
    else:
        concentracion = "moderada"
        color = "#d97706"  # Naranja
    
    analisis += f"""
            <p>Los {min(3, len(nodos_ordenados))} nodos principales agrupan el 
            <span class="highlight-stat">{porcentaje_top3}%</span> de todos los comedores evaluados, 
            lo que muestra una <b style="color: {color};">{concentracion}</b> concentración organizativa 
            en la distribución por nodos.</p>
            
            <p>La diferencia entre el nodo con mayor número de comedores (Nodo {principal['Nodo']} con {principal['Cantidad']} comedores) 
            y el nodo con menor presencia (Nodo {menor['Nodo']} con {menor['Cantidad']} comedores) 
            es de <span class="highlight-stat">{diferencia}</span> comedores.</p>
    """
    
    # Añadir interpretación sobre la equidad en la distribución
    if diferencia > principal["Cantidad"] * 0.5:
        equidad = "desbalanceada"
        recomendacion = "sugiriendo la necesidad de equilibrar la cobertura entre nodos en futuros estudios"
    else:
        equidad = "relativamente equilibrada"
        recomendacion = "lo que permite una visión representativa de los diferentes nodos organizativos"
    
    analisis += f"""
            <p>Esta distribución muestra una estructura <b>{equidad}</b> entre los distintos nodos, 
            {recomendacion}.</p>
        </div>
    </div>
    """
    
    return analisis

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
        # Análisis descriptivo sobre distribución por comuna
        if "descriptivo" in resultados and "distribucion_comunas" in resultados["descriptivo"]:
            comunas_df = resultados["descriptivo"]["distribucion_comunas"]
            analisis_comunas = generar_analisis_descriptivo_comuna(comunas_df)
            st.markdown(analisis_comunas, unsafe_allow_html=True)
    
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
        # Análisis descriptivo sobre distribución por nodo
        if "descriptivo" in resultados and "distribucion_nodos" in resultados["descriptivo"]:
            nodos_df = resultados["descriptivo"]["distribucion_nodos"]
            analisis_nodos = generar_analisis_descriptivo_nodo(nodos_df)
            st.markdown(analisis_nodos, unsafe_allow_html=True)

def mostrar_vista_general(resultados, figuras, show_details):
    """
    Muestra la página de vista general con métricas y distribuciones principales.
    
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
    
    # Mostrar gráficos principales
    st.subheader("Dimensiones del Clima Organizacional")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if "promedios_dimensiones" in figuras:
            st.plotly_chart(figuras["promedios_dimensiones"], use_container_width=True)
    
    with col2:
        if "radar_dimensiones" in figuras:
            st.plotly_chart(figuras["radar_dimensiones"], use_container_width=True)
    
    # Distribución demográfica
    if show_details:
        mostrar_distribucion_demografica(resultados)