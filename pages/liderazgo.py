import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px # Importar plotly express

# Importar funciones de análisis si es necesario (asumiendo que ya están disponibles)
# from analisis_dior import analisis_liderazgo_por_rol, generar_visualizaciones_liderazgo_por_rol

# --- Funciones para Mostrar Contenido ---

def mostrar_liderazgo(resultados, df):
    """
    Muestra la página de análisis comparativo de liderazgo por rol.

    Args:
        resultados: Diccionario con los resultados del análisis general
        df: DataFrame con los datos originales (puede no ser necesario si df_prep está en resultados)
    """
    st.markdown('<div class="section-header">Análisis Comparativo de Liderazgo por Rol</div>', unsafe_allow_html=True)

    st.markdown("""
    Este análisis compara las percepciones sobre liderazgo entre gestores principales y auxiliares,
    enfocándose en las siguientes preguntas:

    - **2.1 Liderazgo Respetuoso**: Evaluación del respeto en el liderazgo.
    - **2.2 Oportunidad de Proponer Ideas**: Oportunidades para proponer ideas.
    - **2.3 Espacios Adecuados Retroalimentación**: Espacios para retroalimentación.

    El objetivo es identificar si existen diferencias significativas en la percepción del liderazgo
    según el rol desempeñado en los comedores que cuentan con ambos roles registrados.
    """)

    # Verificar si los datos preparados están disponibles
    if "datos_preparados" not in resultados:
        st.error("Los datos preparados necesarios para el análisis de liderazgo no se encontraron.")
        return

    # Ejecutar análisis de liderazgo por rol (asumiendo que las funciones están importadas o definidas)
    try:
        from analisis_dior import analisis_liderazgo_por_rol, generar_visualizaciones_liderazgo_por_rol
        with st.spinner("Analizando datos de liderazgo por rol..."):
            # Usar los datos preparados que ya están en el diccionario 'resultados'
            resultados_liderazgo = analisis_liderazgo_por_rol(resultados["datos_preparados"])
            figuras_liderazgo = generar_visualizaciones_liderazgo_por_rol(resultados_liderazgo)

    except ImportError:
        st.error("No se pudieron importar las funciones de análisis de liderazgo desde 'analisis_dior.py'.")
        return
    except Exception as e:
        st.error(f"Ocurrió un error durante el análisis de liderazgo: {e}")
        return

    # Mostrar resultados si no hubo errores
    if "error" in resultados_liderazgo:
        st.error(f"Error en el análisis de liderazgo: {resultados_liderazgo['error']}")
    else:
        mostrar_metricas_liderazgo(resultados_liderazgo)
        mostrar_visualizaciones_liderazgo(resultados_liderazgo, figuras_liderazgo) # Aquí se añadirá el resumen
        mostrar_detalle_por_comedor(resultados_liderazgo) # Mostrar exploración detallada

def mostrar_metricas_liderazgo(resultados_liderazgo):
    """
    Muestra las métricas generales del análisis de liderazgo.

    Args:
        resultados_liderazgo: Diccionario con los resultados del análisis de liderazgo
    """
    st.subheader("Disponibilidad de Datos por Rol")

    col1, col2, col3, col4 = st.columns(4)

    # Usar .get con valor por defecto 0 por si alguna clave no existe
    total_comedores = resultados_liderazgo.get("total_comedores", 0)
    con_principal = resultados_liderazgo.get("comedores_con_principal", 0)
    con_auxiliar = resultados_liderazgo.get("comedores_con_auxiliar", 0)
    con_ambos = resultados_liderazgo.get("comedores_con_ambos_roles", 0)

    with col1:
        st.metric("Total Comedores", total_comedores)
    with col2:
        st.metric("Con Gestor Principal", con_principal)
    with col3:
        st.metric("Con Gestor Auxiliar", con_auxiliar)
    with col4:
        # Calcular delta solo si total_comedores > 0
        delta_perc = f"{(con_ambos / total_comedores * 100):.1f}%" if total_comedores > 0 else "0.0%"
        st.metric("Con Ambos Roles", con_ambos, delta=delta_perc, help="Porcentaje del total de comedores.")

def mostrar_visualizaciones_liderazgo(resultados_liderazgo, figuras_liderazgo):
    """
    Muestra las visualizaciones del análisis de liderazgo y el resumen de intervención.

    Args:
        resultados_liderazgo: Diccionario con los resultados del análisis
        figuras_liderazgo: Diccionario con las figuras del análisis de liderazgo
    """
    st.subheader("Comparación Global de Percepción por Rol")

    # Gráfico de comparación global
    if "comparacion_global" in figuras_liderazgo:
        st.plotly_chart(figuras_liderazgo["comparacion_global"], use_container_width=True)
    else:
        st.info("Gráfico de comparación global no disponible.")

    st.markdown("---")

    # Sección de Concordancia
    st.subheader("Concordancia entre Roles")
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de distribución de concordancia
        if "distribucion_concordancia" in figuras_liderazgo:
            st.plotly_chart(figuras_liderazgo["distribucion_concordancia"], use_container_width=True)
        else:
            st.info("Gráfico de distribución de concordancia no disponible.")

    with col2:
        # Explicación de los niveles de concordancia
        mostrar_explicacion_concordancia(resultados_liderazgo)

    # --- NUEVO: Resumen de Comedores para Intervención ---
    if "analisis_comedores" in resultados_liderazgo:
        comedores_baja_concordancia = [
            comedor for comedor, datos in resultados_liderazgo["analisis_comedores"].items()
            if datos.get("concordancia_global") == "Baja"
        ]

        if comedores_baja_concordancia:
            st.warning("⚠️ Comedores con Baja Concordancia (Potencial Intervención):")
            st.markdown(f"""
            Se identificaron **{len(comedores_baja_concordancia)}** comedores donde existen diferencias significativas
            (baja concordancia) entre la percepción del liderazgo del gestor/a principal y el/la auxiliar.
            Estos comedores podrían requerir atención o diálogo para alinear perspectivas:
            """)
            # Mostrar lista con viñetas
            for comedor in comedores_baja_concordancia:
                st.markdown(f"- {comedor}")
        else:
            st.success("✅ No se encontraron comedores con baja concordancia general entre roles.")

    st.markdown("---")

    # Comedores con Mayor Diferencia
    st.subheader("Comedores con Mayor Diferencia de Percepción (Top 10)")
    if "top_comedores_diferencia" in figuras_liderazgo:
        st.plotly_chart(figuras_liderazgo["top_comedores_diferencia"], use_container_width=True)
        st.caption("El gráfico muestra los 10 comedores con la mayor diferencia promedio absoluta en las 3 preguntas de liderazgo entre roles.")
    else:
        st.info("Gráfico de comedores con mayor diferencia no disponible.")


def mostrar_explicacion_concordancia(resultados_liderazgo):
    """
    Muestra la explicación de los niveles de concordancia usando componentes Streamlit.

    Args:
        resultados_liderazgo: Diccionario con los resultados del análisis de liderazgo
    """
    if "resumen_concordancia" in resultados_liderazgo:
        resumen = resultados_liderazgo["resumen_concordancia"]
        # Sumar los valores del resumen para obtener el total de comedores con ambos roles analizados
        comedores_con_ambos_roles = sum(resumen.values())

        if comedores_con_ambos_roles > 0: # Mostrar solo si hay comedores para analizar
            with st.container(border=True): # Usar contenedor con borde
                st.markdown("##### ¿Qué significa la Concordancia?")
                st.markdown("""
                Mide qué tan similares son las percepciones entre gestores principales y auxiliares en las preguntas de liderazgo. Se calcula sobre los comedores que tienen *ambos* roles registrados.
                - **Alta**: Diferencia promedio ≤ 0.5 puntos.
                - **Media**: Diferencia promedio > 0.5 y ≤ 1 punto.
                - **Baja**: Diferencia promedio > 1 punto.
                """)
                st.markdown(f"##### Resumen ({comedores_con_ambos_roles} comedores con ambos roles):")
                # Usar formato de lista o métricas pequeñas
                st.markdown(f"- **Alta Concordancia:** {resumen.get('Alta', 0)} comedores")
                st.markdown(f"- **Media Concordancia:** {resumen.get('Media', 0)} comedores")
                st.markdown(f"- **Baja Concordancia:** {resumen.get('Baja', 0)} comedores")
        else:
            st.info("No hay suficientes datos (comedores con ambos roles) para calcular la concordancia.")
    else:
        st.info("Resumen de concordancia no disponible.")


def mostrar_detalle_por_comedor(resultados_liderazgo):
    """
    Muestra la exploración detallada por comedor.

    Args:
        resultados_liderazgo: Diccionario con los resultados del análisis de liderazgo
    """
    st.markdown("---")
    st.subheader("Exploración Detallada por Comedor")

    if "analisis_comedores" in resultados_liderazgo and resultados_liderazgo["analisis_comedores"]:
        comedores_analizados = list(resultados_liderazgo["analisis_comedores"].keys())

        if not comedores_analizados:
            st.info("No hay comedores con ambos roles registrados para mostrar detalles.")
            return

        # Ordenar alfabéticamente para el selector
        comedores_analizados.sort()

        comedor_seleccionado = st.selectbox(
            "Selecciona un comedor para ver detalles:",
            comedores_analizados,
            index=0, # Seleccionar el primero por defecto
            key="select_comedor_liderazgo"
        )

        if comedor_seleccionado and comedor_seleccionado in resultados_liderazgo["analisis_comedores"]:
            datos_comedor = resultados_liderazgo["analisis_comedores"][comedor_seleccionado]

            # Mostrar concordancia global y diferencia promedio
            nivel_conc = datos_comedor.get("concordancia_global", "N/A")
            dif_prom = datos_comedor.get("diferencia_promedio", float('nan')) # Usar nan si no existe

            # Asignar color según concordancia
            color_conc = "green" if nivel_conc == "Alta" else "orange" if nivel_conc == "Media" else "red" if nivel_conc == "Baja" else "grey"

            st.markdown(f"""
            <div style="background-color:#f8f9fa; padding:10px; border-radius:5px; margin-bottom:15px; border-left: 5px solid {color_conc};">
                Concordancia global: <strong style="color:{color_conc};">{nivel_conc}</strong>
                (Diferencia promedio: {dif_prom:.2f} puntos)
            </div>
            """, unsafe_allow_html=True)

            # Crear tabla de detalles por pregunta
            detalles = []
            if "analisis_preguntas" in datos_comedor:
                for pregunta, datos_pregunta in datos_comedor["analisis_preguntas"].items():
                    # Nombre más legible de la pregunta
                    nombre_legible = pregunta.replace("_", " ").replace("2.", "").replace("1 ", "1. ").strip() # Limpiar nombre
                    if pregunta == "2.1_LIDERAZGO_RESPESTUOSO": nombre_legible = "Liderazgo Respetuoso"
                    elif pregunta == "2.2_OPORTUNIDAD_DE_PROPONER_IDEAS": nombre_legible = "Oportunidad de Proponer Ideas"
                    elif pregunta == "2.3_ESPACIOS_ADECUADOS_RETROALIMENTACION": nombre_legible = "Espacios para Retroalimentación"

                    # Manejar posibles NaN o None
                    prom_princ = datos_pregunta.get('promedio_principal', float('nan'))
                    prom_aux = datos_pregunta.get('promedio_auxiliar', float('nan'))
                    dif = datos_pregunta.get('diferencia', float('nan'))
                    conc_preg = datos_pregunta.get("concordancia", "N/A")

                    detalles.append({
                        "Pregunta": nombre_legible,
                        "Principal": f"{prom_princ:.2f}",
                        "Auxiliar": f"{prom_aux:.2f}",
                        "Diferencia": f"{dif:.2f}",
                        "Concordancia Pregunta": conc_preg
                    })

            if detalles:
                df_detalles = pd.DataFrame(detalles)
                st.dataframe(
                    df_detalles,
                    column_config={
                        "Pregunta": st.column_config.TextColumn("Pregunta de Liderazgo"),
                        "Principal": st.column_config.NumberColumn("Prom. Principal", format="%.2f"),
                        "Auxiliar": st.column_config.NumberColumn("Prom. Auxiliar", format="%.2f"),
                        "Diferencia": st.column_config.NumberColumn("Diferencia (P-A)", format="%.2f"),
                        "Concordancia Pregunta": st.column_config.TextColumn(
                            "Concordancia",
                            help="Nivel de concordancia para esta pregunta específica."
                        )
                    },
                    use_container_width=True,
                    hide_index=True
                )

                # Crear gráfico de radar para el comedor seleccionado
                crear_radar_comedor(detalles, comedor_seleccionado)
            else:
                st.warning("No se encontraron detalles de preguntas para este comedor.")

    else:
        st.info("No hay análisis detallado por comedor disponible (requiere comedores con ambos roles).")


def crear_radar_comedor(detalles, comedor_seleccionado):
    """
    Crea un gráfico de radar para comparar las percepciones en el comedor seleccionado.

    Args:
        detalles: Lista de diccionarios con los detalles por pregunta del comedor
        comedor_seleccionado: Nombre del comedor seleccionado
    """
    if not detalles: # No crear gráfico si no hay detalles
        return

    # Datos para el radar
    preguntas_radar = [d["Pregunta"] for d in detalles]
    # Convertir a float, manejando posibles errores o strings 'nan'
    try:
        valores_principal = [float(d["Principal"]) for d in detalles]
        valores_auxiliar = [float(d["Auxiliar"]) for d in detalles]
    except ValueError:
        st.error("Error al convertir valores para el gráfico radar. Verifique los datos.")
        return

    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(
        r=valores_principal,
        theta=preguntas_radar,
        fill='toself',
        name='Gestor Principal',
        line_color='#1f77b4' # Azul
    ))

    fig_radar.add_trace(go.Scatterpolar(
        r=valores_auxiliar,
        theta=preguntas_radar,
        fill='toself',
        name='Gestor Auxiliar',
        line_color='#ff7f0e' # Naranja
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 3] # Escala de 1 a 3
            )
        ),
        title=f"Comparación de Percepciones en {comedor_seleccionado}",
        showlegend=True,
        height=400, # Ajustar altura
        margin=dict(l=40, r=40, t=80, b=40) # Ajustar márgenes
    )

    st.plotly_chart(fig_radar, use_container_width=True)


# --- Punto de entrada para ejecución directa (si se corre este archivo solo) ---
if __name__ == "__main__":
    # Simular datos de sesión si no existen (para pruebas)
    if "resultados_actuales" not in st.session_state:
         # Crear datos simulados mínimos para que las funciones no fallen
         st.session_state["resultados_actuales"] = {
             "datos_preparados": pd.DataFrame({ # Simular df_prep
                 "NOMBRE_COMEDOR": ["Comedor A", "Comedor A", "Comedor B", "Comedor B", "Comedor C"],
                 "ROL": ["GESTORA/OR PRINCIPAL", "GESTORA/OR  AUXILIAR", "GESTORA/OR PRINCIPAL", "GESTORA/OR  AUXILIAR", "GESTORA/OR PRINCIPAL"],
                 "2.1_LIDERAZGO_RESPESTUOSO": [3, 1, 2, 2, 3],
                 "2.2_OPORTUNIDAD_DE_PROPONER_IDEAS": [2, 2, 3, 1, 2],
                 "2.3_ESPACIOS_ADECUADOS_RETROALIMENTACION": [1, 3, 2, 2, 1]
             })
         }
    if "df" not in st.session_state: # Simular df original si es necesario
        st.session_state["df"] = st.session_state["resultados_actuales"]["datos_preparados"]

    # Llamar a la función principal de esta página
    mostrar_liderazgo(st.session_state["resultados_actuales"], st.session_state["df"])

