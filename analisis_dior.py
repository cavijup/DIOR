import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
from scipy import stats

# Importar constantes y funciones de utilidad
from config import GRUPOS_COLUMNAS, COLUMNAS_UBICACION, MAPEO_RESPUESTAS
from utils import obtener_letra_a_indice, interpretar_promedio

def preparar_dataframe(df):
    """
    Prepara el DataFrame para el análisis, mapeando valores de respuesta a números.
    """
    # Crear una copia para no modificar el original
    df_analisis = df.copy()
    
    # Aplicar el mapeo a todas las columnas de encuesta
    for grupo, columnas in GRUPOS_COLUMNAS.items():
        for nombre_col, letra_col in columnas.items():
            # Intentar acceder por nombre si existe
            if nombre_col in df_analisis.columns:
                df_analisis[nombre_col] = df_analisis[nombre_col].map(MAPEO_RESPUESTAS).fillna(0).astype(int)
            # Intentar acceder por índice si es necesario
            else:
                indice = obtener_letra_a_indice(letra_col)
                if indice >= 0 and indice < len(df_analisis.columns):
                    col_actual = df_analisis.columns[indice]
                    df_analisis[col_actual] = df_analisis[col_actual].map(MAPEO_RESPUESTAS).fillna(0).astype(int)
                    # Renombrar para claridad
                    df_analisis.rename(columns={col_actual: nombre_col}, inplace=True)
    
    return df_analisis

def mostrar_analisis(df):
    """
    Función principal que muestra el análisis de los datos DIOR
    """
    # Verificar que haya datos
    if df is None or df.empty:
        st.error("No hay datos para analizar.")
        return
    
    st.header("Análisis de datos DIOR")
    
    # Mostrar las primeras filas del DataFrame
    st.subheader("Vista previa de datos")
    st.dataframe(df.head(10), use_container_width=True)
    
    # Preparar el DataFrame para análisis
    df_analisis = preparar_dataframe(df)
    
    # Mostrar análisis por grupos
    for grupo, columnas in GRUPOS_COLUMNAS.items():
        st.subheader(f"Análisis de {grupo}")
        
        # Para cada grupo, mostrar estadísticas y visualizaciones
        for nombre_col, letra_col in columnas.items():
            # Intentar encontrar la columna
            columna_encontrada = None
            
            # Verificar por nombre
            if nombre_col in df_analisis.columns:
                columna_encontrada = nombre_col
            else:
                # Intentar encontrar por índice de letra
                indice = obtener_letra_a_indice(letra_col)
                if indice >= 0 and indice < len(df_analisis.columns):
                    columna_encontrada = df_analisis.columns[indice]
            
            if columna_encontrada:
                st.write(f"### {nombre_col.replace('_', ' ')}")
                
                # Mostrar conteo de respuestas
                conteo = df_analisis[columna_encontrada].value_counts().sort_index()
                
                # Transformar los números de vuelta a etiquetas para visualización
                etiquetas_inversas = {v: k for k, v in MAPEO_RESPUESTAS.items()}
                
                # Preparar los datos para mostrarlos
                resultados_conteo = []
                for valor in range(1, 6):
                    if valor in conteo.index:
                        etiqueta = etiquetas_inversas.get(valor, f"Valor {valor}")
                        cantidad = conteo[valor]
                        porcentaje = (cantidad / conteo.sum() * 100).round(2)
                        resultados_conteo.append({
                            'Respuesta': etiqueta,
                            'Valor': valor,
                            'Cantidad': cantidad,
                            'Porcentaje': porcentaje
                        })
                
                # Crear dos columnas para mostrar tabla y gráfico lado a lado
                col1, col2 = st.columns([1, 2])  # Proporción 1:2 para tabla:gráfico
                
                with col1:
                    # Tabla de conteo
                    st.write("#### Distribución de respuestas:")
                    st.dataframe(pd.DataFrame(resultados_conteo), height=220)
                
                with col2:
                    # Gráfico de barras
                    fig = px.bar(
                        resultados_conteo,
                        x='Respuesta', 
                        y='Cantidad',
                        title=f"Distribución de respuestas para {nombre_col.replace('_', ' ')}",
                        color='Respuesta',
                        color_discrete_sequence=px.colors.sequential.Blues_r  # Tonos de azul invertidos (más oscuro = mayor valor)
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
    
    # Resumen general usando MODA (valor más frecuente) para el análisis estadístico
    st.subheader("Resumen General")
    
    # Calcular medidas por grupo
    resumen_grupo = {}
    
    for grupo, columnas in GRUPOS_COLUMNAS.items():
        # Recopilar columnas existentes para este grupo
        cols_existentes = []
        for nombre_col, letra_col in columnas.items():
            if nombre_col in df_analisis.columns:
                cols_existentes.append(nombre_col)
            else:
                indice = obtener_letra_a_indice(letra_col)
                if indice >= 0 and indice < len(df_analisis.columns):
                    cols_existentes.append(df_analisis.columns[indice])
        
        if cols_existentes:
            # Concatenar todas las respuestas de este grupo en una sola serie
            todas_respuestas = pd.Series()
            for col in cols_existentes:
                todas_respuestas = pd.concat([todas_respuestas, df_analisis[col]])
            
            # Calcular estadísticas
            try:
                moda = stats.mode(todas_respuestas, keepdims=True).mode[0]
            except:
                # Fallback si hay un error con stats.mode
                moda = todas_respuestas.value_counts().idxmax()
                
            # También calcular la media (promedio) para mantener consistencia con análisis anterior
            media = todas_respuestas.mean()
            
            resumen_grupo[grupo] = {
                'moda': moda,
                'media': media
            }
    
    # Mostrar resumen por grupo
    if resumen_grupo:
        # Crear columnas para visualización
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Gráfico de barras con la moda
            moda_data = pd.DataFrame({
                'Grupo': [grupo for grupo in resumen_grupo.keys()],
                'Moda': [resumen_grupo[grupo]['moda'] for grupo in resumen_grupo.keys()]
            })
            
            fig_moda = px.bar(
                moda_data,
                x='Grupo', 
                y='Moda',
                title="Respuesta más frecuente por grupo",
                color='Grupo',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            # Añadir etiqueta de interpretación sobre cada barra
            for i, grupo in enumerate(resumen_grupo.keys()):
                moda = resumen_grupo[grupo]['moda']
                interpretacion = interpretar_promedio(moda)
                fig_moda.add_annotation(
                    x=i,
                    y=moda + 0.1,
                    text=interpretacion,
                    showarrow=False,
                    font=dict(size=12)
                )
            
            fig_moda.update_layout(height=400)
            st.plotly_chart(fig_moda, use_container_width=True)
        
        with col2:
            # Tabla de resumen
            st.write("#### Análisis por grupo:")
            resumen_data = []
            
            for grupo in resumen_grupo.keys():
                moda_valor = resumen_grupo[grupo]['moda']
                media_valor = resumen_grupo[grupo]['media']
                
                resumen_data.append({
                    'Grupo': grupo,
                    'Moda': moda_valor,
                    'Interpretación': interpretar_promedio(moda_valor),
                    'Media': round(media_valor, 2)
                })
            
            st.dataframe(pd.DataFrame(resumen_data), height=230)