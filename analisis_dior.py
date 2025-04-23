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

# Función para generar visualizaciones con Plotly (modificada)
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
    
    return figuras
def analisis_liderazgo_por_rol(df_prep):
    """
    Realiza un análisis comparativo de percepción de liderazgo entre gestores principales y auxiliares.
    
    Args:
        df_prep (DataFrame): DataFrame preparado con valores numéricos
        
    Returns:
        dict: Diccionario con los resultados del análisis
    """
    resultados = {}
    
    # Verificar que existen las columnas necesarias
    columnas_requeridas = [
        "ROL", 
        "NOMBRE_COMEDOR", 
        "2.1_LIDERAZGO_RESPESTUOSO", 
        "2.2_OPORTUNIDAD_DE_PROPONER_IDEAS", 
        "2.3_ESPACIOS_ADECUADOS_RETROALIMENTACION"
    ]
    
    if not all(col in df_prep.columns for col in columnas_requeridas):
        missing_columns = [col for col in columnas_requeridas if col not in df_prep.columns]
        return {"error": f"Faltan columnas requeridas: {', '.join(missing_columns)}"}
    
    # Filtrar solo las filas que tienen un rol definido
    df_con_rol = df_prep[df_prep["ROL"].notna()]
    
    # Normalizar los valores de rol para manejar posibles variaciones en el texto
    df_con_rol["ROL_NORMALIZADO"] = df_con_rol["ROL"].str.strip().str.upper()
    
    # Definir los roles a comparar
    rol_principal = "GESTORA/OR PRINCIPAL"
    rol_auxiliar = "GESTORA/OR  AUXILIAR"
    
    # Identificar comedores que tienen ambos roles para comparar
    comedores_principales = set(df_con_rol[df_con_rol["ROL_NORMALIZADO"].str.contains(rol_principal)]["NOMBRE_COMEDOR"])
    comedores_auxiliares = set(df_con_rol[df_con_rol["ROL_NORMALIZADO"].str.contains(rol_auxiliar)]["NOMBRE_COMEDOR"])
    comedores_ambos_roles = comedores_principales.intersection(comedores_auxiliares)
    
    resultados["total_comedores"] = len(set(df_con_rol["NOMBRE_COMEDOR"]))
    resultados["comedores_con_principal"] = len(comedores_principales)
    resultados["comedores_con_auxiliar"] = len(comedores_auxiliares)
    resultados["comedores_con_ambos_roles"] = len(comedores_ambos_roles)
    
    # Análisis por pregunta de liderazgo
    preguntas_liderazgo = [
        "2.1_LIDERAZGO_RESPESTUOSO", 
        "2.2_OPORTUNIDAD_DE_PROPONER_IDEAS", 
        "2.3_ESPACIOS_ADECUADOS_RETROALIMENTACION"
    ]
    
    # Análisis global (todos los comedores)
    analisis_global = {}
    for pregunta in preguntas_liderazgo:
        # Obtener promedios por rol
        promedio_principal = df_con_rol[df_con_rol["ROL_NORMALIZADO"].str.contains(rol_principal)][pregunta].mean()
        promedio_auxiliar = df_con_rol[df_con_rol["ROL_NORMALIZADO"].str.contains(rol_auxiliar)][pregunta].mean()
        
        # Calcular diferencia
        diferencia = promedio_principal - promedio_auxiliar
        
        analisis_global[pregunta] = {
            "promedio_principal": promedio_principal,
            "promedio_auxiliar": promedio_auxiliar,
            "diferencia": diferencia,
            "diferencia_abs": abs(diferencia)
        }
    
    resultados["analisis_global"] = analisis_global
    
    # Análisis por comedor (solo para comedores que tienen ambos roles)
    analisis_comedores = {}
    
    for comedor in comedores_ambos_roles:
        # Filtrar datos de este comedor
        df_comedor = df_con_rol[df_con_rol["NOMBRE_COMEDOR"] == comedor]
        
        # Datos de gestores principales de este comedor
        df_principal = df_comedor[df_comedor["ROL_NORMALIZADO"].str.contains(rol_principal)]
        
        # Datos de gestores auxiliares de este comedor
        df_auxiliar = df_comedor[df_comedor["ROL_NORMALIZADO"].str.contains(rol_auxiliar)]
        
        # Análisis por pregunta para este comedor
        analisis_comedor = {}
        
        for pregunta in preguntas_liderazgo:
            # Obtener valores para cada rol (puede haber múltiples gestores por rol)
            valores_principal = df_principal[pregunta].tolist()
            valores_auxiliar = df_auxiliar[pregunta].tolist()
            
            # Calcular promedios
            promedio_principal = df_principal[pregunta].mean()
            promedio_auxiliar = df_auxiliar[pregunta].mean()
            
            # Calcular diferencia
            diferencia = promedio_principal - promedio_auxiliar
            
            # Calcular concordancia (qué tan similares son las respuestas)
            concordancia = "Alta" if abs(diferencia) <= 0.5 else "Media" if abs(diferencia) <= 1 else "Baja"
            
            analisis_comedor[pregunta] = {
                "valores_principal": valores_principal,
                "valores_auxiliar": valores_auxiliar,
                "promedio_principal": promedio_principal,
                "promedio_auxiliar": promedio_auxiliar,
                "diferencia": diferencia,
                "diferencia_abs": abs(diferencia),
                "concordancia": concordancia
            }
        
        # Calcular indicadores globales para este comedor
        diferencias = [analisis_comedor[pregunta]["diferencia_abs"] for pregunta in preguntas_liderazgo]
        concordancia_global = "Alta" if all(d <= 0.5 for d in diferencias) else "Media" if all(d <= 1 for d in diferencias) else "Baja"
        
        analisis_comedores[comedor] = {
            "analisis_preguntas": analisis_comedor,
            "diferencia_promedio": sum(diferencias) / len(diferencias),
            "concordancia_global": concordancia_global
        }
    
    resultados["analisis_comedores"] = analisis_comedores
    
    # Crear resumen de concordancia
    resumen_concordancia = {
        "Alta": 0,
        "Media": 0,
        "Baja": 0
    }
    
    for comedor, analisis in analisis_comedores.items():
        concordancia = analisis["concordancia_global"]
        resumen_concordancia[concordancia] += 1
    
    resultados["resumen_concordancia"] = resumen_concordancia
    
    return resultados
# Función para generar visualizaciones para el análisis de liderazgo por rol
def generar_visualizaciones_liderazgo_por_rol(resultados_liderazgo):
    """
    Genera visualizaciones para el análisis de liderazgo por rol.
    
    Args:
        resultados_liderazgo (dict): Resultados del análisis de liderazgo por rol
        
    Returns:
        dict: Diccionario con figuras de Plotly
    """
    
    figuras = {}
    
    if "error" in resultados_liderazgo:
        return {"error": resultados_liderazgo["error"]}
    
    # 1. Comparación global de promedios por pregunta y rol
    if "analisis_global" in resultados_liderazgo:
        analisis_global = resultados_liderazgo["analisis_global"]
        
        # Preparar datos para el gráfico
        preguntas = []
        promedios_principal = []
        promedios_auxiliar = []
        diferencias = []
        
        # Mapeo para etiquetas más legibles
        mapeo_etiquetas = {
            "2.1_LIDERAZGO_RESPESTUOSO": "Liderazgo\nRespetuoso",
            "2.2_OPORTUNIDAD_DE_PROPONER_IDEAS": "Oportunidad de\nProponer Ideas",
            "2.3_ESPACIOS_ADECUADOS_RETROALIMENTACION": "Espacios para\nRetroalimentación"
        }
        
        for pregunta, datos in analisis_global.items():
            preguntas.append(mapeo_etiquetas.get(pregunta, pregunta))
            promedios_principal.append(datos["promedio_principal"])
            promedios_auxiliar.append(datos["promedio_auxiliar"])
            diferencias.append(datos["diferencia"])
        
        # Crear DataFrame para gráfico de barras agrupadas
        df_barras = pd.DataFrame({
            "Pregunta": preguntas * 2,
            "Rol": ["Principal"] * len(preguntas) + ["Auxiliar"] * len(preguntas),
            "Promedio": promedios_principal + promedios_auxiliar
        })
        
        # Gráfico de barras agrupadas
        fig_barras = px.bar(
            df_barras,
            x="Pregunta",
            y="Promedio",
            color="Rol",
            barmode="group",
            title="Comparación de Percepción de Liderazgo por Rol",
            color_discrete_map={"Principal": "#1f77b4", "Auxiliar": "#ff7f0e"},
            text_auto=".2f"
        )
        
        fig_barras.update_layout(
            xaxis_title="Pregunta de Liderazgo",
            yaxis_title="Puntuación Promedio (1-3)",
            yaxis=dict(range=[0, 3.2]),
            legend_title="Rol"
        )
        
        figuras["comparacion_global"] = fig_barras
        
        # Gráfico de diferencias
        df_dif = pd.DataFrame({
            "Pregunta": preguntas,
            "Diferencia": diferencias
        })
        
        fig_dif = px.bar(
            df_dif,
            x="Pregunta",
            y="Diferencia",
            title="Diferencia de Percepción entre Roles (Principal - Auxiliar)",
            color="Diferencia",
            color_continuous_scale="RdBu",
            text_auto=".2f"
        )
        
        fig_dif.update_layout(
            xaxis_title="Pregunta de Liderazgo",
            yaxis_title="Diferencia en Puntuación"
        )
        
        figuras["diferencias_global"] = fig_dif
    
    # 2. Distribución de concordancia entre comedores
    if "resumen_concordancia" in resultados_liderazgo:
        resumen = resultados_liderazgo["resumen_concordancia"]
        
        df_concordancia = pd.DataFrame({
            "Nivel de Concordancia": list(resumen.keys()),
            "Cantidad de Comedores": list(resumen.values())
        })
        
        # Ordenar por nivel de concordancia (Alta, Media, Baja)
        orden_concordancia = ["Alta", "Media", "Baja"]
        df_concordancia["Orden"] = df_concordancia["Nivel de Concordancia"].map({
            nivel: i for i, nivel in enumerate(orden_concordancia)
        })
        df_concordancia = df_concordancia.sort_values("Orden")
        
        colores_concordancia = {
            "Alta": "#2ca02c",   # Verde
            "Media": "#ffbb78",  # Naranja
            "Baja": "#d62728"    # Rojo
        }
        
        fig_conc = px.pie(
            df_concordancia,
            names="Nivel de Concordancia",
            values="Cantidad de Comedores",
            title="Distribución de Concordancia entre Roles por Comedor",
            color="Nivel de Concordancia",
            color_discrete_map=colores_concordancia
        )
        
        fig_conc.update_traces(textinfo="percent+label+value")
        
        figuras["distribucion_concordancia"] = fig_conc
    
    # 3. Detalle por comedor (si hay más de 5 comedores, mostrar solo top 5 con mayor diferencia)
    if "analisis_comedores" in resultados_liderazgo:
        analisis_comedores = resultados_liderazgo["analisis_comedores"]
        
        if analisis_comedores:
            # Ordenar comedores por diferencia promedio (de mayor a menor)
            comedores_ordenados = sorted(
                analisis_comedores.items(),
                key=lambda x: x[1]["diferencia_promedio"],
                reverse=True
            )
            
            # Limitar a 10 comedores para el gráfico
            top_comedores = comedores_ordenados[:10]
            
            # Datos para el gráfico
            nombres_comedores = []
            diferencias_promedio = []
            
            for comedor, datos in top_comedores:
                nombres_comedores.append(comedor)
                diferencias_promedio.append(datos["diferencia_promedio"])
            
            df_top = pd.DataFrame({
                "Comedor": nombres_comedores,
                "Diferencia Promedio": diferencias_promedio
            })
            
            # Truncar nombres muy largos
            df_top["Comedor"] = df_top["Comedor"].apply(lambda x: x[:25] + "..." if len(x) > 25 else x)
            
            fig_top = px.bar(
                df_top,
                x="Diferencia Promedio",
                y="Comedor",
                orientation="h",
                title="Top Comedores con Mayor Diferencia de Percepción entre Roles",
                color="Diferencia Promedio",
                color_continuous_scale="Reds",
                text_auto=".2f"
            )
            
            fig_top.update_layout(
                xaxis_title="Diferencia Promedio en Puntuación",
                yaxis_title="",
                yaxis=dict(autorange="reversed")  # Para ordenar de mayor a menor
            )
            
            figuras["top_comedores_diferencia"] = fig_top
    
    return figuras


