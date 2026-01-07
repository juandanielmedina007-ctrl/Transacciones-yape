import pandas as pd
import numpy as np

def calculate_kpis(df):
    """
    Calcula KPIs principales: Total Recibido, Total Enviado, Balance, Cantidad de TXs.
    """
    # Filtrar ingresos y egresos
    ingresos = df[df['TipoMovimiento'] == 'Ingreso']
    egresos = df[df['TipoMovimiento'] == 'Egreso']
    
    total_recibido = ingresos['Monto'].sum()
    total_enviado = egresos['Monto'].sum()
    balance = total_recibido - total_enviado
    
    count_tx = len(df)
    
    return {
        'total_recibido': total_recibido,
        'total_enviado': total_enviado,
        'balance': balance,
        'count_tx': count_tx
    }

def get_busiest_hour(df):
    """
    Retorna la hora con más transacciones y la cantidad.
    """
    if df.empty:
        return 0, 0
    
    counts = df['Hora'].value_counts()
    if counts.empty:
        return 0, 0
        
    busiest_hour = counts.idxmax()
    count = counts.max()
    return busiest_hour, count

def get_busiest_day(df):
    """
    Retorna el día (fecha) con más transacciones.
    """
    if df.empty:
        return "N/A", 0
    counts = df['Fecha'].value_counts()
    return counts.idxmax(), counts.max()

def get_amount_stats(df):
    """
    Retorna estadísticas de montos: Max recibido, Max enviado, Promedio.
    """
    ingresos = df[df['TipoMovimiento'] == 'Ingreso']['Monto']
    egresos = df[df['TipoMovimiento'] == 'Egreso']['Monto']

    max_recibido = ingresos.max() if not ingresos.empty else 0
    max_enviado = egresos.max() if not egresos.empty else 0
    avg_monto = df['Monto'].mean() if not df.empty else 0
    
    return {
        'max_recibido': max_recibido,
        'max_enviado': max_enviado,
        'avg_monto': avg_monto
    }

def get_top_days_by_amount(df, n=5):
    """
    Retorna los N días con mayor volumen total de dinero movido (suma absoluta).
    """
    if df.empty:
        return pd.DataFrame()
    
    # Agrupar por fecha y sumar monto
    daily_sum = df.groupby('Fecha')['Monto'].sum().sort_values(ascending=False).head(n).reset_index()
    daily_sum.columns = ['Fecha', 'Monto Total']
    return daily_sum

def get_top_movements(df, tipo='Ingreso', n=5):
    """
    Retorna los N movimientos más altos de un tipo específico.
    """
    if df.empty:
        return pd.DataFrame()
    
    filtered = df[df['TipoMovimiento'] == tipo]
    top = filtered.nlargest(n, 'Monto')[['Fecha', 'Hora', 'Origen', 'Destino', 'Monto']]
    return top

def calculate_ratios(df):
    """
    Calcula % de Ingresos vs Egresos y Ratio Envio/Recepción.
    """
    kpis = calculate_kpis(df)
    total_recibido = kpis['total_recibido']
    total_enviado = kpis['total_enviado']
    total_movido = total_recibido + total_enviado
    
    if total_movido == 0:
        pct_ingreso = 0
        pct_egreso = 0
    else:
        pct_ingreso = (total_recibido / total_movido) * 100
        pct_egreso = (total_enviado / total_movido) * 100
        
    # Ratio: Por cada sol recibido, cuántos envío
    ratio_egreso_ingreso = total_enviado / total_recibido if total_recibido > 0 else 0
    
    return {
        'pct_ingreso': pct_ingreso,
        'pct_egreso': pct_egreso,
        'ratio': ratio_egreso_ingreso,
        'total_movido': total_movido
    }

def get_alerts(df, custom_threshold=None):
    """
    Genera alertas basadas en reglas de negocio (montos altos, picos de frecuencia).
    """
    alerts = []
    
    if df.empty:
        return alerts

    # 1. Alerta de Montos Altos (Outliers)
    if custom_threshold is not None:
        threshold_high = custom_threshold
    else:
        # Usamos percentil 95 como umbral dinámico, pero con un piso mínimo de 50 soles
        threshold_high = df['Monto'].quantile(0.95)
        if threshold_high < 50: threshold_high = 50
    
    high_tx = df[df['Monto'] > threshold_high].sort_values(by='Monto', ascending=False)
    
    if not high_tx.empty:
        alerts.append({
            'type': 'high_amount',
            'title': '🚨 Operaciones de Alto Valor',
            'message': f"Se detectaron {len(high_tx)} operaciones por encima de S/ {threshold_high:.2f}",
            'data': high_tx[['Fecha', 'Hora', 'TipoMovimiento', 'Monto', 'Origen', 'Destino']]
        })

    # 2. Alerta de Frecuencia Inusual (Picos por Hora)
    # Agrupar por Fecha y Hora para ver cuántas txs ocurren en una misma hora
    hourly_counts = df.groupby(['Fecha', 'Hora']).size().reset_index(name='count')
    
    # Umbral: si hay más de 5 ops en una hora (ajustable)
    peak_threshold = 5
    abnormal_peaks = hourly_counts[hourly_counts['count'] > peak_threshold].sort_values(by='count', ascending=False)
    
    if not abnormal_peaks.empty:
        alerts.append({
            'type': 'frequency_peak',
            'title': '⚠️ Picos de Actividad Inusual',
            'message': f"Hubo {len(abnormal_peaks)} momentos con alto tráfico (> {peak_threshold} transacciones/hora).",
            'data': abnormal_peaks
        })
        
    return alerts
