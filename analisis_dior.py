import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import spearmanr
import streamlit as st

# Mapeo de respuestas de la encuesta a valores numéricos
MAPEO_RESPUESTAS = {
    "DE ACUERDO": 3,
    "NI DEACUERDO, NI EN DESACUERDO": 2,
    "EN DESACUERDO": 1
}

# Agrupación de preguntas por dimensiones/categorías
DIMENSIONES = {
    "Trabajo en equipo": [
        "1.1_A_GUSTO_TRABAJANDO_CON_OTRAS_GESTORAS",
        "1.2_LIBRE_EXPRESAR_IDEAS_SUGERENCIAS",
        "1.3_DECISIONES_IMPORTANTES_COMUNICADAS",
        "1.4_CONVERSACIONES_RESPETUOSAS"
    ],
    "Liderazgo": [
        "2.1_LIDERAZGO_RESPESTUOSO",
        "2.2_OPORTUNIDAD_DE_PROPONER_IDEAS",
        "2.3_ESPACIOS_ADECUADOS_RETROALIMENTACION"
    ],
    "Compromiso": [
        "3.1_GESTORAS_COMPROMETIDAS",
        "3.2_EQUIPO_UNIDO",
        "3.3_NORMAS_DE_SEGURIDAD_DOTACION"
    ],
    "Valoración": [
        "4.1_LABOR_VALORADA",
        "4.2_ESFUERZO_IGUAL_DE_VALORADO",
        "4.3_HABILIDADES_RECONOCIDAS"
    ],
    "Comunicación": [
        "5.1_DIALOGO_CON_RESPETO",
        "5.2_OPINION_TENIDA_EN_CUENTA",
        "5.3_EMOCIONES_TOMADES_ENSERIO"
    ],
    "Recursos y condiciones": [
        "6.1_INSUMOS_HERRAMIENTAS_NECESARIAS",
        "6.2_ESPACIO_COMODO_SEGURO",
        "6.3_AUSENCIA_POR_URGENCIA"
    ],
    "Bienestar": [
        "7.1_MOMENTOS_DE_PAUSA",
        "7.2_AUTOCUIDADO",
        "7.3_ESPACIOS_PARA_ALEGRIA",
        "7.4_TIEMPO_OBLIGACIONES_FAMILIARES"
    ]
}

# Columnas de información demográfica
DEMOGRAFICAS = [
    "NOMBRE_COMEDOR",
    "UBICACION",
    "BARRIO",
    "COMUNA",
    "NODO",
    "NICHO"
]

def preparar_datos(df):
    """
    Prepara los datos para el análisis, convirtiendo las respuestas 
    de texto a valores numéricos.
    
    Args:
        df (DataFrame): DataFrame con los datos originales
        
    Returns:
        DataFrame: DataFrame preparado para análisis
    """
    if df is None or df.empty:
        return None
        
    df_prep = df.copy()
    
    # Convertir respuestas de texto a valores numéricos
    for dimension, preguntas in DIMENSIONES.items():
        for pregunta in preguntas:
            if pregunta in df_prep.columns:
                df_prep[pregunta] = df_prep[pregunta].map(MAPEO_RESPUESTAS).fillna(0).astype(int)
    
    return df_prep

def calcular_promedios_por_dimension(df):
    """
    Calcula el promedio de cada dimensión.
    
    Args:
        df (DataFrame): DataFrame preparado con valores numéricos
        
    Returns:
        dict: Diccionario con los promedios por dimensión
    """
    promedios = {}
    
    for dimension, preguntas in DIMENSIONES.items():
        # Filtrar solo preguntas existentes en el DataFrame
        preguntas_existentes = [p for p in preguntas if p in df.columns]
        
        if preguntas_existentes:
            # Calcular promedio de la dimensión
            promedios[dimension] = df[preguntas_existentes].mean(axis=1).mean()
    
    return promedios

def interpretar_promedio(valor):
    """
    Interpreta el valor promedio según la escala de 1-3.
    
    Args:
        valor (float): Valor promedio
        
    Returns:
        str: Interpretación del valor
    """
    if valor < 1.5:
        return "Desfavorable"
    elif valor < 2.5:
        return "Neutral"
    else:
        return "Favorable"

# 3.1 Análisis descriptivo básico
def analisis_descriptivo(df, df_prep):
    """
    Realiza un análisis descriptivo básico de los datos.
    
    Args:
        df (DataFrame): DataFrame original
        df_prep (DataFrame): DataFrame preparado con valores numéricos
        
    Returns:
        dict: Diccionario con los resultados del análisis
    """
    resultados = {}
    
    # Número de comedores
    if "NOMBRE_COMEDOR" in df.columns:
        resultados["total_comedores"] = df["NOMBRE_COMEDOR"].nunique()
    else:
        resultados["total_comedores"] = len(df)
    
    # Distribución por comuna
    if "COMUNA" in df.columns:
        comunas = df["COMUNA"].value_counts().reset_index()
        comunas.columns = ["Comuna", "Cantidad"]
        resultados["distribucion_comunas"] = comunas
    
    # Distribución por nodo
    if "NODO" in df.columns:
        nodos = df["NODO"].value_counts().reset_index()
        nodos.columns = ["Nodo", "Cantidad"]
        resultados["distribucion_nodos"] = nodos
    
    # Distribución por nicho
    if "NICHO" in df.columns:
        nichos = df["NICHO"].value_counts().reset_index()
        nichos.columns = ["Nicho", "Cantidad"]
        resultados["distribucion_nichos"] = nichos
    
    # Distribución general de respuestas
    respuestas_todas = []
    
    for dimension, preguntas in DIMENSIONES.items():
        for pregunta in preguntas:
            if pregunta in df_prep.columns:
                values = df_prep[pregunta].dropna()
                respuestas_todas.extend(values)
    
    if respuestas_todas:
        conteo = pd.Series(respuestas_todas).value_counts().sort_index()
        
        # Mapear valores numéricos a etiquetas
        etiquetas = {
            1: "EN DESACUERDO",
            2: "NI DEACUERDO, NI EN DESACUERDO",
            3: "DE ACUERDO"
        }
        
        distribucion = pd.DataFrame({
            "Respuesta": [etiquetas.get(i, str(i)) for i in conteo.index],
            "Cantidad": conteo.values,
            "Porcentaje": (conteo.values / sum(conteo.values) * 100).round(2)
        })
        
        resultados["distribucion_respuestas"] = distribucion
    
    return resultados

# 3.2 Análisis por dimensiones
def analisis_por_dimensiones(df_prep):
    """
    Realiza un análisis por dimensiones.
    
    Args:
        df_prep (DataFrame): DataFrame preparado con valores numéricos
        
    Returns:
        dict: Diccionario con los resultados del análisis
    """
    resultados = {}
    
    # Promedios por dimensión
    promedios = calcular_promedios_por_dimension(df_prep)
    
    if promedios:
        promedios_df = pd.DataFrame({
            "Dimensión": list(promedios.keys()),
            "Promedio": list(promedios.values())
        })
        promedios_df["Interpretación"] = promedios_df["Promedio"].apply(interpretar_promedio)
        promedios_df = promedios_df.sort_values("Promedio", ascending=False)
        
        resultados["promedios_dimensiones"] = promedios_df
        
        # Dimensión mejor evaluada
        resultados["dimension_mejor"] = promedios_df.iloc[0]["Dimensión"]
        resultados["promedio_mejor"] = promedios_df.iloc[0]["Promedio"]
        
        # Dimensión peor evaluada
        resultados["dimension_peor"] = promedios_df.iloc[-1]["Dimensión"]
        resultados["promedio_peor"] = promedios_df.iloc[-1]["Promedio"]
    
    # Análisis detallado por pregunta
    analisis_preguntas = {}
    
    for dimension, preguntas in DIMENSIONES.items():
        analisis_dimension = {}
        
        for pregunta in preguntas:
            if pregunta in df_prep.columns:
                valores = df_prep[pregunta].dropna()
                
                if len(valores) > 0:
                    conteo = valores.value_counts().sort_index()
                    porcentajes = (conteo / conteo.sum() * 100).round(2)
                    
                    # Mapear valores numéricos a etiquetas
                    etiquetas = {
                        1: "EN DESACUERDO",
                        2: "NI DEACUERDO, NI EN DESACUERDO",
                        3: "DE ACUERDO"
                    }
                    
                    distribucion = pd.DataFrame({
                        "Respuesta": [etiquetas.get(i, str(i)) for i in conteo.index],
                        "Cantidad": conteo.values,
                        "Porcentaje": porcentajes.values
                    })
                    
                    promedio = valores.mean()
                    
                    analisis_dimension[pregunta] = {
                        "distribucion": distribucion,
                        "promedio": promedio,
                        "interpretacion": interpretar_promedio(promedio)
                    }
        
        if analisis_dimension:
            analisis_preguntas[dimension] = analisis_dimension
    
    resultados["analisis_preguntas"] = analisis_preguntas
    
    return resultados

# 3.3 Análisis de correlaciones
def analisis_correlaciones(df_prep):
    """
    Realiza un análisis de correlaciones entre las preguntas.
    
    Args:
        df_prep (DataFrame): DataFrame preparado con valores numéricos
        
    Returns:
        dict: Diccionario con los resultados del análisis
    """
    resultados = {}
    
    # Recopilar todas las preguntas
    todas_preguntas = []
    for dimension, preguntas in DIMENSIONES.items():
        todas_preguntas.extend([p for p in preguntas if p in df_prep.columns])
    
    if todas_preguntas:
        # Calcular matriz de correlación de Spearman
        matriz_corr = df_prep[todas_preguntas].corr(method="spearman")
        resultados["matriz_correlacion"] = matriz_corr
        
        # Crear versión de la matriz con nombres cortos para visualización
        nombres_cortos = {}
        for pregunta in todas_preguntas:
            # Extraer el código numérico (como 1.1, 2.3, etc.)
            partes = pregunta.split('_')
            if partes and partes[0].replace('.', '').isdigit():
                nombres_cortos[pregunta] = partes[0]
        
        if nombres_cortos:
            matriz_corr_corta = matriz_corr.copy()
            matriz_corr_corta = matriz_corr_corta.rename(index=nombres_cortos, columns=nombres_cortos)
            resultados["matriz_correlacion_corta"] = matriz_corr_corta
        
        # Identificar correlaciones más fuertes (positivas y negativas)
        correlaciones = []
        
        for i in range(len(todas_preguntas)):
            for j in range(i+1, len(todas_preguntas)):
                p1 = todas_preguntas[i]
                p2 = todas_preguntas[j]
                corr = matriz_corr.iloc[i, j]
                
                # Encontrar a qué dimensión pertenece cada pregunta
                dim1 = next((dim for dim, pregs in DIMENSIONES.items() if p1 in pregs), "Desconocida")
                dim2 = next((dim for dim, pregs in DIMENSIONES.items() if p2 in pregs), "Desconocida")
                
                # Nombres cortos
                p1_corto = nombres_cortos.get(p1, p1)
                p2_corto = nombres_cortos.get(p2, p2)
                
                correlaciones.append({
                    "pregunta1": p1,
                    "pregunta2": p2,
                    "pregunta1_corta": p1_corto,
                    "pregunta2_corta": p2_corto,
                    "dimension1": dim1,
                    "dimension2": dim2,
                    "correlacion": corr,
                    "correlacion_abs": abs(corr)
                })
        
        df_corrs = pd.DataFrame(correlaciones)
        
        # Top correlaciones positivas
        top_positivas = df_corrs[df_corrs["correlacion"] > 0].sort_values("correlacion", ascending=False).head(10)
        resultados["top_correlaciones_positivas"] = top_positivas
        
        # Top correlaciones negativas
        top_negativas = df_corrs[df_corrs["correlacion"] < 0].sort_values("correlacion", ascending=True).head(10)
        resultados["top_correlaciones_negativas"] = top_negativas
        
        # Correlaciones entre dimensiones
        correlaciones_dim = {}
        
        for dim1 in DIMENSIONES.keys():
            correlaciones_dim[dim1] = {}
            
            for dim2 in DIMENSIONES.keys():
                if dim1 != dim2:
                    pregs1 = [p for p in DIMENSIONES[dim1] if p in df_prep.columns]
                    pregs2 = [p for p in DIMENSIONES[dim2] if p in df_prep.columns]
                    
                    if pregs1 and pregs2:
                        # Calcular correlación promedio entre las dimensiones
                        corrs = []
                        for p1 in pregs1:
                            for p2 in pregs2:
                                idx1 = todas_preguntas.index(p1)
                                idx2 = todas_preguntas.index(p2)
                                corrs.append(matriz_corr.iloc[idx1, idx2])
                        
                        correlaciones_dim[dim1][dim2] = sum(corrs) / len(corrs)
        
        # Convertir a DataFrame
        df_corrs_dim = pd.DataFrame(correlaciones_dim)
        resultados["correlaciones_dimensiones"] = df_corrs_dim
    
    return resultados

# 3.4 Análisis de conglomerados (clusters)
def analisis_clusters(df, df_prep, n_clusters=3):
    """
    Realiza un análisis de conglomerados para identificar perfiles de comedores.
    
    Args:
        df (DataFrame): DataFrame original
        df_prep (DataFrame): DataFrame preparado con valores numéricos
        n_clusters (int): Número de clusters a generar
        
    Returns:
        dict: Diccionario con los resultados del análisis
    """
    resultados = {}
    
    # Recopilar todas las preguntas
    todas_preguntas = []
    for dimension, preguntas in DIMENSIONES.items():
        todas_preguntas.extend([p for p in preguntas if p in df_prep.columns])
    
    if todas_preguntas:
        # Preparar datos para clustering
        X = df_prep[todas_preguntas].fillna(df_prep[todas_preguntas].mean())
        
        # Escalar datos
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Aplicar K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Añadir etiquetas de cluster al DataFrame
        df_clusters = df.copy()
        df_clusters["Cluster"] = clusters
        
        resultados["clusters"] = df_clusters
        resultados["n_clusters"] = n_clusters
        resultados["kmeans_model"] = kmeans
        
        # Reducir dimensionalidad para visualización
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        # Crear DataFrame para visualización
        df_pca = pd.DataFrame({
            "PCA1": X_pca[:, 0],
            "PCA2": X_pca[:, 1],
            "Cluster": clusters
        })
        
        # Añadir nombre del comedor si está disponible
        if "NOMBRE_COMEDOR" in df.columns:
            df_pca["Comedor"] = df["NOMBRE_COMEDOR"].values
        
        resultados["pca_data"] = df_pca
        resultados["pca_varianza"] = pca.explained_variance_ratio_
        
        # Calcular perfiles de cada cluster
        perfiles = {}
        
        for cluster_id in range(n_clusters):
            # Filtrar datos de este cluster
            mask = clusters == cluster_id
            df_cluster = df_prep[mask]
            
            # Número de comedores en el cluster
            perfiles[cluster_id] = {
                "n_comedores": mask.sum()
            }
            
            # Promedios por dimensión
            promedios_dim = {}
            
            for dimension, preguntas in DIMENSIONES.items():
                pregs_existentes = [p for p in preguntas if p in df_prep.columns]
                
                if pregs_existentes:
                    promedio = df_cluster[pregs_existentes].mean(axis=1).mean()
                    promedios_dim[dimension] = promedio
            
            perfiles[cluster_id]["promedios_dimensiones"] = promedios_dim
            
            # Fortalezas (dimensiones con mayor puntuación)
            sorted_dims = sorted(promedios_dim.items(), key=lambda x: x[1], reverse=True)
            perfiles[cluster_id]["fortalezas"] = sorted_dims[:3]
            
            # Debilidades (dimensiones con menor puntuación)
            perfiles[cluster_id]["debilidades"] = sorted_dims[-3:]
            
            # Promedio general del cluster
            perfiles[cluster_id]["promedio_general"] = df_cluster[todas_preguntas].mean().mean()
            
            # Listado de comedores en el cluster
            if "NOMBRE_COMEDOR" in df.columns:
                perfiles[cluster_id]["comedores"] = df[mask]["NOMBRE_COMEDOR"].tolist()
        
        resultados["perfiles_clusters"] = perfiles
    
    return resultados

# 3.5 Análisis comparativo
def analisis_comparativo(df, df_prep):
    """
    Realiza un análisis comparativo por variables demográficas.
    
    Args:
        df (DataFrame): DataFrame original
        df_prep (DataFrame): DataFrame preparado con valores numéricos
        
    Returns:
        dict: Diccionario con los resultados del análisis
    """
    resultados = {}
    
    # Comparación por comuna
    if "COMUNA" in df.columns:
        comparacion_comuna = {}
        
        # Recopilar valores únicos de comuna
        comunas = df["COMUNA"].dropna().unique()
        
        for comuna in comunas:
            # Filtrar datos de esta comuna
            mask = df["COMUNA"] == comuna
            df_comuna = df_prep[mask]
            
            # Calcular promedios por dimensión
            promedios = {}
            
            for dimension, preguntas in DIMENSIONES.items():
                pregs_existentes = [p for p in preguntas if p in df_prep.columns]
                
                if pregs_existentes:
                    promedio = df_comuna[pregs_existentes].mean(axis=1).mean()
                    promedios[dimension] = promedio
            
            comparacion_comuna[comuna] = promedios
        
        # Convertir a DataFrame
        if comparacion_comuna:
            df_comp = pd.DataFrame(comparacion_comuna).T
            df_comp.index.name = "Comuna"
            
            resultados["comparacion_comunas"] = df_comp
    
    return resultados

# Función principal para ejecutar todos los análisis
def ejecutar_analisis_completo(df_datos, n_clusters=3):
    """
    Ejecuta el análisis completo del clima organizacional.
    
    Args:
        df_datos (DataFrame): DataFrame con los datos originales
        n_clusters (int): Número de clusters para el análisis
        
    Returns:
        dict: Diccionario con todos los resultados de los análisis
    """
    # Verificar que el DataFrame no está vacío
    if df_datos is None or df_datos.empty:
        return {"error": "No se pudieron cargar los datos"}
    
    # Preparar datos
    df_prep = preparar_datos(df_datos)
    
    # Ejecutar todos los análisis
    resultados = {
        "datos_originales": df_datos,
        "datos_preparados": df_prep
    }
    
    # 3.1 Análisis descriptivo básico
    resultados["descriptivo"] = analisis_descriptivo(df_datos, df_prep)
    
    # 3.2 Análisis por dimensiones
    resultados["dimensiones"] = analisis_por_dimensiones(df_prep)
    
    # 3.3 Análisis de correlaciones
    resultados["correlaciones"] = analisis_correlaciones(df_prep)
    
    # 3.4 Análisis de conglomerados
    resultados["clusters"] = analisis_clusters(df_datos, df_prep, n_clusters)
    
    # 3.5 Análisis comparativo
    resultados["comparativo"] = analisis_comparativo(df_datos, df_prep)
    
    return resultados

# Función para generar visualizaciones con Plotly
def generar_visualizaciones(resultados):
    """
    Genera visualizaciones interactivas a partir de los resultados de los análisis.
    
    Args:
        resultados (dict): Resultados de los análisis
        
    Returns:
        dict: Diccionario con figuras de Plotly
    """
    figuras = {}
    
    if "error" in resultados:
        return {"error": resultados["error"]}
    
    # Visualización 1: Distribución de respuestas
    if "descriptivo" in resultados and "distribucion_respuestas" in resultados["descriptivo"]:
        dist = resultados["descriptivo"]["distribucion_respuestas"]
        
        fig_dist = px.pie(
            dist,
            names="Respuesta",
            values="Cantidad",
            title="Distribución General de Respuestas",
            color="Respuesta",
            color_discrete_map={
                "DE ACUERDO": "#2ca02c",
                "NI DEACUERDO, NI EN DESACUERDO": "#ffbb78",
                "EN DESACUERDO": "#d62728"
            }
        )
        
        fig_dist.update_traces(textinfo="percent+label")
        figuras["distribucion_respuestas"] = fig_dist
    
    # Visualización 2: Distribución por comuna
    if "descriptivo" in resultados and "distribucion_comunas" in resultados["descriptivo"]:
        comunas = resultados["descriptivo"]["distribucion_comunas"]
        
        fig_comunas = px.bar(
            comunas,
            x="Comuna",
            y="Cantidad",
            title="Distribución de Comedores por Comuna",
            color="Cantidad",
            color_continuous_scale="Viridis"
        )
        
        fig_comunas.update_layout(xaxis_title="Comuna", yaxis_title="Número de Comedores")
        figuras["distribucion_comunas"] = fig_comunas
    
    # Visualización 3: Promedios por dimensión
    if "dimensiones" in resultados and "promedios_dimensiones" in resultados["dimensiones"]:
        promedios = resultados["dimensiones"]["promedios_dimensiones"]
        
        fig_promedios = px.bar(
            promedios,
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
        
        fig_promedios.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig_promedios.update_layout(
            xaxis_title="Dimensión",
            yaxis_title="Puntuación Promedio (1-3)",
            yaxis=dict(range=[0, 3.2])
        )
        
        figuras["promedios_dimensiones"] = fig_promedios
    
    # Visualización 4: Radar de dimensiones
    if "dimensiones" in resultados and "promedios_dimensiones" in resultados["dimensiones"]:
        promedios = resultados["dimensiones"]["promedios_dimensiones"]
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=promedios["Promedio"],
            theta=promedios["Dimensión"],
            fill="toself",
            name="Promedio"
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 3]
                )
            ),
            title="Perfil de Dimensiones del Clima Organizacional",
            showlegend=False
        )
        
        figuras["radar_dimensiones"] = fig_radar
    
    # Visualización 5:
    # Visualización 5: Matriz de correlación
    if "correlaciones" in resultados and "matriz_correlacion_corta" in resultados["correlaciones"]:
        corr_matrix = resultados["correlaciones"]["matriz_correlacion_corta"]
        
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Matriz de Correlación de Spearman"
        )
        
        fig_corr.update_layout(height=700, width=700)
        figuras["matriz_correlacion"] = fig_corr
    
    # Visualización 6: Clusters en PCA
    if "clusters" in resultados and "pca_data" in resultados["clusters"]:
        pca_data = resultados["clusters"]["pca_data"]
        n_clusters = resultados["clusters"]["n_clusters"]
        
        fig_clusters = px.scatter(
            pca_data,
            x="PCA1",
            y="PCA2",
            color="Cluster",
            hover_name="Comedor" if "Comedor" in pca_data.columns else None,
            title=f"Clusters de Comedores (PCA, {n_clusters} grupos)",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig_clusters.update_layout(height=600, legend_title="Cluster")
        figuras["clusters_pca"] = fig_clusters
    
    # Visualización 7: Perfiles de clusters
    if "clusters" in resultados and "perfiles_clusters" in resultados["clusters"]:
        perfiles = resultados["clusters"]["perfiles_clusters"]
        
        # Preparar datos para gráfico
        datos_perfiles = []
        
        for cluster_id, perfil in perfiles.items():
            for dimension, valor in perfil["promedios_dimensiones"].items():
                datos_perfiles.append({
                    "Cluster": f"Cluster {cluster_id}",
                    "Dimensión": dimension,
                    "Puntuación": valor
                })
        
        df_perfiles = pd.DataFrame(datos_perfiles)
        
        fig_perfiles = px.bar(
            df_perfiles,
            x="Dimensión",
            y="Puntuación",
            color="Cluster",
            barmode="group",
            title="Perfil de Clusters por Dimensión",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig_perfiles.update_layout(
            xaxis_title="Dimensión",
            yaxis_title="Puntuación Promedio (1-3)",
            yaxis=dict(range=[0, 3.2])
        )
        
        figuras["perfiles_clusters"] = fig_perfiles
    
    # Visualización 8: Comparación por comunas
    if "comparativo" in resultados and "comparacion_comunas" in resultados["comparativo"]:
        comp_comunas = resultados["comparativo"]["comparacion_comunas"]
        
        # Preparar datos para gráfico
        datos_comp = []
        
        for comuna, valores in comp_comunas.iterrows():
            for dimension, valor in valores.items():
                datos_comp.append({
                    "Comuna": f"Comuna {comuna}",
                    "Dimensión": dimension,
                    "Puntuación": valor
                })
        
        df_comp = pd.DataFrame(datos_comp)
        
        fig_comp = px.bar(
            df_comp,
            x="Dimensión",
            y="Puntuación",
            color="Comuna",
            barmode="group",
            title="Comparación por Comuna",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig_comp.update_layout(
            xaxis_title="Dimensión",
            yaxis_title="Puntuación Promedio (1-3)",
            yaxis=dict(range=[0, 3.2])
        )
        
        figuras["comparacion_comunas"] = fig_comp
    
    return figuras