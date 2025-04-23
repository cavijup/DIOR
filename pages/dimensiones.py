import streamlit as st
import pandas as pd
import plotly.express as px

# Importar las constantes necesarias y funciones auxiliares si es necesario
# Asumiendo que MAPEO_RESPUESTAS está definido en analisis_dior.py o aquí
try:
    from analisis_dior import MAPEO_RESPUESTAS
except ImportError:
    # Definir localmente si no se puede importar
    MAPEO_RESPUESTAS = {
        "DE ACUERDO": 3,
        "NI DEACUERDO, NI EN DESACUERDO": 2,
        "EN DESACUERDO": 1
    }

# Mapeo inverso para mostrar respuestas textuales
MAPEO_INVERSO = {v: k for k, v in MAPEO_RESPUESTAS.items()}

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

    # Mostrar solo el gráfico de barras para las dimensiones
    if "dimensiones" in resultados and "promedios_dimensiones" in resultados["dimensiones"]:
        promedios_df = resultados["dimensiones"]["promedios_dimensiones"]
        if not promedios_df.empty:
            # Recrear figura de barras aquí para asegurar consistencia
            fig_promedios_bar = px.bar(
                promedios_df,
                x="Dimensión",
                y="Promedio",
                color="Interpretación",
                title="Puntuación Promedio por Dimensión",
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


    # Análisis detallado por dimensión
    st.subheader("Análisis Detallado por Dimensión")

    # Selector de dimensión
    if "dimensiones" in resultados and "analisis_preguntas" in resultados["dimensiones"]:
        analisis_preguntas = resultados["dimensiones"]["analisis_preguntas"]

        # Verificar si hay dimensiones para seleccionar
        if not analisis_preguntas:
            st.warning("No hay datos de análisis por preguntas disponibles para las dimensiones.")
            return # Salir si no hay nada que mostrar

        dimension_seleccionada = st.selectbox(
            "Selecciona una dimensión para ver detalles:",
            list(analisis_preguntas.keys()),
            key="select_dimension_detalles" # Añadir clave única
        )

        if dimension_seleccionada and dimension_seleccionada in analisis_preguntas:
            preguntas = analisis_preguntas[dimension_seleccionada]

            # Mostrar promedios de las preguntas en esta dimensión
            promedio_preguntas = {pregunta: datos["promedio"] for pregunta, datos in preguntas.items() if "promedio" in datos}

            # Verificar si hay promedios para mostrar
            if promedio_preguntas:
                df_promedio = pd.DataFrame({
                    # Usar nombre original para el gráfico, el eje x lo mostrará
                    "Pregunta": list(promedio_preguntas.keys()),
                    "Promedio": list(promedio_preguntas.values())
                })

                # Crear nombres legibles para el eje x (truncados si son largos)
                nombres_legibles_eje = [p.replace("_", " ").replace(".", ". ", 1) for p in df_promedio["Pregunta"]]
                nombres_legibles_eje = [name[:30] + '...' if len(name) > 30 else name for name in nombres_legibles_eje]


                fig_prom_dim = px.bar(
                    df_promedio,
                    x="Pregunta", # Usar la columna original para datos
                    y="Promedio",
                    title=f"Promedios de Preguntas en {dimension_seleccionada}",
                    color="Promedio",
                    color_continuous_scale="YlGnBu", # Escala de color
                    text="Promedio"
                )

                fig_prom_dim.update_traces(texttemplate="%{text:.2f}", textposition="outside")
                fig_prom_dim.update_layout(
                    xaxis_title="Pregunta",
                    yaxis_title="Puntuación Promedio (1-3)",
                    yaxis=dict(range=[0, 3.2]),
                    xaxis=dict(
                        tickmode='array',
                        tickvals=df_promedio["Pregunta"], # Valores originales
                        ticktext=nombres_legibles_eje # Etiquetas legibles
                    )
                )

                st.plotly_chart(fig_prom_dim, use_container_width=True)

                # Llamar a la función para mostrar detalles por pregunta
                mostrar_detalle_por_pregunta(resultados, promedio_preguntas, dimension_seleccionada)
            else:
                st.info(f"No hay promedios de preguntas calculados para la dimensión '{dimension_seleccionada}'.")
        # else: # No es necesario un else aquí, st.selectbox maneja la selección
        #    st.info("Selecciona una dimensión para continuar.")

    else:
        st.warning("No se encontraron datos de análisis por dimensiones o preguntas.")


def mostrar_detalle_por_pregunta(resultados, promedio_preguntas, dimension_seleccionada):
    """
    Muestra detalles de los comedores por pregunta específica, filtrando por respuestas
    Neutrales o Desfavorables (1 o 2) y añade un resumen de intervención.

    Args:
        resultados: Diccionario con los resultados de análisis
        promedio_preguntas: Diccionario con promedios por pregunta (para obtener la lista de preguntas)
        dimension_seleccionada: Dimensión seleccionada para análisis
    """
    st.markdown("---") # Separador visual
    st.subheader("Explorar Comedores con Respuestas Neutrales o Desfavorables")
    st.markdown("Selecciona una pregunta para ver los comedores que respondieron 'NI DEACUERDO, NI EN DESACUERDO' o 'EN DESACUERDO'.")

    # Crear lista de preguntas para el selector (usando los nombres originales de las columnas)
    lista_preguntas_originales = list(promedio_preguntas.keys())
    # Crear nombres más legibles para el dropdown
    nombres_legibles_preguntas = [p.replace("_", " ").replace(".", ". ", 1) for p in lista_preguntas_originales]

    # Crear un mapeo de nombre legible a nombre original
    mapeo_legible_original = dict(zip(nombres_legibles_preguntas, lista_preguntas_originales))

    # Selector para la pregunta específica
    pregunta_legible_seleccionada = st.selectbox(
        "Selecciona una pregunta:",
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

            # --- MODIFICACIÓN: Filtrar solo por respuestas 1 (EN DESACUERDO) y 2 (NEUTRAL) ---
            comedores_filtrados = df_preparado[df_preparado[pregunta_seleccionada_original].isin([1, 2])]

            if not comedores_filtrados.empty:
                # Seleccionar y renombrar columnas para mostrar
                df_mostrar = comedores_filtrados[["NOMBRE_COMEDOR", pregunta_seleccionada_original]].copy()
                df_mostrar.rename(columns={
                    "NOMBRE_COMEDOR": "Nombre del Comedor",
                    pregunta_seleccionada_original: "Respuesta Numérica"
                }, inplace=True)

                # Añadir respuesta textual usando el mapeo inverso
                df_mostrar["Respuesta Textual"] = df_mostrar["Respuesta Numérica"].map(MAPEO_INVERSO)

                # Ordenar por respuesta numérica (primero los 1, luego los 2)
                df_mostrar = df_mostrar.sort_values(by="Respuesta Numérica", ascending=True)

                # Mostrar en una tabla expandible
                num_comedores_filtrados = len(df_mostrar)
                with st.expander(f"Ver los {num_comedores_filtrados} comedores con respuesta Neutral o Desfavorable a '{pregunta_legible_seleccionada}'"):
                    st.dataframe(
                        df_mostrar[["Nombre del Comedor", "Respuesta Numérica", "Respuesta Textual"]],
                        hide_index=True,
                        use_container_width=True
                    )

                # --- NUEVO: Añadir resumen de intervención ---
                st.info(f"""
                📝 **Nota de Intervención:** \n
                Los **{num_comedores_filtrados}** comedores listados arriba mostraron una percepción **Neutral** o **Desfavorable**
                respecto a la pregunta '{pregunta_legible_seleccionada}'.
                Estos podrían ser puntos focales para acciones de mejora o seguimiento en esta área específica.
                """)

            else:
                st.success(f"✅ ¡Buenas noticias! Ningún comedor respondió de forma Neutral o Desfavorable a la pregunta '{pregunta_legible_seleccionada}'.")
        else:
            st.warning("No se pudo acceder a los datos de los comedores preparados para esta pregunta.")

# Código que se ejecuta cuando este archivo se carga como página
if __name__ == "__main__":
    # Verificar si hay resultados disponibles en la sesión (para pruebas)
    if "resultados_actuales" in st.session_state and "figuras_actuales" in st.session_state:
        resultados = st.session_state["resultados_actuales"]
        figuras = st.session_state["figuras_actuales"]

        # Simular datos mínimos si no existen para evitar errores
        if "dimensiones" not in resultados:
            resultados["dimensiones"] = {"analisis_preguntas": {}}
        if not resultados["dimensiones"].get("analisis_preguntas"):
             resultados["dimensiones"]["analisis_preguntas"] = {
                 "Dimensión Ejemplo": {
                     "Pregunta_Ejemplo_1": {"promedio": 2.5, "distribucion": pd.DataFrame()},
                     "Pregunta_Ejemplo_2": {"promedio": 1.8, "distribucion": pd.DataFrame()}
                 }
             }
        if "datos_preparados" not in resultados:
             resultados["datos_preparados"] = pd.DataFrame({ # Simular df_prep
                 "NOMBRE_COMEDOR": ["Comedor A", "Comedor B", "Comedor C"],
                 "Pregunta_Ejemplo_1": [3, 2, 1],
                 "Pregunta_Ejemplo_2": [2, 1, 1]
             })
        if "promedios_dimensiones" not in resultados["dimensiones"]:
             resultados["dimensiones"]["promedios_dimensiones"] = pd.DataFrame({
                 'Dimensión': ['Dimensión Ejemplo'], 'Promedio': [2.1], 'Interpretación': ['Neutral']
             })


        # Llamar a la función principal de esta página
        mostrar_dimensiones(resultados, figuras)
    else:
        st.error("No hay datos disponibles. Por favor, carga los datos desde la página principal.")

