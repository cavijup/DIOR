import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

# Importar constantes y funciones de utilidad
from config import GRUPOS_COLUMNAS, COLUMNAS_UBICACION, MAPEO_RESPUESTAS
from utils import obtener_letra_a_indice

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

def mostrar_analisis_correlacion(df):
    """
    Muestra el análisis de correlación de Spearman para las variables de la encuesta
    """
    # Verificar que haya datos
    if df is None or df.empty:
        st.error("No hay datos para analizar.")
        return
    
    st.header("Análisis de Correlación")
    
    # Preparar el DataFrame para análisis
    df_analisis = preparar_dataframe(df)
    
    # Recopilar todas las columnas de encuesta
    columnas_encuesta = []
    nombres_cortos = {}  # Para usar nombres más cortos en el mapa de calor
    
    for grupo, columnas in GRUPOS_COLUMNAS.items():
        for nombre_col, letra_col in columnas.items():
            # Verificar por nombre
            if nombre_col in df_analisis.columns:
                columnas_encuesta.append(nombre_col)
                # Crear nombre más corto para la visualización
                nombres_cortos[nombre_col] = nombre_col.replace('_', ' ').title()[:15] + '...'
            else:
                # Intentar encontrar por índice de letra
                indice = obtener_letra_a_indice(letra_col)
                if indice >= 0 and indice < len(df_analisis.columns):
                    col_actual = df_analisis.columns[indice]
                    columnas_encuesta.append(col_actual)
                    nombres_cortos[col_actual] = nombre_col.replace('_', ' ').title()[:15] + '...'
    
    # Verificar que hayamos encontrado columnas para analizar
    if not columnas_encuesta:
        st.error("No se encontraron columnas de encuesta para analizar.")
        return
    
    # Calcular matriz de correlación de Spearman
    st.subheader("Matriz de Correlación de Spearman")
    
    # Seleccionar solo las columnas de la encuesta
    df_correlacion = df_analisis[columnas_encuesta]
    
    # Manejar posibles valores nulos
    df_correlacion = df_correlacion.fillna(0)
    
    try:
        # Calcular la matriz de correlación de Spearman
        correlation_matrix = df_correlacion.corr(method='spearman')
        
        # Explicación de la correlación
        st.info("""
        **Interpretación del Coeficiente de Correlación de Spearman:**
        - **Colores oscuros rojos**: Correlación negativa fuerte
        - **Colores claros**: Correlación débil o nula
        - **Colores oscuros azules**: Correlación positiva fuerte
        
        Se muestra solo la mitad inferior del mapa de calor para mayor claridad, ya que la matriz de correlación es simétrica.
        """)
        
        # Preparar nombres más cortos para la matriz
        correlation_matrix_renamed = correlation_matrix.copy()
        if len(nombres_cortos) > 0:
            correlation_matrix_renamed.index = [nombres_cortos.get(col, col) for col in correlation_matrix.index]
            correlation_matrix_renamed.columns = [nombres_cortos.get(col, col) for col in correlation_matrix.columns]
        
        # Crear una máscara para mostrar solo la mitad inferior
        mask = np.triu(np.ones_like(correlation_matrix_renamed, dtype=bool))
        
        # Usar matplotlib/seaborn para matriz estática sin números (solo mitad inferior)
        plt.figure(figsize=(14, 12))
        cmap = sns.diverging_palette(230, 20, as_cmap=True)
        
        # Crear el mapa de calor sin anotaciones y solo con la mitad inferior
        heatmap = sns.heatmap(
            correlation_matrix_renamed, 
            mask=mask,  # Usar la máscara para mostrar solo la mitad inferior
            annot=False,  # Sin números
            cmap=cmap,
            vmin=-1, vmax=1, 
            center=0,
            square=True, 
            linewidths=.5, 
            cbar_kws={"shrink": .5, "label": "Coeficiente de Spearman"}
        )
        
        plt.title("Mapa de Calor - Correlación de Spearman", fontsize=16)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        st.pyplot(plt.gcf())
        
        # Mostrar todas las correlaciones (umbral desde -1 hasta 1)
        st.subheader("Todas las Correlaciones (-1.0 a 1.0)")
        
        # Obtener todos los pares de variables con sus correlaciones
        todas_correlaciones = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                var1 = correlation_matrix.columns[i]
                var2 = correlation_matrix.columns[j]
                coef = correlation_matrix.iloc[i, j]
                
                var1_nombre = var1.replace('_', ' ')
                var2_nombre = var2.replace('_', ' ')
                
                todas_correlaciones.append({
                    'Variable 1': var1_nombre,
                    'Variable 2': var2_nombre,
                    'Coeficiente': coef,
                    'Tipo': 'Positiva' if coef > 0 else 'Negativa',
                    'Fuerza': interpret_correlation_strength(coef)
                })
        
        # Mostrar tabla de todas las correlaciones
        if todas_correlaciones:
            df_todas = pd.DataFrame(todas_correlaciones)
            df_todas = df_todas.sort_values(by='Coeficiente', ascending=False)
            
            # Color condicional para la tabla
            st.dataframe(
                df_todas,
                column_config={
                    "Coeficiente": st.column_config.NumberColumn(
                        "Coeficiente",
                        format="%.3f",
                    ),
                },
                use_container_width=True
            )
            
        else:
            st.write("No se encontraron correlaciones.")
        
    except Exception as e:
        st.error(f"Error al calcular la matriz de correlación: {str(e)}")
        st.code(str(e))

def interpret_correlation_strength(coef):
    """Interpreta la fuerza de la correlación según su valor absoluto"""
    abs_coef = abs(coef)
    if abs_coef >= 0.90:
        return "Muy alta"
    elif abs_coef >= 0.70:
        return "Alta"
    elif abs_coef >= 0.40:
        return "Moderada"
    elif abs_coef >= 0.20:
        return "Baja"
    else:
        return "Muy baja"