import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px # Importar plotly.express


def generar_analisis_descriptivo_comuna(comunas_df):
    """
    Genera un análisis descriptivo textual de la distribución por comuna. (Versión HTML Corregida v2)
    Corrige la construcción de cadenas HTML para asegurar validez.

    Args:
        comunas_df: DataFrame con la distribución de comedores por comuna (debe tener columnas 'Comuna' y 'Cantidad')

    Returns:
        str: Texto con el análisis descriptivo en formato HTML válido
    """
    if comunas_df.empty:
        return "<p>No hay datos suficientes para analizar la distribución por comuna.</p>"

    comunas_ordenadas = comunas_df.sort_values("Cantidad", ascending=False)
    total_comedores = comunas_ordenadas["Cantidad"].sum()
    total_comunas = len(comunas_ordenadas)
    top_comunas = comunas_ordenadas.head(3)

    # Usar una lista para construir el HTML y luego unir
    html_parts = [
        # Se asume que las clases CSS están definidas globalmente si se usan
        '<div class="analysis-container">',
        '<div class="analysis-title">Análisis Descriptivo de Comunas</div>',
        '<div class="analysis-text">',
        f'<p>En este trabajo de investigación sobre el clima organizacional en comedores comunitarios, se visitaron un total de <b>{total_comedores}</b> comedores distribuidos en <b>{total_comunas}</b> comunas diferentes.</p>'
    ]

    # Construir la descripción de las comunas principales
    if len(top_comunas) > 0 and total_comedores > 0:
        principal = top_comunas.iloc[0]
        porcentaje_principal = round((principal["Cantidad"] / total_comedores) * 100, 1)
        # Construir el párrafo principal como una sola cadena continua
        texto_principal = f"<p>La comuna que concentra el mayor número de comedores es la <b>Comuna {principal['Comuna']}</b>, donde se visitaron <b>{principal['Cantidad']}</b> comedores, representando el <b>{porcentaje_principal}%</b> del total de la muestra"

        # Añadir comunas secundarias si existen
        if len(top_comunas) > 1:
            secundarias = top_comunas.iloc[1:]
            lista_secundarias = []
            for i, comuna in secundarias.iterrows():
                porcentaje = round((comuna["Cantidad"] / total_comedores) * 100, 1) if total_comedores > 0 else 0
                lista_secundarias.append(f"la Comuna {comuna['Comuna']} con <b>{comuna['Cantidad']}</b> comedores ({porcentaje}%)")

            # Formatear la lista de secundarias
            if len(lista_secundarias) == 1:
                texto_principal += f", seguida de {lista_secundarias[0]}." # Punto final antes de cerrar P
            elif len(lista_secundarias) > 1:
                 secundarias_texto = ", ".join(lista_secundarias[:-1]) + " y " + lista_secundarias[-1]
                 texto_principal += f", seguida de {secundarias_texto}." # Punto final antes de cerrar P
            # Cerrar la etiqueta P después de añadir secundarias o el punto final
            texto_principal += "</p>"
        else:
            # Si no hay secundarias, añadir punto final y cerrar P
            texto_principal += ".</p>"
        # Añadir el párrafo completo a la lista de partes HTML
        html_parts.append(texto_principal)

    # Analizar concentración geográfica
    if total_comedores > 0:
        top3_cantidad = top_comunas["Cantidad"].sum()
        porcentaje_top3 = round((top3_cantidad / total_comedores) * 100, 1)

        # Determinar nivel de concentración y color
        if porcentaje_top3 > 70:
            concentracion = "alta"; color = "#b91c1c" # Rojo
        elif porcentaje_top3 > 50:
            concentracion = "moderada"; color = "#d97706" # Naranja
        else:
            concentracion = "baja"; color = "#15803d" # Verde

        # Añadir párrafo de concentración
        html_parts.append(
            f'<p>Las {len(top_comunas)} comunas principales concentran el <b>{porcentaje_top3}%</b> de todos los comedores evaluados, lo que indica una <b style="color: {color};">{concentracion}</b> concentración geográfica en el estudio realizado.</p>'
        )

    # Añadir información sobre la comuna menos representada
    if len(comunas_ordenadas) > 3 and total_comedores > 0:
        menor = comunas_ordenadas.iloc[-1]
        porcentaje_menor = round((menor["Cantidad"] / total_comedores) * 100, 1)
        # Añadir párrafo de menor representación
        html_parts.append(
            f'<p>Por otro lado, la <b>Comuna {menor["Comuna"]}</b> es la que presenta menor participación en el estudio con <b>{menor["Cantidad"]}</b> comedores, representando apenas el <b>{porcentaje_menor}%</b> del total.</p>'
        )

    # Cerrar las etiquetas div principales
    html_parts.append('</div>') # Cierre de analysis-text
    html_parts.append('</div>') # Cierre de analysis-container

    # Unir todas las partes HTML en una sola cadena
    return "\n".join(html_parts)


def generar_analisis_descriptivo_nodo(nodos_df):
    """
    Genera un análisis descriptivo textual de la distribución por nodo. (Versión HTML Corregida v2)
    Corrige la construcción de cadenas HTML para asegurar validez.

    Args:
        nodos_df: DataFrame con la distribución de comedores por nodo (debe tener columnas 'Nodo' y 'Cantidad')

    Returns:
        str: Texto con el análisis descriptivo en formato HTML válido
    """
    if nodos_df.empty:
        return "<p>No hay datos suficientes para analizar la distribución por nodo.</p>"

    nodos_ordenados = nodos_df.sort_values("Cantidad", ascending=False)
    total_comedores = nodos_ordenados["Cantidad"].sum()
    total_nodos = len(nodos_ordenados)

    # Usar una lista para construir el HTML
    html_parts = [
        '<div class="analysis-container">',
        '<div class="analysis-title">Análisis Descriptivo de Nodos</div>',
        '<div class="analysis-text">',
        f'<p>En cuanto a la distribución por nodos organizativos, los <b>{total_comedores}</b> comedores visitados se distribuyen en <b>{total_nodos}</b> nodos diferentes.</p>'
    ]

    # Análisis si hay nodos y comedores
    if not nodos_ordenados.empty and total_comedores > 0:
        principal = nodos_ordenados.iloc[0]
        porcentaje_principal = round((principal["Cantidad"] / total_comedores) * 100, 1)
        # Construir párrafo principal como una sola cadena
        texto_principal_nodo = f"<p>El <b>Nodo {principal['Nodo']}</b> concentra la mayor cantidad de comedores con <b>{principal['Cantidad']}</b> comedores, representando el <b>{porcentaje_principal}%</b> del total"

        # Añadir nodos secundarios
        if len(nodos_ordenados) > 1:
            secundarios = nodos_ordenados.iloc[1:min(3, len(nodos_ordenados))]
            lista_secundarios = []
            for i, nodo in secundarios.iterrows():
                porcentaje = round((nodo["Cantidad"] / total_comedores) * 100, 1) if total_comedores > 0 else 0
                lista_secundarios.append(f"el Nodo {nodo['Nodo']} con <b>{nodo['Cantidad']}</b> comedores ({porcentaje}%)")

            # Formatear lista de secundarios
            if len(lista_secundarios) == 1:
                texto_principal_nodo += f", seguido de {lista_secundarios[0]}." # Punto final
            elif len(lista_secundarios) > 1:
                secundarias_texto_nodo = ", ".join(lista_secundarios[:-1]) + " y " + lista_secundarios[-1]
                texto_principal_nodo += f", seguido de {secundarias_texto_nodo}." # Punto final
            # Cerrar etiqueta P
            texto_principal_nodo += "</p>"
        else:
             # Si no hay secundarios, añadir punto final y cerrar P
            texto_principal_nodo += ".</p>"
        # Añadir párrafo a la lista
        html_parts.append(texto_principal_nodo)

        # Analizar concentración
        top_nodos = nodos_ordenados.head(min(3, len(nodos_ordenados)))
        top3_cantidad = top_nodos["Cantidad"].sum()
        porcentaje_top3 = round((top3_cantidad / total_comedores) * 100, 1)

        # Determinar nivel y color
        if porcentaje_top3 > 80:
            concentracion = "muy alta"; color = "#7f1d1d"
        elif porcentaje_top3 > 60:
            concentracion = "alta"; color = "#b91c1c"
        else:
            concentracion = "moderada"; color = "#d97706"

        # Añadir párrafo de concentración
        html_parts.append(
            f'<p>Los {len(top_nodos)} nodos principales agrupan el <b>{porcentaje_top3}%</b> de todos los comedores evaluados, lo que muestra una <b style="color: {color};">{concentracion}</b> concentración organizativa en la distribución por nodos.</p>'
        )

        # Analizar diferencia y equidad
        if len(nodos_ordenados) > 1:
            menor = nodos_ordenados.iloc[-1]
            diferencia = principal["Cantidad"] - menor["Cantidad"]
            # Añadir párrafo de diferencia
            html_parts.append(
                f"<p>La diferencia entre el nodo con mayor número de comedores (Nodo <b>{principal['Nodo']}</b> con <b>{principal['Cantidad']}</b> comedores) y el nodo con menor presencia (Nodo <b>{menor['Nodo']}</b> con <b>{menor['Cantidad']}</b> comedores) es de <b>{diferencia}</b> comedores.</p>"
            )

            # Determinar equidad
            if diferencia > principal["Cantidad"] * 0.5:
                equidad = "desbalanceada"
                recomendacion = "sugiriendo la necesidad de equilibrar la cobertura entre nodos en futuros estudios"
            else:
                equidad = "relativamente equilibrada"
                recomendacion = "lo que permite una visión representativa de los diferentes nodos organizativos"

            # Añadir párrafo de equidad
            html_parts.append(
                f'<p>Esta distribución muestra una estructura <b>{equidad}</b> entre los distintos nodos, {recomendacion}.</p>'
            )

    # Cerrar las etiquetas div principales
    html_parts.append('</div>') # Cierre de analysis-text
    html_parts.append('</div>') # Cierre de analysis-container

    # Unir todas las partes HTML
    return "\n".join(html_parts)


# --- Funciones para Mostrar Contenido en la Página ---

def mostrar_distribucion_demografica(resultados):
    """
    Muestra los detalles de distribución demográfica (comunas, nodos, etc.)
    con una presentación estética y profesional usando componentes Streamlit.

    Args:
        resultados: Diccionario con los resultados del análisis
    """
    st.markdown("## Distribución Demográfica")

    # --- Fila 1: Distribución por Comuna ---
    col1, col2 = st.columns(2)

    with col1:
        # Tabla de distribución por comuna
        if "descriptivo" in resultados and "distribucion_comunas" in resultados["descriptivo"]:
            comunas_df = resultados["descriptivo"]["distribucion_comunas"]
            if not comunas_df.empty:
                # Ordenar por cantidad (de mayor a menor)
                comunas_df = comunas_df.sort_values(by="Cantidad", ascending=False)

                # Calcular el porcentaje del total
                total_comedores_comuna = comunas_df["Cantidad"].sum()
                comunas_df["Porcentaje"] = round((comunas_df["Cantidad"] / total_comedores_comuna) * 100, 2) if total_comedores_comuna > 0 else 0

                # Crear un expander para la tabla
                with st.expander("Tabla: Distribución por Comuna", expanded=True):
                    st.dataframe(
                        comunas_df,
                        column_config={
                            "Comuna": "Comuna",
                            "Cantidad": st.column_config.NumberColumn("Cantidad", format="%d"),
                            "Porcentaje": st.column_config.NumberColumn("Porcentaje", format="%.2f%%")
                        },
                        use_container_width=True,
                        hide_index=True
                    )
            else:
                st.info("No hay datos de distribución por comuna disponibles.")

    with col2:
        # Análisis descriptivo de Comunas usando componentes Streamlit
        if "descriptivo" in resultados and "distribucion_comunas" in resultados["descriptivo"]:
            comunas_df = resultados["descriptivo"]["distribucion_comunas"]
            if not comunas_df.empty:
                # Ordenar comunas por cantidad (de mayor a menor)
                comunas_ordenadas = comunas_df.sort_values("Cantidad", ascending=False)

                # Obtener número total de comedores y comunas
                total_comedores = comunas_ordenadas["Cantidad"].sum()
                total_comunas = len(comunas_ordenadas)

                # Obtener las comunas más visitadas (top 3)
                top_comunas = comunas_ordenadas.head(3)

                with st.expander("Análisis: Distribución por Comuna", expanded=True):
                    # Métricas clave
                    cols_metricas = st.columns(3)
                    with cols_metricas[0]:
                        st.metric("Total Encuestas", total_comedores)
                    with cols_metricas[1]:
                        st.metric("Total Comunas", total_comunas)

                    # Calcular concentración para métrica
                    top3_cantidad = top_comunas["Cantidad"].sum()
                    porcentaje_top3 = round((top3_cantidad / total_comedores) * 100, 1) if total_comedores > 0 else 0
                    with cols_metricas[2]:
                        st.metric("Concentración Top 3", f"{porcentaje_top3}%")

                    st.markdown("---") # Separador

                    # Comuna principal
                    if len(top_comunas) > 0:
                        principal = top_comunas.iloc[0]
                        porcentaje_principal = round((principal["Cantidad"] / total_comedores) * 100, 1) if total_comedores > 0 else 0
                        st.markdown(f"##### Comuna Principal: **{principal['Comuna']}**")
                        st.markdown(f"📍 {principal['Cantidad']} comedores ({porcentaje_principal}% del total)")

                    # Comunas secundarias
                    if len(top_comunas) > 1:
                        st.markdown("##### Comunas Secundarias:")
                        for i, comuna in top_comunas.iloc[1:].iterrows():
                            porcentaje = round((comuna["Cantidad"] / total_comedores) * 100, 1) if total_comedores > 0 else 0
                            st.markdown(f"- Comuna **{comuna['Comuna']}**: {comuna['Cantidad']} ({porcentaje}%)")

                    # Análisis de concentración
                    st.markdown("##### Concentración Geográfica:")
                    if porcentaje_top3 > 70:
                        concentracion = "Alta"; emoji = "🔴"
                    elif porcentaje_top3 > 50:
                        concentracion = "Moderada"; emoji = "🟠"
                    else:
                        concentracion = "Baja"; emoji = "🟢"
                    st.markdown(f"{emoji} **{concentracion}**: Las {len(top_comunas)} comunas principales agrupan el **{porcentaje_top3}%** del total.")

                    # Menor representación
                    if len(comunas_ordenadas) > 3:
                        menor = comunas_ordenadas.iloc[-1]
                        porcentaje_menor = round((menor["Cantidad"] / total_comedores) * 100, 1) if total_comedores > 0 else 0
                        st.markdown("##### Menor Representación:")
                        st.markdown(f"ℹ️ Comuna **{menor['Comuna']}**: {menor['Cantidad']} comedores ({porcentaje_menor}%).")
            else:
                 st.info("No hay datos suficientes para el análisis descriptivo de comunas.")

    # --- Fila 2: Distribución por Nodo ---
    st.markdown("---")  # Separador
    col3, col4 = st.columns(2)

    with col3:
        # Gráfico de distribución por nodo
        if "descriptivo" in resultados and "distribucion_nodos" in resultados["descriptivo"]:
            nodos_df = resultados["descriptivo"]["distribucion_nodos"]
            if not nodos_df.empty:
                with st.expander("Gráfico: Distribución por Nodo", expanded=True):
                    fig_nodos = px.bar(
                        nodos_df,
                        x="Nodo",
                        y="Cantidad",
                        title="Distribución de Comedores por Nodo",
                        color="Cantidad",
                        color_continuous_scale="Blues", # Esquema de color azul
                        text_auto=True
                    )
                    fig_nodos.update_layout(
                        xaxis_title="Nodo",
                        yaxis_title="Número de Comedores",
                        xaxis={'categoryorder':'total descending'}, # Ordenar barras
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig_nodos, use_container_width=True)
            else:
                st.info("No hay datos de distribución por nodo disponibles.")

    with col4:
        # Análisis descriptivo de Nodos usando componentes Streamlit
        if "descriptivo" in resultados and "distribucion_nodos" in resultados["descriptivo"]:
            nodos_df = resultados["descriptivo"]["distribucion_nodos"]
            if not nodos_df.empty:
                # Ordenar nodos por cantidad
                nodos_ordenados = nodos_df.sort_values("Cantidad", ascending=False)
                total_comedores_nodo = nodos_ordenados["Cantidad"].sum()
                total_nodos = len(nodos_ordenados)

                with st.expander("Análisis: Distribución por Nodo", expanded=True):
                    # Métricas clave
                    cols_metricas_nodo = st.columns(3)
                    with cols_metricas_nodo[0]:
                        st.metric("Total Nodos", total_nodos)

                    if len(nodos_ordenados) > 0:
                        principal_nodo = nodos_ordenados.iloc[0]
                        porcentaje_principal_nodo = round((principal_nodo["Cantidad"] / total_comedores_nodo) * 100, 1) if total_comedores_nodo > 0 else 0

                        with cols_metricas_nodo[1]:
                            st.metric("Nodo Principal", f"Nodo {principal_nodo['Nodo']}")

                        # Concentración Top 3 Nodos
                        top_nodos = nodos_ordenados.head(min(3, len(nodos_ordenados)))
                        top_cantidad_nodo = top_nodos["Cantidad"].sum()
                        porcentaje_top_nodo = round((top_cantidad_nodo / total_comedores_nodo) * 100, 1) if total_comedores_nodo > 0 else 0
                        with cols_metricas_nodo[2]:
                            st.metric("Concentración Top 3", f"{porcentaje_top_nodo}%")

                        st.markdown("---") # Separador

                        # Nodo principal
                        st.markdown(f"##### Nodo Principal: **{principal_nodo['Nodo']}**")
                        st.markdown(f"🔗 {principal_nodo['Cantidad']} comedores ({porcentaje_principal_nodo}% del total)")

                        # Nodos secundarios
                        if len(nodos_ordenados) > 1:
                            st.markdown("##### Nodos Secundarios:")
                            for i, nodo in nodos_ordenados.iloc[1:min(3, len(nodos_ordenados))].iterrows():
                                porcentaje_nodo = round((nodo["Cantidad"] / total_comedores_nodo) * 100, 1) if total_comedores_nodo > 0 else 0
                                st.markdown(f"- Nodo **{nodo['Nodo']}**: {nodo['Cantidad']} ({porcentaje_nodo}%)")

                        # Análisis de concentración
                        st.markdown("##### Concentración Organizativa:")
                        if porcentaje_top_nodo > 80:
                            concentracion_nodo = "Muy alta"; emoji_nodo = "🔴"
                        elif porcentaje_top_nodo > 60:
                            concentracion_nodo = "Alta"; emoji_nodo = "🟠"
                        else:
                            concentracion_nodo = "Moderada"; emoji_nodo = "🟡"
                        st.markdown(f"{emoji_nodo} **{concentracion_nodo}**: Los {len(top_nodos)} nodos principales agrupan el **{porcentaje_top_nodo}%** del total.")

                        # Diferencia entre nodos
                        if len(nodos_ordenados) > 1:
                            menor_nodo = nodos_ordenados.iloc[-1]
                            diferencia_nodo = principal_nodo["Cantidad"] - menor_nodo["Cantidad"]
                            st.markdown("##### Equilibrio entre Nodos:")
                            st.markdown(f"📊 **Diferencia**: {diferencia_nodo} comedores entre el mayor (Nodo {principal_nodo['Nodo']}) y el menor (Nodo {menor_nodo['Nodo']}).")

                            # Interpretación equidad
                            if diferencia_nodo > principal_nodo["Cantidad"] * 0.5:
                                equidad_nodo = "desbalanceada"; emoji_eq = "⚠️"
                                recomendacion_nodo = "sugiere necesidad de equilibrar cobertura."
                            else:
                                equidad_nodo = "relativamente equilibrada"; emoji_eq = "✓"
                                recomendacion_nodo = "permite visión representativa."
                            st.markdown(f"{emoji_eq} Distribución **{equidad_nodo}**, {recomendacion_nodo}")
            else:
                st.info("No hay datos suficientes para el análisis descriptivo de nodos.")

    # --- Sección Adicional: Análisis Textual Completo (Opcional) ---
    # Se mantiene el código pero se oculta por defecto, ya que la información
    # se presenta mejor con los componentes Streamlit anteriores.
    with st.expander("Ver análisis textual completo (Formato antiguo)", expanded=False):
        st.markdown("#### Análisis de Distribución por Comuna (Texto)")
        if "descriptivo" in resultados and "distribucion_comunas" in resultados["descriptivo"]:
            comunas_df_expander = resultados["descriptivo"]["distribucion_comunas"]
            if not comunas_df_expander.empty:
                analisis_texto_comunas = generar_analisis_descriptivo_comuna(comunas_df_expander)
                # Asegúrate de que unsafe_allow_html=True esté aquí
                st.markdown(analisis_texto_comunas, unsafe_allow_html=True)
            else:
                st.info("No hay datos de comunas para el análisis textual.")
        else:
            st.info("No disponible.")

        st.markdown("---") # Separador entre análisis

        st.markdown("#### Análisis de Distribución por Nodo (Texto)")
        if "descriptivo" in resultados and "distribucion_nodos" in resultados["descriptivo"]:
             nodos_df_expander = resultados["descriptivo"]["distribucion_nodos"]
             if not nodos_df_expander.empty:
                 analisis_texto_nodos = generar_analisis_descriptivo_nodo(nodos_df_expander)
                 # Asegúrate de que unsafe_allow_html=True esté aquí
                 st.markdown(analisis_texto_nodos, unsafe_allow_html=True)
             else:
                st.info("No hay datos de nodos para el análisis textual.")
        else:
             st.info("No disponible.")


def mostrar_vista_general(resultados, figuras, show_details):
    """
    Muestra la página de vista general con métricas y distribuciones principales.

    Args:
        resultados: Diccionario con los resultados del análisis
        figuras: Diccionario con las figuras generadas
        show_details: Booleano que indica si se deben mostrar detalles adicionales
    """
    # --- Métricas principales con formato HTML personalizado ---
    # Utiliza las clases CSS definidas en app.py
    if "descriptivo" in resultados and "total_comedores" in resultados["descriptivo"]:
        col1, col2, col3, col4 = st.columns(4)

        # Extraer valores para fácil acceso y manejar posibles ausencias
        total_comedores = resultados["descriptivo"].get("total_comedores", "N/A")
        # Calcula el total de comunas contando las filas del dataframe o usa 0 si no existe/está vacío
        total_comunas = len(resultados["descriptivo"].get("distribucion_comunas", pd.DataFrame())) if "distribucion_comunas" in resultados.get("descriptivo", {}) else "N/A"
        total_nodos = len(resultados["descriptivo"].get("distribucion_nodos", pd.DataFrame())) if "distribucion_nodos" in resultados.get("descriptivo", {}) else "N/A"
        total_nichos = len(resultados["descriptivo"].get("distribucion_nichos", pd.DataFrame())) if "distribucion_nichos" in resultados.get("descriptivo", {}) else "N/A"


        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Comedores Analizados</div>
                <div class="metric-value">{total_comedores}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
             st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Comunas</div>
                <div class="metric-value">{total_comunas}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
             st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Nodos</div>
                <div class="metric-value">{total_nodos}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
             st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Nichos</div>
                <div class="metric-value">{total_nichos}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No se pudieron cargar las métricas principales.")

    st.markdown("---") # Separador

    # --- Distribución general de respuestas ---
    st.subheader("Distribución General de Respuestas")

    col_resp1, col_resp2 = st.columns([2, 3]) # Ajustar proporción de columnas

    with col_resp1:
        # Gráfico de barras horizontales para las respuestas
        if "descriptivo" in resultados and "distribucion_respuestas" in resultados["descriptivo"]:
            dist = resultados["descriptivo"]["distribucion_respuestas"]
            if not dist.empty:
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
                    "EN DESACUERDO": "#d62728", # Rojo
                    "NI DEACUERDO, NI EN DESACUERDO": "#ffbb78", # Naranja claro
                    "DE ACUERDO": "#2ca02c" # Verde
                }

                fig_barras = go.Figure()
                for idx, row in dist_ordenada.iterrows():
                    fig_barras.add_trace(go.Bar(
                        y=[row["Respuesta"]],
                        x=[row["Cantidad"]],
                        orientation='h',
                        name=row["Respuesta"],
                        marker_color=colores.get(row["Respuesta"], "#1f77b4"),
                        text=f"{row['Porcentaje']}% ({row['Cantidad']})", # Mostrar porcentaje y cantidad
                        textposition='auto'
                    ))

                fig_barras.update_layout(
                    #title="Distribución de Respuestas", # Título redundante
                    xaxis_title="Cantidad de Respuestas",
                    yaxis_title="",
                    showlegend=False,
                    height=250, # Altura ajustada
                    margin=dict(l=10, r=10, t=30, b=20) # Margen reducido
                )
                st.plotly_chart(fig_barras, use_container_width=True)
            else:
                st.info("No hay datos de distribución de respuestas.")

    with col_resp2:
        # Análisis de texto sobre las respuestas
        if "descriptivo" in resultados and "distribucion_respuestas" in resultados["descriptivo"]:
            dist = resultados["descriptivo"]["distribucion_respuestas"]
            if not dist.empty:
                # Encontrar la respuesta más común
                respuesta_max = dist.loc[dist["Cantidad"].idxmax()]
                total_respuestas = dist["Cantidad"].sum()

                # Determinar interpretación general
                de_acuerdo = dist[dist["Respuesta"] == "DE ACUERDO"]["Porcentaje"].iloc[0] if "DE ACUERDO" in dist["Respuesta"].values else 0
                desacuerdo = dist[dist["Respuesta"] == "EN DESACUERDO"]["Porcentaje"].iloc[0] if "EN DESACUERDO" in dist["Respuesta"].values else 0

                interpretacion = ""
                color_interpretacion = ""
                emoji_interpretacion = ""

                if de_acuerdo >= 60:
                    interpretacion = "muy favorable"; color_interpretacion = "#15803d"; emoji_interpretacion="✅"
                elif de_acuerdo >= 40:
                    interpretacion = "favorable"; color_interpretacion = "#65a30d"; emoji_interpretacion="👍"
                elif desacuerdo >= 60:
                    interpretacion = "muy desfavorable"; color_interpretacion = "#b91c1c"; emoji_interpretacion="❌"
                elif desacuerdo >= 40:
                    interpretacion = "desfavorable"; color_interpretacion = "#dc2626"; emoji_interpretacion="👎"
                else:
                    interpretacion = "mixto/neutral"; color_interpretacion = "#d97706"; emoji_interpretacion="↔️"

                # Usar st.expander para el análisis textual
                with st.expander("Análisis de Respuestas", expanded=True):
                    st.markdown(f"""
                    Se analizaron **{total_respuestas}** respuestas en total.
                    La opción más seleccionada fue **"{respuesta_max['Respuesta']}"** con **{respuesta_max['Cantidad']}** respuestas
                    ({respuesta_max['Porcentaje']}% del total).
                    """)
                    st.markdown("##### Desglose por Respuesta:")
                    for idx, row in dist.iterrows():
                        st.markdown(f"- **{row['Respuesta']}**: {row['Cantidad']} ({row['Porcentaje']}%)")

                    st.markdown("##### Interpretación General:")
                    st.markdown(f"""
                    <p style="font-size: 1.1em;">{emoji_interpretacion} El clima organizacional general tiende a ser
                    <b style="color:{color_interpretacion};"> {interpretacion}</b>.</p>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay datos suficientes para el análisis de respuestas.")

    st.markdown("---") # Separador

    # --- Dimensiones del Clima Organizacional ---
    st.subheader("Dimensiones del Clima Organizacional")

    # Mostrar solo el gráfico de barras de promedios por dimensión
    if "dimensiones" in resultados and "promedios_dimensiones" in resultados["dimensiones"]:
        promedios_df = resultados["dimensiones"]["promedios_dimensiones"]
        if not promedios_df.empty:
             # Recrear figura de barras aquí para asegurar consistencia
            fig_promedios_bar = px.bar(
                promedios_df,
                x="Dimensión",
                y="Promedio",
                color="Interpretación",
                #title="Puntuación Promedio por Dimensión", # Título redundante
                color_discrete_map={
                    "Favorable": "#2ca02c",
                    "Neutral": "#ffbb78",
                    "Desfavorable": "#d62728"
                },
                text="Promedio"
            )
            fig_promedios_bar.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig_promedios_bar.update_layout(
                xaxis_title="Dimensión",
                yaxis_title="Puntuación Promedio (1-3)",
                yaxis=dict(range=[0, 3.2]),
                legend_title="Interpretación"
            )
            st.plotly_chart(fig_promedios_bar, use_container_width=True)
        else:
            st.info("No hay datos de promedios por dimensión.")
    else:
        st.warning("Resultados de análisis por dimensiones no encontrados.")


    # --- Distribución demográfica (si show_details es True) ---
    if show_details:
        mostrar_distribucion_demografica(resultados)
    else:
        st.info("Active 'Mostrar detalles avanzados' en la barra lateral para ver la distribución demográfica.")

# --- Punto de entrada para ejecución directa (si se corre este archivo solo) ---
if __name__ == "__main__":
    # Simular datos de sesión si no existen (para pruebas)
    if "resultados_actuales" not in st.session_state:
        st.session_state["resultados_actuales"] = {"descriptivo": {}, "dimensiones": {}} # Datos mínimos
    if "figuras_actuales" not in st.session_state:
        st.session_state["figuras_actuales"] = {}
    if "show_details" not in st.session_state:
        st.session_state["show_details"] = True

    # Cargar estilos (necesario si se ejecuta solo)
    st.markdown("""
    <style>
    .metric-card { background-color: #E0F2FE; border-radius: 8px; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; margin-bottom: 10px; height: 100px; display: flex; flex-direction: column; justify-content: center; border: 1px solid #BFDBFE; }
    .metric-label { font-size: 0.9em; color: #4B5563; margin-bottom: 5px; font-weight: 500; }
    .metric-value { font-size: 1.8em; font-weight: bold; color: #1E3A8A; line-height: 1.2; }
    </style>
    """, unsafe_allow_html=True)

    # Llamar a la función principal de esta página
    mostrar_vista_general(
        st.session_state["resultados_actuales"],
        st.session_state["figuras_actuales"],
        st.session_state["show_details"]
    )
