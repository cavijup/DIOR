import streamlit as st
import pandas as pd
import plotly.express as px

# Importar las constantes necesarias
from analisis_dior import MAPEO_RESPUESTAS

def mostrar_dimensiones(resultados, figuras):
    """
    Muestra la página de análisis por dimensiones del clima organizacional.
    
    Args:
        resultados: Diccionario con los resultados del análisis
        figuras: Diccionario con las figuras generadas
    """
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
            
            mostrar_detalle_por_pregunta(resultados, promedio_preguntas, dimension_seleccionada)

def mostrar_detalle_por_pregunta(resultados, promedio_preguntas, dimension_seleccionada):
    """
    Muestra detalles de los comedores por pregunta específica.
    
    Args:
        resultados: Diccionario con los resultados de análisis
        promedio_preguntas: Diccionario con promedios por pregunta
        dimension_seleccionada: Dimensión seleccionada para análisis
    """
    # --- INICIO: Código para mostrar comedores por pregunta ---
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

        # Acceder a df_prep desde el diccionario 'resultados'
        df_preparado = resultados.get("datos_preparados")

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

    # --- FIN: Código para mostrar comedores por pregunta ---