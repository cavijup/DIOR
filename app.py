"""
Aplicación principal para el Análisis de Clima Organizacional en Comedores Comunitarios.

Este script es el punto de entrada principal de la aplicación Streamlit.
Gestiona la carga de datos, la configuración de la interfaz de usuario,
la navegación entre las diferentes páginas de análisis y la generación de reportes.

Autor: Equipo de DIOR Analytics
Versión: 1.4 (Añadido título principal y descarga HTML)
"""

import streamlit as st
import traceback
import os
import pandas as pd # Importar pandas
from datetime import datetime # Para la fecha en el nombre del archivo

# Configuración de la página
st.set_page_config(
    page_title="Análisis DIOR",
    page_icon="📊",
    layout="wide"
)

# Importar la función para cargar datos
from google_connection import load_data

# Importar las funciones de análisis
# Asegúrate de que estas funciones existan y sean importables
try:
    from analisis_dior import ejecutar_analisis_completo, generar_visualizaciones, analisis_liderazgo_por_rol, interpretar_promedio
except ImportError as e:
    st.error(f"Error al importar funciones de análisis: {e}. Asegúrate de que 'analisis_dior.py' esté en el mismo directorio.")
    st.stop() # Detener si las funciones de análisis no se pueden importar

# Estilos CSS personalizados
def cargar_estilos_css():
    """Carga los estilos CSS globales para la aplicación."""
    st.markdown("""
    <style>
    /* Estilos existentes */
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A8A; /* Azul oscuro */
        margin-bottom: 1.5rem;
        background-color: #4ade80;  /* Color verde */
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2563EB; /* Azul */
        margin-bottom: 1rem;
        text-align: center;
    }
    .metric-card {
        background-color: #E0F2FE; /* Azul claro */
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 10px;
        height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid #BFDBFE;
    }
    .metric-label {
        font-size: 0.9em;
        color: #4B5563;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .metric-value {
        font-size: 1.8em;
        font-weight: bold;
        color: #1E3A8A;
        line-height: 1.2;
    }
    /* Estilo para el botón de descarga */
    .stDownloadButton>button {
        width: 100%;
        background-color: #1D4ED8; /* Azul más oscuro */
        color: white;
        border-radius: 5px;
        padding: 10px 0;
        margin-top: 15px;
    }
    .stDownloadButton>button:hover {
        background-color: #1E3A8A; /* Azul aún más oscuro */
        color: white;
        border: 1px solid #1E3A8A;
    }
    /* Estilo para la descripción principal */
    .main-description {
        margin-bottom: 2rem;
        padding: 1rem;
        background-color: #f8f9fa; /* Fondo gris muy claro */
        border-left: 5px solid #2563EB; /* Borde izquierdo azul */
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Función para Generar Reporte HTML ---
def generar_reporte_html(resultados, resultados_liderazgo):
    """
    Genera una cadena HTML con el resumen de los análisis.

    Args:
        resultados: Diccionario con los resultados del análisis principal.
        resultados_liderazgo: Diccionario con los resultados del análisis de liderazgo.

    Returns:
        str: Cadena de texto con el contenido HTML del reporte.
    """
    # Inicializar lista para partes HTML
    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="es">',
        "<head>",
        '  <meta charset="UTF-8">',
        "  <title>Resumen Análisis DIOR</title>",
        "  <style>",
        "    body { font-family: sans-serif; line-height: 1.6; padding: 25px; color: #333; }",
        "    h1, h2, h3 { color: #1E3A8A; border-bottom: 1px solid #ccc; padding-bottom: 5px; }",
        "    h1 { font-size: 1.8em; }",
        "    h2 { font-size: 1.5em; margin-top: 30px; }",
        "    h3 { font-size: 1.2em; margin-top: 20px; }",
        "    table { border-collapse: collapse; width: 90%; margin: 15px auto; }",
        "    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }",
        "    th { background-color: #E0F2FE; color: #1E3A8A; font-weight: bold; }",
        "    .section { margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px dashed #eee; }", # Separador entre secciones
        "    .metric-summary p, .summary-text p, .dimension-summary p, .liderazgo-summary p { margin: 8px 0; }",
        "    ul { padding-left: 20px; }",
        "    li { margin-bottom: 5px; }",
        "    .warning { color: #D97706; font-weight: bold; }",
        "    .success { color: #15803D; font-weight: bold; }",
        "    .interpretation-favorable { color: #15803D; }",
        "    .interpretation-neutral { color: #D97706; }",
        "    .interpretation-desfavorable { color: #B91C1C; }",
        "    .timestamp { font-size: 0.8em; color: #888; text-align: right; margin-top: 40px; }",
        "  </style>",
        "</head>",
        "<body>",
        f"<h1>Resumen Análisis Clima Organizacional DIOR</h1>"
        # Timestamp se mueve al final
    ]

    # --- Sección 1: Vista General ---
    html_parts.append('<div class="section"><h2>Vista General</h2>')
    if resultados and "descriptivo" in resultados:
        desc = resultados["descriptivo"]
        html_parts.append('<div class="metric-summary"><h3>Métricas Principales</h3>')
        html_parts.append(f"<p><b>Total Comedores Analizados:</b> {desc.get('total_comedores', 'N/A')}</p>")
        total_comunas = len(desc.get("distribucion_comunas", pd.DataFrame())) if isinstance(desc.get("distribucion_comunas"), pd.DataFrame) else "N/A"
        total_nodos = len(desc.get("distribucion_nodos", pd.DataFrame())) if isinstance(desc.get("distribucion_nodos"), pd.DataFrame) else "N/A"
        total_nichos = len(desc.get("distribucion_nichos", pd.DataFrame())) if isinstance(desc.get("distribucion_nichos"), pd.DataFrame) else "N/A"
        html_parts.append(f"<p><b>Total Comunas:</b> {total_comunas}</p>")
        html_parts.append(f"<p><b>Total Nodos:</b> {total_nodos}</p>")
        html_parts.append(f"<p><b>Total Nichos:</b> {total_nichos}</p>")
        html_parts.append('</div>')

        dist_resp_data = desc.get("distribucion_respuestas")
        if isinstance(dist_resp_data, pd.DataFrame) and not dist_resp_data.empty:
            dist_resp = dist_resp_data
            respuesta_max = dist_resp.loc[dist_resp["Cantidad"].idxmax()]
            total_respuestas = dist_resp["Cantidad"].sum()
            de_acuerdo = dist_resp[dist_resp["Respuesta"] == "DE ACUERDO"]["Porcentaje"].iloc[0] if "DE ACUERDO" in dist_resp["Respuesta"].values else 0
            desacuerdo = dist_resp[dist_resp["Respuesta"] == "EN DESACUERDO"]["Porcentaje"].iloc[0] if "EN DESACUERDO" in dist_resp["Respuesta"].values else 0

            if de_acuerdo >= 60: interpretacion = "muy favorable"
            elif de_acuerdo >= 40: interpretacion = "favorable"
            elif desacuerdo >= 60: interpretacion = "muy desfavorable"
            elif desacuerdo >= 40: interpretacion = "desfavorable"
            else: interpretacion = "mixto/neutral"

            html_parts.append('<div class="summary-text"><h3>Distribución General de Respuestas</h3>')
            html_parts.append(f"<p>Se analizaron <b>{total_respuestas}</b> respuestas. La más frecuente fue <b>'{respuesta_max['Respuesta']}'</b> ({respuesta_max['Porcentaje']}%).</p>")
            html_parts.append(f"<p>Interpretación General del Clima: <b>{interpretacion.upper()}</b>.</p>")
            html_parts.append('</div>')
        else:
             html_parts.append("<p>Distribución de respuestas no disponible.</p>")
    else:
        html_parts.append("<p>Datos descriptivos no disponibles.</p>")
    html_parts.append('</div>') # Fin sección Vista General

    # --- Sección 2: Análisis por Dimensiones ---
    html_parts.append('<div class="section"><h2>Análisis por Dimensiones</h2>')
    if resultados and "dimensiones" in resultados and "promedios_dimensiones" in resultados["dimensiones"]:
        prom_dim_data = resultados["dimensiones"]["promedios_dimensiones"]
        if isinstance(prom_dim_data, pd.DataFrame) and not prom_dim_data.empty:
            prom_dim = prom_dim_data
            html_parts.append('<h3>Puntuación Promedio por Dimensión</h3>')
            def get_interpretation_class(interp):
                if interp == "Favorable": return "interpretation-favorable"
                if interp == "Neutral": return "interpretation-neutral"
                if interp == "Desfavorable": return "interpretation-desfavorable"
                return ""

            prom_dim_html = prom_dim.copy()
            prom_dim_html['Promedio'] = prom_dim_html['Promedio'].map('{:.2f}'.format)
            prom_dim_html['Interpretación'] = prom_dim_html.apply(lambda row: f'<span class="{get_interpretation_class(row["Interpretación"])}">{row["Interpretación"]}</span>', axis=1)
            html_parts.append(prom_dim_html[['Dimensión', 'Promedio', 'Interpretación']].to_html(escape=False, index=False, classes='dataframe')) # Añadir clase

            mejor_dim = prom_dim.iloc[0]
            peor_dim = prom_dim.iloc[-1]
            html_parts.append('<div class="dimension-summary"><h3>Resumen Dimensiones</h3>')
            html_parts.append(f"<p><b>Dimensión mejor evaluada:</b> {mejor_dim['Dimensión']} (Promedio: {mejor_dim['Promedio']:.2f} - {mejor_dim['Interpretación']})</p>")
            html_parts.append(f"<p><b>Dimensión peor evaluada:</b> {peor_dim['Dimensión']} (Promedio: {peor_dim['Promedio']:.2f} - {peor_dim['Interpretación']})</p>")
            html_parts.append('</div>')
        else:
            html_parts.append("<p>Promedios por dimensión no disponibles.</p>")
    else:
        html_parts.append("<p>Análisis por dimensiones no disponible.</p>")
    html_parts.append('</div>') # Fin sección Dimensiones

    # --- Sección 3: Liderazgo ---
    html_parts.append('<div class="section"><h2>Análisis de Liderazgo (Comparación por Rol)</h2>')
    if resultados_liderazgo and "error" not in resultados_liderazgo:
        resumen_conc = resultados_liderazgo.get("resumen_concordancia", {})
        comedores_ambos_roles = sum(resumen_conc.values())

        html_parts.append('<div class="liderazgo-summary"><h3>Concordancia entre Roles</h3>')
        if comedores_ambos_roles > 0:
            html_parts.append(f"<p>Análisis sobre <b>{comedores_ambos_roles}</b> comedores con ambos roles registrados.</p>")
            html_parts.append("<ul>")
            html_parts.append(f"<li><b>Alta Concordancia:</b> {resumen_conc.get('Alta', 0)} comedores</li>")
            html_parts.append(f"<li><b>Media Concordancia:</b> {resumen_conc.get('Media', 0)} comedores</li>")
            html_parts.append(f"<li><b>Baja Concordancia:</b> {resumen_conc.get('Baja', 0)} comedores</li>")
            html_parts.append("</ul>")

            comedores_baja_concordancia = [
                comedor for comedor, datos in resultados_liderazgo.get("analisis_comedores", {}).items()
                if datos.get("concordancia_global") == "Baja"
            ]
            if comedores_baja_concordancia:
                html_parts.append("<p class='warning'>⚠️ Comedores con Baja Concordancia (Potencial Intervención):</p><ul>")
                for comedor in sorted(comedores_baja_concordancia):
                    html_parts.append(f"<li>{comedor}</li>")
                html_parts.append("</ul>")
            else:
                html_parts.append("<p class='success'>✅ No se encontraron comedores con baja concordancia general entre roles.</p>")
        else:
            html_parts.append("<p>No hay suficientes datos (comedores con ambos roles) para calcular la concordancia.</p>")
        html_parts.append('</div>')
    else:
        html_parts.append("<p>Análisis de liderazgo no disponible o con errores.</p>")
    html_parts.append('</div>') # Fin sección Liderazgo

    # Añadir timestamp al final
    html_parts.append(f"<p class='timestamp'>Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
    # Cerrar HTML
    html_parts.append("</body></html>")

    return "\n".join(html_parts)


# --- Función Principal de la App ---
def main():
    """Función principal que ejecuta la aplicación Streamlit."""
    cargar_estilos_css()

    # --- Barra Lateral ---
    st.sidebar.markdown('<div class="sidebar-title">DIOR Analytics</div>', unsafe_allow_html=True)
    page = st.sidebar.radio(
        "Navegar",
        ["Vista General", "Análisis por Dimensiones", "Liderazgo", "Desempeño de Usuarios"],
        key="page_selection"
    )
    st.sidebar.markdown('## Configuración')
    n_clusters = st.sidebar.slider(
        "Número de clusters (Análisis Backend)", min_value=2, max_value=5, value=3,
        help="Selecciona el número de grupos para el análisis de clusters (usado en el backend)"
    )
    show_details = st.sidebar.checkbox(
        "Mostrar detalles avanzados", value=True,
        help="Activa esta opción para ver análisis más detallados"
    )
    st.session_state["show_details"] = show_details

    # --- Área Principal ---

    # Título principal y Descripción (AÑADIDO)
    st.markdown('<div class="main-header">Análisis de Clima Organizacional en Comedores Comunitarios</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="main-description">
    Análisis del clima organizacional en los comedores comunitarios,
    basado en la percepción de las gestoras y gestores sobre el relacionamiento, trabajo en equipo,
    liderazgos y sentido de pertenencia. Utilice la barra lateral para navegar entre las diferentes secciones del análisis y descargar un resumen.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---") # Separador

    # --- Variables para resultados ---
    df = None
    resultados = None
    figuras = None
    resultados_liderazgo = None

    try:
        # --- Carga de Datos ---
        if "df" not in st.session_state:
            with st.spinner("Cargando datos de Google Sheets..."):
                df = load_data()
                if df is None or df.empty:
                    st.error("No se pudieron cargar datos. Verifique la conexión.")
                    st.stop()
                else:
                    st.session_state["df"] = df
        else:
            df = st.session_state["df"]

        # --- Ejecución de Análisis ---
        cache_key = f"resultados_{n_clusters}"
        if cache_key not in st.session_state:
            with st.spinner("Analizando datos... Por favor espera."):
                resultados = ejecutar_analisis_completo(df_datos=df, n_clusters=n_clusters)
                figuras = generar_visualizaciones(resultados)
                st.session_state[cache_key] = (resultados, figuras)
        else:
            resultados, figuras = st.session_state[cache_key]

        # --- Pre-cálculo de Análisis de Liderazgo ---
        if resultados and "datos_preparados" in resultados:
             try:
                 if "resultados_liderazgo_actuales" not in st.session_state: # Calcular solo si no existe
                     resultados_liderazgo = analisis_liderazgo_por_rol(resultados["datos_preparados"])
                     st.session_state["resultados_liderazgo_actuales"] = resultados_liderazgo
                 else:
                     resultados_liderazgo = st.session_state["resultados_liderazgo_actuales"]
             except Exception as e_lider:
                 print(f"Advertencia: No se pudo pre-calcular análisis de liderazgo: {e_lider}")
                 resultados_liderazgo = {"error": str(e_lider)}
                 if "resultados_liderazgo_actuales" in st.session_state:
                     del st.session_state["resultados_liderazgo_actuales"]
        else:
             resultados_liderazgo = {"error": "Datos preparados no disponibles."}

        # Guardar referencias actuales para las páginas
        st.session_state["resultados_actuales"] = resultados
        st.session_state["figuras_actuales"] = figuras

        # --- Botón de Descarga en Sidebar ---
        st.sidebar.markdown('## Descargar Reporte')
        # Verificar que ambos resultados necesarios estén disponibles y sin errores
        if resultados and resultados_liderazgo and "error" not in resultados_liderazgo:
            reporte_html_content = generar_reporte_html(resultados, resultados_liderazgo)
            fecha_actual = datetime.now().strftime("%Y%m%d")
            nombre_archivo = f"resumen_analisis_dior_{fecha_actual}.html"
            st.sidebar.download_button(
                label="Descargar Resumen (HTML)",
                data=reporte_html_content,
                file_name=nombre_archivo,
                mime="text/html"
            )
        else:
            st.sidebar.info("Análisis necesarios incompletos para generar el reporte.")

        # --- Renderizar Página Seleccionada ---
        # El contenido de la página se mostrará DEBAJO del título y descripción principal
        if page == "Vista General":
            from pages.vista_general import mostrar_vista_general
            mostrar_vista_general(resultados, figuras, show_details)
        elif page == "Análisis por Dimensiones":
            from pages.dimensiones import mostrar_dimensiones
            mostrar_dimensiones(resultados, figuras)
        elif page == "Liderazgo":
            from pages.liderazgo import mostrar_liderazgo
            mostrar_liderazgo(resultados, df)
        elif page == "Desempeño de Usuarios":
            from pages.desempeno_usuarios import mostrar_desempeno_usuarios
            mostrar_desempeno_usuarios(df)

    except Exception as e:
        st.error(f"Ha ocurrido un error en la aplicación: {str(e)}")
        st.code(traceback.format_exc())
        st.info("Recomendación: Verifique la conexión y la estructura de los datos.")

# Punto de entrada
if __name__ == "__main__":
    main()
