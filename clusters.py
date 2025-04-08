import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.express as px

# Importar constantes y funciones de utilidad
try:
    from config import GRUPOS_COLUMNAS, COLUMNAS_UBICACION, MAPEO_RESPUESTAS
    from utils import obtener_letra_a_indice, interpretar_promedio
except ImportError as e:
    st.error(f"Error al importar módulos: {e}. Asegúrate de que 'config.py' y 'utils.py' estén en el mismo directorio.")
    st.stop()

def preparar_dataframe(df):
    """
    Prepara el DataFrame para el análisis, mapeando valores de respuesta a números.
    """
    df_analisis = df.copy()
    for grupo, columnas in GRUPOS_COLUMNAS.items():
        for nombre_col, letra_col in columnas.items():
            if nombre_col in df_analisis.columns:
                df_analisis[nombre_col] = df_analisis[nombre_col].map(MAPEO_RESPUESTAS).fillna(0).astype(int)
            else:
                indice = obtener_letra_a_indice(letra_col)
                if indice >= 0 and indice < len(df_analisis.columns):
                    col_actual = df_analisis.columns[indice]
                    df_analisis[col_actual] = df_analisis[col_actual].map(MAPEO_RESPUESTAS).fillna(0).astype(int)
                    df_analisis.rename(columns={col_actual: nombre_col}, inplace=True)
    return df_analisis

def mostrar_analisis_clusters(df):
    """
    Muestra el análisis de clustering para los comedores con control de visibilidad.
    """
    if df is None or df.empty:
        st.error("No hay datos para analizar.")
        return

    st.header("Análisis de Conglomerados (Clustering)")

    df_analisis = preparar_dataframe(df)

    columna_comedor = None
    for nombre, letra in COLUMNAS_UBICACION.items():
        if nombre == "NOMBRE_COMEDOR":
            indice = obtener_letra_a_indice(letra)
            if indice < len(df.columns):
                columna_comedor = df.columns[indice]
                break

    if columna_comedor is None or columna_comedor not in df.columns:
        st.warning("No se encontró la columna para NOMBRE_COMEDOR. Se usará el índice como identificador.")
        df_analisis['COMEDOR_ID'] = [f"Comedor {i+1}" for i in range(len(df_analisis))]
        columna_comedor = 'COMEDOR_ID'

    columnas_por_grupo = {}
    todas_columnas = []

    for grupo, columnas in GRUPOS_COLUMNAS.items():
        columnas_en_este_grupo = []
        for nombre_col, letra_col in columnas.items():
            if nombre_col in df_analisis.columns:
                columnas_en_este_grupo.append(nombre_col)
                todas_columnas.append(nombre_col)
            else:
                indice = obtener_letra_a_indice(letra_col)
                if indice >= 0 and indice < len(df_analisis.columns):
                    col_actual = df_analisis.columns[indice]
                    columnas_en_este_grupo.append(col_actual)
                    todas_columnas.append(col_actual)
        if columnas_en_este_grupo:
            columnas_por_grupo[grupo] = columnas_en_este_grupo

    if not todas_columnas:
        st.error("No se encontraron columnas de encuesta para analizar.")
        return

    X = df_analisis[todas_columnas].fillna(0)

    try:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        st.subheader("Determinación del número óptimo de clusters")
        show_elbow_chart = st.checkbox("Mostrar gráfico del Método del Codo", value=False) # Oculto por defecto

        max_clusters = min(10, len(df_analisis) - 1)
        if max_clusters < 2:
            st.error("No hay suficientes datos para realizar clustering (mínimo 3 observaciones).")
            return

        inertias = []
        K_range = range(1, max_clusters + 1)

        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_scaled)
            inertias.append(kmeans.inertia_)

        fig_elbow = px.line(
            x=list(K_range),
            y=inertias,
            markers=True,
            title="Método del Codo para determinar el número óptimo de clusters",
            labels={"x": "Número de clusters", "y": "Inercia"}
        )

        if show_elbow_chart:
            st.plotly_chart(fig_elbow, use_container_width=True)

        show_slider = st.checkbox("Seleccionar número de clusters", value=False) # Botón para el slider
        n_clusters = 3 # Valor por defecto si el slider está oculto

        if show_slider:
            st.write("Seleccione el número de clusters basado en el 'codo' del gráfico anterior.")
            n_clusters = st.slider("Número de clusters", min_value=2, max_value=max_clusters, value=3)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)

        df_clustered = df_analisis.copy()
        df_clustered['Cluster'] = clusters

        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        explained_variance = pca.explained_variance_ratio_ * 100

        df_plot = pd.DataFrame({
            f'Componente Principal 1 ({explained_variance[0]:.1f}%)': X_pca[:, 0],
            f'Componente Principal 2 ({explained_variance[1]:.1f}%)': X_pca[:, 1],
            'Cluster': clusters,
            'Comedor': df_analisis[columna_comedor].values
        })

        st.subheader(f"Visualización de {n_clusters} clusters")

        fig_clusters = px.scatter(
            df_plot,
            x=f'Componente Principal 1 ({explained_variance[0]:.1f}%)',
            y=f'Componente Principal 2 ({explained_variance[1]:.1f}%)',
            color='Cluster',
            symbol='Cluster',
            hover_name='Comedor',
            title=f"Clusters de Comedores (PCA)",
            color_discrete_sequence=px.colors.qualitative.Bold
        )

        fig_clusters.update_layout(
            height=600,
            legend_title="Cluster",
            font=dict(size=12)
        )

        st.plotly_chart(fig_clusters, use_container_width=True)

        st.subheader("Análisis Detallado por Cluster")
        show_tables = st.checkbox("Mostrar Tablas de Valores Promedio por Cluster", value=False) # Oculto por defecto

        if show_tables:
            st.subheader("Tabla de Valores Promedio por Cluster")
            st.write("""
            Esta tabla muestra el valor promedio de cada variable para cada cluster identificado.
            Esto te ayudará a entender qué características definen a cada grupo de comedores.
            """)

            promedios_por_cluster = {}
            for grupo, cols in columnas_por_grupo.items():
                df_promedios_grupo = pd.DataFrame()
                for cluster_id in range(n_clusters):
                    df_cluster = df_clustered[df_clustered['Cluster'] == cluster_id]
                    promedios = df_cluster[cols].mean().round(2)
                    df_promedios_grupo[f'Cluster {cluster_id}'] = promedios
                promedios_por_cluster[grupo] = df_promedios_grupo

            for grupo, df_promedios in promedios_por_cluster.items():
                st.write(f"### {grupo}")
                df_display = df_promedios.reset_index()
                df_display.rename(columns={'index': 'Variable'}, inplace=True)
                df_display['Variable'] = df_display['Variable'].apply(lambda x: x.replace('_', ' ').title())
                for cluster_id in range(n_clusters):
                    col_name = f'Cluster {cluster_id}'
                    interpretacion_col = f'Interpretación Cluster {cluster_id}'
                    df_display[interpretacion_col] = df_display[col_name].apply(interpretar_promedio)
                st.dataframe(df_display, use_container_width=True)

        st.subheader("Resumen de Características por Cluster")
        resumen_clusters = []
        for cluster_id in range(n_clusters):
            df_cluster = df_clustered[df_clustered['Cluster'] == cluster_id]
            count = len(df_cluster)
            promedios = df_cluster[todas_columnas].mean()
            top_vars = promedios.nlargest(3).index.tolist()
            top_vals = promedios.nlargest(3).values.round(2).tolist()
            bottom_vars = promedios.nsmallest(3).index.tolist()
            bottom_vals = promedios.nsmallest(3).values.round(2).tolist()
            top_vars = [v.replace('_', ' ').title() for v in top_vars]
            bottom_vars = [v.replace('_', ' ').title() for v in bottom_vars]
            resumen = {
                'Cluster': f'Cluster {cluster_id}',
                'Número de Comedores': count,
                'Fortalezas (Valores Más Altos)': f"{top_vars[0]} ({top_vals[0]}), {top_vars[1]} ({top_vals[1]}), {top_vars[2]} ({top_vals[2]})",
                'Oportunidades (Valores Más Bajos)': f"{bottom_vars[0]} ({bottom_vals[0]}), {bottom_vars[1]} ({bottom_vals[1]}), {bottom_vars[2]} ({bottom_vals[2]})"
            }
            resumen_clusters.append(resumen)
        st.dataframe(pd.DataFrame(resumen_clusters), use_container_width=True)

        st.subheader("Comedores en cada Cluster")
        for cluster_id in range(n_clusters):
            df_cluster = df_clustered[df_clustered['Cluster'] == cluster_id]
            with st.expander(f"Cluster {cluster_id} ({len(df_cluster)} comedores)"):
                st.write(", ".join(df_cluster[columna_comedor].tolist()))

    except Exception as e:
        st.error(f"Error al realizar el análisis de clusters: {str(e)}")
        st.code(str(e))

if __name__ == '__main__':
    # Ejemplo de cómo usar la función con un DataFrame de ejemplo
    data = {
        'NOMBRE_COMEDOR': ['Comedor A', 'Comedor B', 'Comedor C', 'Comedor D', 'Comedor E', 'Comedor F'],
        'P1_1': ['A', 'B', 'A', 'C', 'B', 'A'],
        'P1_2': ['B', 'C', 'B', 'A', 'C', 'B'],
        'P2_1': ['C', 'A', 'C', 'B', 'A', 'C'],
        'P2_2': ['A', 'B', 'A', 'C', 'B', 'A'],
        'Ubicacion_Latitud': [1.0, 2.0, 1.5, 2.5, 1.2, 2.2],
        'Ubicacion_Longitud': [-76.0, -75.5, -76.2, -75.8, -76.1, -75.6]
    }
    df_ejemplo = pd.DataFrame(data)

    # Definir las constantes necesarias (simulando los archivos config.py y utils.py)
    GRUPOS_COLUMNAS = {
        'Preguntas Parte 1': {'P1_1': 'A', 'P1_2': 'B'},
        'Preguntas Parte 2': {'P2_1': 'C', 'P2_2': 'D'}
    }
    COLUMNAS_UBICACION = {'NOMBRE_COMEDOR': 'NOMBRE_COMEDOR'}
    MAPEO_RESPUESTAS = {'A': 1, 'B': 2, 'C': 3, 'D': 4}

    def obtener_letra_a_indice(letra):
        return ord(letra.upper()) - ord('A')

    def interpretar_promedio(promedio):
        if promedio <= 1.5:
            return "Bajo"
        elif promedio <= 2.5:
            return "Medio"
        else:
            return "Alto"

    globals()['obtener_letra_a_indice'] = obtener_letra_a_indice
    globals()['interpretar_promedio'] = interpretar_promedio

    mostrar_analisis_clusters(df_ejemplo)