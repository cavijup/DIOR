import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
import os
import json
from config import SHEET_ID, SHEET_NAME

@st.cache_resource(ttl=3600)
def connect_to_gsheets():
    """
    Establece conexión con Google Sheets utilizando credenciales locales.
    
    Returns:
        client: Cliente autorizado de gspread o None si hay error
    """
    try:
        # Ruta al archivo de credenciales local
        credentials_path = "credentials.json"
        
        # Verificar si el archivo existe
        if os.path.exists(credentials_path):
            scopes = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            
            creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
            client = gspread.authorize(creds)
            return client
        else:
            st.error("No se encontró el archivo de credenciales. Por favor, crea un archivo 'credentials.json' con las credenciales del servicio.")
            return None
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return None

@st.cache_data(ttl=300)
def load_data():
    """
    Carga datos de la hoja DIOR de Google Sheets.
    
    Returns:
        DataFrame con los datos o None si hay error
    """
    try:
        client = connect_to_gsheets()
        if client:
            # Abrir la hoja por ID
            sheet = client.open_by_key(SHEET_ID)
            
            # Obtener la hoja específica
            worksheet = sheet.worksheet(SHEET_NAME)
            
            # Obtener todos los valores
            values = worksheet.get_values()
            
            if not values:
                st.error(f"No se encontraron datos en la hoja {SHEET_NAME}.")
                return None
            
            # La primera fila contiene los encabezados
            headers = values[0]
            
            # Filtrar filas vacías
            data_rows = []
            for row in values[1:]:
                # Extender la fila si es más corta que los encabezados
                extended_row = row + [''] * (len(headers) - len(row))
                
                # Verificar si la fila tiene al menos un valor no vacío
                if any(cell.strip() for cell in extended_row):
                    data_rows.append(extended_row)
            
            # Crear DataFrame
            df = pd.DataFrame(data_rows, columns=headers)
            
            # Limpiar datos básicos
            df = clean_dataframe(df)
            
            return df
        else:
            st.error("No se pudo conectar con Google Sheets")
            return None
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None

def clean_dataframe(df):
    """
    Realiza una limpieza básica del DataFrame preservando el tipo de datos original.
    
    Args:
        df: DataFrame a limpiar
    
    Returns:
        DataFrame limpio
    """
    # Eliminar espacios en blanco de los encabezados
    df.columns = [col.strip() for col in df.columns]
    
    # Eliminar filas completamente vacías
    df = df.dropna(how='all')
    
    # Intentar identificar solo columnas que deberían ser numéricas
    # Por ejemplo, columnas que empiezan con números o contienen solo dígitos
    for col in df.columns:
        # Verificar si la mayoría de los valores no vacíos son numéricos
        non_empty_values = df[col].dropna()
        if len(non_empty_values) > 0:
            # Intentar convertir a numérico y contar éxitos
            numeric_count = sum(pd.to_numeric(non_empty_values, errors='coerce').notna())
            
            # Si más del 80% de los valores son numéricos, convertir la columna
            if numeric_count / len(non_empty_values) > 0.8:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df