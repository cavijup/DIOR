import streamlit as st
import pandas as pd

# Importar las funciones necesarias
from user_performance_analysis import analizar_desempeno_usuarios, generar_visualizaciones_desempeno

def mostrar_desempeno_usuarios(df):
    """
    Muestra la página de análisis de desempeño de usuarios.
    
    Args:
        df: DataFrame con los datos originales
    """
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
        mostrar_metricas_usuarios(resultados_usuarios)
        mostrar_analisis_registros(resultados_usuarios, figuras_usuarios)
        mostrar_eficiencia_por_dia(resultados_usuarios, figuras_usuarios)

def mostrar_metricas_usuarios(resultados_usuarios):
    """
    Muestra las métricas principales del análisis de usuarios.
    
    Args:
        resultados_usuarios: Diccionario con los resultados del análisis de usuarios
    """
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

def mostrar_analisis_registros(resultados_usuarios, figuras_usuarios):
    """
    Muestra el análisis de registros por usuario.
    
    Args:
        resultados_usuarios: Diccionario con los resultados del análisis de usuarios
        figuras_usuarios: Diccionario con las figuras generadas para el análisis de usuarios
    """
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
    
    # Análisis de completitud si está disponible
    if "analisis_completitud" in resultados_usuarios:
        df_completitud = resultados_usuarios["analisis_completitud"]
        
        st.subheader("Análisis de Completitud de Datos")
        
        with st.expander("Ver análisis de completitud por usuario"):
            st.dataframe(
                df_completitud,
                column_config={
                    "Usuario": "Usuario",
                    "Registros": st.column_config.NumberColumn("Total de Registros", format="%d"),
                    "Comedores Visitados": st.column_config.NumberColumn("Comedores Visitados", format="%d"),
                    "Comunas Visitadas": st.column_config.NumberColumn("Comunas Visitadas", format="%d"),
                    "Nodos Visitados": st.column_config.NumberColumn("Nodos Visitados", format="%d"),
                    "Completitud (%)": st.column_config.ProgressColumn("Completitud", format="%.1f%%", min_value=0, max_value=100),
                    "Promedio Respuestas por Comedor": st.column_config.NumberColumn("Promedio Respuestas/Comedor", format="%.1f")
                },
                use_container_width=True,
                hide_index=True
            )

def mostrar_eficiencia_por_dia(resultados_usuarios, figuras_usuarios):
    """
    Muestra el análisis de eficiencia por día de visita.
    
    Args:
        resultados_usuarios: Diccionario con los resultados del análisis de usuarios
        figuras_usuarios: Diccionario con las figuras generadas para el análisis de usuarios
    """
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
            
        # Análisis adicional por día de la semana si está disponible
        if "registros_por_dia_semana" in resultados_usuarios:
            with st.expander("Ver análisis por día de la semana"):
                registros_por_dia = resultados_usuarios["registros_por_dia_semana"]
                
                # Convertir a un DataFrame con formato más amigable
                pivot_dias = registros_por_dia.pivot_table(
                    index='USER', 
                    columns='dia_semana', 
                    values='registros',
                    fill_value=0
                ).reset_index()
                
                # Reordenar días de la semana si es posible
                dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                # Crear configuración de columnas
                column_config = {"USER": "Usuario"}
                for dia in dias_orden:
                    if dia in pivot_dias.columns:
                        column_config[dia] = st.column_config.NumberColumn(dia, format="%d")
                
                st.dataframe(
                    pivot_dias,
                    column_config=column_config,
                    use_container_width=True,
                    hide_index=True
                )
    else:
        if "error_fecha" in resultados_usuarios:
            st.warning(f"No se pudo realizar el análisis por fecha: {resultados_usuarios['error_fecha']}")
        else:
            st.warning("No hay datos suficientes para analizar la eficiencia por día de visita.")