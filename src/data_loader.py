import pandas as pd
import streamlit as st

def load_data(filepath):
    """
    Carga los datos del Excel de Yape, buscando dinámicamente la fila de encabezado.
    Retorna un DataFrame limpio con columnas estandarizadas.
    """
    try:
        # Paso 1: Leer las primeras filas para encontrar el encabezado
        df_temp = pd.read_excel(filepath, header=None, nrows=20)
        
        header_row = None
        for i, row in df_temp.iterrows():
            row_str = row.astype(str).str.lower()
            if row_str.str.contains('fecha de operación').any() or row_str.str.contains('tipo de transacción').any():
                header_row = i
                break
        
        if header_row is None:
            st.error("No se pudo encontrar la fila de encabezados en el Excel.")
            return None

        # Paso 2: Leer el Excel con el encabezado correcto
        df = pd.read_excel(filepath, header=header_row)

        # Paso 3: Limpieza básica
        # Eliminar filas vacías
        df = df.dropna(how='all')
        
        # Validar columnas esperadas
        expected_cols = ['Tipo de Transacción', 'Fecha de operación', 'Monto']
        missing_cols = [col for col in expected_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"Faltan columnas esperadas: {missing_cols}")
            return None

        # Paso 4: Conversiones de tipos
        
        # Convertir Fecha (asumiendo formato dd/mm/yyyy HH:MM:SS o similar)
        # Forzar a datetime, los errores se convierten en NaT
        df['Fecha de operación'] = pd.to_datetime(df['Fecha de operación'], dayfirst=True, errors='coerce')
        
        # Eliminar filas con fechas inválidas (pueden ser totales o basura al final)
        df = df.dropna(subset=['Fecha de operación'])

        # Extraer Hora y Día para análisis
        df['Hora'] = df['Fecha de operación'].dt.hour
        df['Fecha'] = df['Fecha de operación'].dt.date
        df['DiaSemana'] = df['Fecha de operación'].dt.day_name()
        
        # Segmentación por Rango Horario
        def get_time_range(hour):
            if 0 <= hour < 6: return 'Madrugada'
            elif 6 <= hour < 12: return 'Mañana'
            elif 12 <= hour < 18: return 'Tarde'
            else: return 'Noche'
            
        df['RangoHorario'] = df['Hora'].apply(get_time_range)

        # Convertir Monto a numérico (si viene con S/ o comas)
        # Si es string, quitar 'S/' y ','
        if df['Monto'].dtype == 'object':
            df['Monto'] = df['Monto'].astype(str).str.replace('S/', '', regex=False)
            df['Monto'] = df['Monto'].str.replace(',', '', regex=False)
            df['Monto'] = df['Monto'].str.strip()
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
        
        # Clasificar Tipo de Movimiento (Ingreso/Egreso)
        # Esto depende de los valores en "Tipo de Transacción". 
        # Típicos Yape: "Te yapearon" (Ingreso), "Yapeaste" (Egreso)
        # Vamos a normalizar una nueva columna 'TipoMovimiento'
        
        def clasificar_movimiento(tipo):
            tipo = str(tipo).lower()
            if any(x in tipo for x in ['te yapearon', 'recibiste', 'pago recibido', 'cobraste', 'yapeo recibido', 'te pagó', 'abono yape']):
                return 'Ingreso'
            elif any(x in tipo for x in ['yapeaste', 'enviaste', 'pago realizado', 'pagaste', 'pago']):
                return 'Egreso'
            return 'Otro'

        df['TipoMovimiento'] = df['Tipo de Transacción'].apply(clasificar_movimiento)

        return df

    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None
