import streamlit as st
import pandas as pd

from analisis_dior import interpretar_promedio

def mostrar_clusters(resultados, figuras, n_clusters):
    """
    Muestra la página de análisis de clusters (conglomerados).
    
    Args:
        resultados: Diccionario con los resultados del análisis
        figuras: Diccionario con las figuras generadas
        n_clusters: Número de clusters utilizado en el análisis
    """
    st.markdown('<div class="section-header">Análisis de Clusters</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    Este análisis agrupa los comedores en {n_clusters} clusters (grupos) según la similitud en sus respuestas.
    Cada cluster representa un perfil diferente de clima organizacional.
    """)
    
    # Visualización de clusters en PCA
    st.subheader("Visualización de Clusters")
    
    if "clusters_pca" in figuras:
        st.plotly_chart(figuras["clusters_pca"], use_container_width=True)
        
        # Agregar explicación sobre la visualización PCA
        st.markdown("""
        **¿Qué muestra este gráfico?**
        
        La visualización anterior utiliza el Análisis de Componentes Principales (PCA) para reducir 
        la dimensionalidad de los datos y mostrar en un espacio bidimensional cómo se agrupan los comedores.
        Puntos cercanos representan comedores con respuestas similares en la encuesta.
        
        Los colores diferentes indican los distintos clusters (grupos) identificados por el algoritmo,
        donde cada cluster representa un perfil de clima organizacional con características similares.
        """)
    
    # Detalles de cada cluster
    st.subheader("Detalles por Cluster")
    
    if "clusters" in resultados and "perfiles_clusters" in resultados["clusters"]:
        perfiles = resultados["clusters"]["perfiles_clusters"]
        
        for cluster_id, perfil in perfiles.items():
            with st.expander(f"Cluster {cluster_id} ({perfil['n_comedores']} comedores)"):
                mostrar_detalle_cluster(cluster_id, perfil)

def mostrar_detalle_cluster(cluster_id, perfil):
    """
    Muestra el detalle de un cluster específico.
    
    Args:
        cluster_id: ID del cluster
        perfil: Diccionario con información del perfil del cluster
    """
    # Mostrar lista de comedores en el cluster
    if "comedores" in perfil:
        st.markdown("#### Comedores en este cluster:")
        st.write(", ".join(perfil["comedores"]))
    
    # Mostrar promedios por dimensión
    st.markdown("#### Puntuaciones por dimensión:")
    
    promedios_dim = pd.DataFrame({
        "Dimensión": list(perfil["promedios_dimensiones"].keys()),
        "Puntuación": list(perfil["promedios_dimensiones"].values())
    })
    
    promedios_dim["Interpretación"] = promedios_dim["Puntuación"].apply(interpretar_promedio)
    promedios_dim = promedios_dim.sort_values("Puntuación", ascending=False)
    
    # Configurar columnas para mejor visualización
    st.dataframe(
        promedios_dim,
        column_config={
            "Dimensión": "Dimensión",
            "Puntuación": st.column_config.NumberColumn("Puntuación", format="%.2f"),
            "Interpretación": "Interpretación"
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Mostrar fortalezas y debilidades
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Fortalezas:")
        if "fortalezas" in perfil:
            for dim, valor in perfil["fortalezas"]:
                st.markdown(f"- **{dim}**: {valor:.2f}")
    
    with col2:
        st.markdown("#### Áreas de mejora:")
        if "debilidades" in perfil:
            for dim, valor in perfil["debilidades"]:
                st.markdown(f"- **{dim}**: {valor:.2f}")
    
    # Promedio general
    if "promedio_general" in perfil:
        promedio_general = perfil["promedio_general"]
        interpretacion = interpretar_promedio(promedio_general)
        
        # Decidir color según interpretación
        color = "#2ca02c" if interpretacion == "Favorable" else "#ffbb78" if interpretacion == "Neutral" else "#d62728"
        
        st.markdown(f"""
        <div style="background-color:#f0f2f6; padding:15px; border-radius:5px; margin-top:20px;">
            <p style="margin:0; font-size:16px;"><b>Promedio general del cluster:</b> 
            <span style="color:{color}; font-weight:bold; font-size:18px;">{promedio_general:.2f}</span> 
            <span style="color:{color}; font-weight:bold;">({interpretacion})</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Resumen del perfil
        st.markdown("#### Resumen del perfil")
        
        # Determinar tipo de perfil basado en puntuaciones
        cantidad_favorables = sum(1 for dim, valor in perfil["promedios_dimensiones"].items() if valor >= 2.5)
        cantidad_neutrales = sum(1 for dim, valor in perfil["promedios_dimensiones"].items() if 1.5 <= valor < 2.5)
        cantidad_desfavorables = sum(1 for dim, valor in perfil["promedios_dimensiones"].items() if valor < 1.5)
        
        total_dimensiones = len(perfil["promedios_dimensiones"])
        
        if cantidad_favorables >= total_dimensiones * 0.7:
            tipo_perfil = "Perfil Favorable"
            descripcion = "Este cluster muestra un clima organizacional generalmente positivo, con puntuaciones favorables en la mayoría de las dimensiones."
        elif cantidad_desfavorables >= total_dimensiones * 0.7:
            tipo_perfil = "Perfil Desfavorable"
            descripcion = "Este cluster muestra un clima organizacional con desafíos significativos, con puntuaciones desfavorables en la mayoría de las dimensiones."
        elif cantidad_favorables > cantidad_desfavorables:
            tipo_perfil = "Perfil Mixto (tendencia positiva)"
            descripcion = "Este cluster muestra un clima organizacional mixto con una tendencia hacia lo positivo, aunque existen áreas específicas que requieren atención."
        elif cantidad_desfavorables > cantidad_favorables:
            tipo_perfil = "Perfil Mixto (tendencia negativa)"
            descripcion = "Este cluster muestra un clima organizacional mixto con una tendencia hacia lo negativo, aunque existen algunas fortalezas que podrían aprovecharse."
        else:
            tipo_perfil = "Perfil Neutral"
            descripcion = "Este cluster muestra un clima organizacional principalmente neutral, sin tendencias marcadas ni positivas ni negativas."
        
        st.markdown(f"**{tipo_perfil}**")
        st.markdown(descripcion)
        
        # Recomendaciones específicas basadas en el tipo de perfil
        st.markdown("#### Recomendaciones")
        
        if "Favorable" in tipo_perfil:
            st.markdown("""
            - Mantener las prácticas que han conducido a estos resultados positivos
            - Documentar y compartir buenas prácticas con otros comedores
            - Enfocarse en las pocas áreas con oportunidad de mejora
            """)
        elif "Desfavorable" in tipo_perfil:
            st.markdown("""
            - Priorizar intervenciones en las dimensiones más críticas
            - Realizar entrevistas de seguimiento para identificar causas específicas
            - Considerar proyectos de acompañamiento intensivo
            """)
        else:
            st.markdown("""
            - Aprovechar las fortalezas identificadas como base para mejorar
            - Desarrollar planes específicos para las dimensiones con puntuación más baja
            - Realizar seguimiento periódico para verificar mejoras
            """)