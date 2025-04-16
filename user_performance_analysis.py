"""
Funciones para el análisis de desempeño por usuario (registradores)
Incluye análisis por fecha para determinar eficiencia por día de visita
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

def analizar_desempeno_usuarios(df):
    """
    Realiza un análisis de desempeño de los usuarios que registran las visitas.
    
    Args:
        df (DataFrame): DataFrame con los datos completos
        
    Returns:
        dict: Diccionario con los resultados del análisis
    """
    resultados = {}
    
    # Verificar que exista la columna USER
    if 'USER' not in df.columns:
        return {"error": "No se encontró la columna USER en los datos"}
    
    # Eliminar filas donde USER está vacío
    df_usuarios = df[df['USER'].notna() & (df['USER'] != '')].copy()
    
    if df_usuarios.empty:
        return {"error": "No hay datos de usuarios para analizar"}
    
    # Normalizar nombres de usuarios (eliminar espacios extra, convertir a mayúsculas)
    df_usuarios['USER'] = df_usuarios['USER'].str.strip().str.upper()
    
    # 1. Estadísticas básicas por usuario
    conteo_por_usuario = df_usuarios['USER'].value_counts().reset_index()
    conteo_por_usuario.columns = ['Usuario', 'Cantidad de Registros']
    
    # Calcular porcentaje del total
    total_registros = conteo_por_usuario['Cantidad de Registros'].sum()
    conteo_por_usuario['Porcentaje del Total'] = round(conteo_por_usuario['Cantidad de Registros'] / total_registros * 100, 2)
    
    resultados['conteo_por_usuario'] = conteo_por_usuario
    resultados['total_usuarios'] = len(conteo_por_usuario)
    resultados['total_registros'] = total_registros
    
    # 2. Analizar completitud de datos por usuario
    analisis_completitud = []
    
    # Obtener todas las columnas de preguntas por dimensión
    from analisis_dior import DIMENSIONES
    columnas_preguntas = []
    for dimension, preguntas in DIMENSIONES.items():
        columnas_preguntas.extend(preguntas)
    
    for usuario, grupo in df_usuarios.groupby('USER'):
        # Calcular el porcentaje de celdas no vacías para las preguntas de la encuesta
        
        # Para cada registro, calcular cuántas preguntas fueron respondidas
        total_posibles = len(columnas_preguntas) * len(grupo)
        respondidas = 0
        
        for pregunta in columnas_preguntas:
            if pregunta in grupo.columns:
                respondidas += grupo[pregunta].notna().sum()
        
        # Calcular el porcentaje de completitud
        if total_posibles > 0:
            porcentaje_completitud = round(respondidas / total_posibles * 100, 2)
        else:
            porcentaje_completitud = 0
        
        # Calcular promedio de respuestas por comedor
        promedio_por_comedor = respondidas / len(grupo) if len(grupo) > 0 else 0
        
        # Cantidad de comedores únicos visitados
        comedores_unicos = grupo['NOMBRE_COMEDOR'].nunique() if 'NOMBRE_COMEDOR' in grupo.columns else 0
        
        # Análisis de comunas y nodos
        comunas_visitadas = grupo['COMUNA'].nunique() if 'COMUNA' in grupo.columns else 0
        nodos_visitados = grupo['NODO'].nunique() if 'NODO' in grupo.columns else 0
        
        # Guardar resultados
        analisis_completitud.append({
            'Usuario': usuario,
            'Registros': len(grupo),
            'Comedores Visitados': comedores_unicos,
            'Comunas Visitadas': comunas_visitadas,
            'Nodos Visitados': nodos_visitados,
            'Completitud (%)': porcentaje_completitud,
            'Promedio Respuestas por Comedor': promedio_por_comedor,
        })
    
    df_completitud = pd.DataFrame(analisis_completitud)
    resultados['analisis_completitud'] = df_completitud
    
    # 3. Análisis por fecha (asumiendo que existe una columna de fecha)
    # Buscar posibles columnas de fecha en el DataFrame
    posibles_columnas_fecha = ['FECHA', 'DATE', 'FECHA_VISITA', 'FECHA_REGISTRO', 'DIA', 'TIMESTAMP', 'CREATED_AT']
    columna_fecha = None
    
    for col in posibles_columnas_fecha:
        if col in df_usuarios.columns:
            columna_fecha = col
            break
    
    # Si no se encuentra una columna específica, buscar columnas que contengan "fecha" o "date"
    if columna_fecha is None:
        for col in df_usuarios.columns:
            if 'fecha' in col.lower() or 'date' in col.lower() or 'day' in col.lower() or 'dia' in col.lower():
                columna_fecha = col
                break
    
    # Si se encuentra una columna de fecha, realizar análisis por fecha
    if columna_fecha:
        try:
            # Crear una copia para no modificar el DataFrame original
            df_con_fecha = df_usuarios.copy()
            
            # Intentar convertir la columna a datetime
            # Primero intentar con pd.to_datetime directamente
            try:
                df_con_fecha['fecha_procesada'] = pd.to_datetime(df_con_fecha[columna_fecha], errors='coerce')
            except:
                # Si falla, intentar extraer fecha con expresiones regulares (formatos comunes)
                # Buscar patrones como DD/MM/YYYY, YYYY-MM-DD, etc.
                fecha_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})'
                df_con_fecha['fecha_extraida'] = df_con_fecha[columna_fecha].astype(str).str.extract(fecha_pattern, expand=False)
                df_con_fecha['fecha_procesada'] = pd.to_datetime(df_con_fecha['fecha_extraida'], errors='coerce')
            
            # Filtrar registros con fechas válidas
            df_fechas_validas = df_con_fecha[df_con_fecha['fecha_procesada'].notna()].copy()
            
            if not df_fechas_validas.empty:
                # Extraer componentes de fecha
                df_fechas_validas['dia_semana'] = df_fechas_validas['fecha_procesada'].dt.day_name()
                df_fechas_validas['mes'] = df_fechas_validas['fecha_procesada'].dt.month_name()
                df_fechas_validas['ano'] = df_fechas_validas['fecha_procesada'].dt.year
                df_fechas_validas['fecha_corta'] = df_fechas_validas['fecha_procesada'].dt.strftime('%d/%m/%Y')
                
                # Análisis por día de la semana
                registros_por_dia = df_fechas_validas.groupby(['dia_semana', 'USER']).size().reset_index(name='registros')
                
                # Calcular promedio de registros por día y usuario
                promedio_por_dia_usuario = registros_por_dia.groupby(['USER', 'dia_semana'])['registros'].mean().reset_index()
                promedio_por_dia_usuario['registros'] = promedio_por_dia_usuario['registros'].round(2)
                
                # Eficiencia por día (registros por día de visita)
                fechas_unicas_por_usuario = df_fechas_validas.groupby('USER')['fecha_corta'].nunique().reset_index()
                fechas_unicas_por_usuario.columns = ['Usuario', 'Dias de Visita']
                
                # Unir con la información de número de registros
                eficiencia_por_usuario = fechas_unicas_por_usuario.merge(
                    conteo_por_usuario[['Usuario', 'Cantidad de Registros']], 
                    on='Usuario', 
                    how='left'
                )
                
                # Calcular promedio de registros por día de visita
                eficiencia_por_usuario['Promedio Registros por Día'] = (
                    eficiencia_por_usuario['Cantidad de Registros'] / 
                    eficiencia_por_usuario['Dias de Visita']
                ).round(2)
                
                # Guardar resultados
                resultados['registros_por_dia_semana'] = registros_por_dia
                resultados['promedio_por_dia_usuario'] = promedio_por_dia_usuario
                resultados['eficiencia_por_usuario'] = eficiencia_por_usuario
                resultados['columna_fecha_usada'] = columna_fecha
                
            else:
                resultados['error_fecha'] = f"No se pudieron procesar fechas válidas de la columna '{columna_fecha}'"
        
        except Exception as e:
            resultados['error_fecha'] = f"Error al procesar fechas: {str(e)}"
    else:
        resultados['error_fecha'] = "No se encontró una columna de fecha en los datos"
    
    return resultados

def generar_visualizaciones_desempeno(resultados_usuarios):
    """
    Genera visualizaciones simplificadas para el análisis de desempeño de usuarios.
    
    Args:
        resultados_usuarios (dict): Resultados del análisis de desempeño
        
    Returns:
        dict: Diccionario con figuras de Plotly
    """
    figuras = {}
    
    if "error" in resultados_usuarios:
        return {"error": resultados_usuarios["error"]}
    
    # 1. Gráfico de barras de registros por usuario
    if "conteo_por_usuario" in resultados_usuarios:
        df_conteo = resultados_usuarios["conteo_por_usuario"]
        
        # Ordenar por cantidad de registros (descendente)
        df_conteo = df_conteo.sort_values("Cantidad de Registros", ascending=False)
        
        fig_registros = px.bar(
            df_conteo,
            x="Usuario",
            y="Cantidad de Registros",
            title="Cantidad de Registros por Usuario",
            color="Cantidad de Registros",
            color_continuous_scale="Viridis",
            text_auto=True
        )
        
        fig_registros.update_layout(
            xaxis_title="Usuario",
            yaxis_title="Número de Registros",
            xaxis={'categoryorder':'total descending'}
        )
        
        figuras["registros_por_usuario"] = fig_registros
    
    # 2. Gráfico de eficiencia por día (registros por día de visita)
    if "eficiencia_por_usuario" in resultados_usuarios:
        df_eficiencia = resultados_usuarios["eficiencia_por_usuario"]
        
        # Ordenar por promedio de registros por día (descendente)
        df_eficiencia = df_eficiencia.sort_values("Promedio Registros por Día", ascending=False)
        
        fig_eficiencia = px.bar(
            df_eficiencia,
            x="Usuario",
            y="Promedio Registros por Día",
            title="Promedio de Registros por Día de Visita",
            color="Promedio Registros por Día",
            color_continuous_scale="YlOrRd",
            text_auto=True
        )
        
        fig_eficiencia.update_layout(
            xaxis_title="Usuario",
            yaxis_title="Promedio de Registros por Día",
            xaxis={'categoryorder':'total descending'}
        )
        
        figuras["eficiencia_por_dia"] = fig_eficiencia
    
    return figuras