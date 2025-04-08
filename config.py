# Configuración de la aplicación DIOR
import streamlit as st

# ID del libro de Google Sheets
SHEET_ID = "1r81JF53_v9HhtrPFFo6hXezD8UY-Ui-6J4xy1R4KuOQ"

# Nombres de las hojas en el libro
SHEET_NAMES = {
    "DIOR": "DIOR",  # Nombre de la hoja principal
}

# Nombre de la hoja principal (para facilitar las importaciones)
SHEET_NAME = "DIOR"

# Configuración de la interfaz
APP_TITLE = "DIOR Analyzer"
APP_ICON = "📊"
APP_LAYOUT = "wide"

# Temas de color para gráficos
COLOR_THEMES = {
    "primary": ["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c"],
    "sequential": "Blues",
    "diverging": "RdBu",
    "qualitative": "Set3"
}

# Mapeo de grupos de columnas 
GRUPOS_COLUMNAS = {
    "LIDERAZGO DE LA GESTORA PRINCIPAL": {
        "LIDERAZGO_GESTORA": "L",
        "OPORTUNIDADES_CRECIMIENTO": "M",
        "DECISIONES_LIDER": "N",
        "ESPACIOS_RETROALIMENTACION": "O",
        "RETROALIMENTACION_ADECUADA": "P",
        "FELICITACION_DEL_LIDER": "Q",
        "ACTIVIDADES_QUE_CORRESPONDEN": "R",
        "LIDER_GENERA_CONFIANZA": "S",
        "ARTICULA_ACTIVIDADES": "T"
    },
    "CONDICIONES GENERALES DEL COMEDOR": {
        "LIBERTAD_DE_EXPRESARSE": "U",
        "OPINION_EN_CUENTA": "V",
        "RECONOCIDOS_POR_LOGROS": "W",
        "HABILIDADES_RECONOCIDAS": "X",
        "TRABAJO_EN_EQUIPO": "Y",
        "RELACIONES_RESPETUOSAS": "Z",
        "RED_INTERNA_FORTALECIDA": "AA",
        "OBJETIVOS_COMEDOR": "AB",
        "ACTIVIDADES_RECREATIVAS": "AC",
        "ACTIVIDADES_FORMATIVAS": "AD"
    },
    "CONDICIONES DE LA LABOR SOCIAL": {
        "CAPACITACIONES": "AE",
        "LABOR_SOCIAL": "AF",
        "ORGULLOSO_DE_LABOR_SOCIAL": "AG",
        "IMPACTO_LABOR_SOCIAL": "AH",
        "FORTALECIDO_LABOR_SOCIAL": "AI",
        "APORTA_OBJETIVOS_CC": "AJ",
        "APORTA_POSITIVAMENTE": "AK"
    }
}

# Datos de ubicación
COLUMNAS_UBICACION = {
    "NOMBRE_COMEDOR": "F",
    "UBICACION": "G"
}

# Mapeo de respuestas a valores numéricos
MAPEO_RESPUESTAS = {
    "TOTALMENTE EN DESACUERDO": 1,
    "EN DESACUERDO": 2,
    "NI DE ACUERDO NI DESACUERDO": 3,
    "DE ACUERDO": 4,
    "TOTALMENTE DE ACUERDO": 5
}

# Estructura de columnas conocidas (para mapeo)
COLUMNS_MAP = {
    # Ubicación
    "NOMBRE_COMEDOR": "F",
    "UBICACION": "G",
    
    # Liderazgo de la Gestora Principal
    "LIDERAZGO_GESTORA": "L",
    "OPORTUNIDADES_CRECIMIENTO": "M",
    "DECISIONES_LIDER": "N",
    "ESPACIOS_RETROALIMENTACION": "O",
    "RETROALIMENTACION_ADECUADA": "P",
    "FELICITACION_DEL_LIDER": "Q",
    "ACTIVIDADES_QUE_CORRESPONDEN": "R",
    "LIDER_GENERA_CONFIANZA": "S",
    "ARTICULA_ACTIVIDADES": "T",
    
    # Condiciones Generales del Comedor
    "LIBERTAD_DE_EXPRESARSE": "U",
    "OPINION_EN_CUENTA": "V",
    "RECONOCIDOS_POR_LOGROS": "W",
    "HABILIDADES_RECONOCIDAS": "X",
    "TRABAJO_EN_EQUIPO": "Y",
    "RELACIONES_RESPETUOSAS": "Z",
    "RED_INTERNA_FORTALECIDA": "AA",
    "OBJETIVOS_COMEDOR": "AB",
    "ACTIVIDADES_RECREATIVAS": "AC",
    "ACTIVIDADES_FORMATIVAS": "AD",
    
    # Condiciones de la Labor Social
    "CAPACITACIONES": "AE",
    "LABOR_SOCIAL": "AF",
    "ORGULLOSO_DE_LABOR_SOCIAL": "AG",
    "IMPACTO_LABOR_SOCIAL": "AH",
    "FORTALECIDO_LABOR_SOCIAL": "AI",
    "APORTA_OBJETIVOS_CC": "AJ",
    "APORTA_POSITIVAMENTE": "AK"
}