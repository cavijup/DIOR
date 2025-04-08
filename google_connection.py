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
    Establece conexión con Google Sheets utilizando credenciales.
    
    Returns:
        client: Cliente autorizado de gspread o None si hay error
    """
    try:
        # Intenta primero con credenciales desde secrets (para despliegue)
        if "gcp_credentials" in st.secrets:
            credentials_dict = st.secrets["gcp_credentials"]
            scopes = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            
            creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
            client = gspread.authorize(creds)
            return client
        # Si no hay secrets, intenta con archivo local (para desarrollo)
        else:
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
                st.error("No se encontró el archivo de credenciales. Por favor, crea un archivo 'credentials.json' con las credenciales del servicio o configura los secretos en Streamlit.")
                return None
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return None