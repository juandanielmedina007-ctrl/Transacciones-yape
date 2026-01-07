import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

def plot_transactions_per_hour(df):
    """
    Genera un gráfico de barras de transacciones por hora.
    """
    if df.empty:
        return None
        
    counts = df['Hora'].value_counts().sort_index().reset_index()
    counts.columns = ['Hora', 'Transacciones']
    
    fig = px.bar(
        counts, 
        x='Hora', 
        y='Transacciones',
        title='Distribución Horaria',
        labels={'Hora': 'Hora del día (0-23)', 'Transacciones': 'Cantidad'},
        template='plotly_white',
        color_discrete_sequence=['#FFC107']
    )
    fig.update_xaxes(tickmode='linear', dtick=1)
    return fig

def plot_daily_evolution(df):
    """
    Gráfico de línea mostrando evolución de montos (Ingreso vs Egreso) por día.
    """
    if df.empty:
        return None

    daily = df.groupby(['Fecha', 'TipoMovimiento'])['Monto'].sum().reset_index()
    
    fig = px.line(
        daily, 
        x='Fecha', 
        y='Monto', 
        color='TipoMovimiento',
        title='Evolución Diaria del Dinero',
        color_discrete_map={'Ingreso': '#28a745', 'Egreso': '#dc3545', 'Otro': '#6c757d'},
        template='plotly_white'
    )
    return fig

def plot_transactions_by_day_of_week(df):
    """
    Barras de transacciones por día de la semana.
    """
    if df.empty:
        return None
        
    order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    order_map = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    
    df['DiaSemanaES'] = df['DiaSemana'].map(order_map)
    order_es = [order_map[d] for d in order]
    
    counts = df['DiaSemanaES'].value_counts().reindex(order_es).reset_index()
    counts.columns = ['Día', 'Transacciones']
    
    fig = px.bar(
        counts,
        x='Día',
        y='Transacciones',
        title='Transacciones por Día de Semana',
        template='plotly_white',
        color_discrete_sequence=['#17a2b8']
    )
    return fig

def plot_time_range_distribution(df):
    """
    Donut chart o barras de distribución por Rango Horario.
    """
    if df.empty:
        return None
        
    counts = df['RangoHorario'].value_counts().reset_index()
    counts.columns = ['Rango', 'Cantidad']
    
    fig = px.pie(
        counts, 
        names='Rango', 
        values='Cantidad', 
        title='Distribución por Momento del Día',
        hole=0.4,
        color='Rango',
        color_discrete_map={
            'Mañana': '#ffc107', 
            'Tarde': '#fd7e14', 
            'Noche': '#343a40', 
            'Madrugada': '#6f42c1'
        }
    )
    return fig

def plot_amount_distribution(df):
    """
    Histograma y Boxplot de montos.
    """
    if df.empty:
        return None
    
    fig = px.box(
        df, 
        x='TipoMovimiento', 
        y='Monto', 
        points="all",
        title='Distribución de Montos (Boxplot)',
        color='TipoMovimiento',
        color_discrete_map={'Ingreso': '#28a745', 'Egreso': '#dc3545', 'Otro': '#6c757d'},
        template='plotly_white'
    )
    return fig

def plot_top_days_bar(df_top):
    """
    Barras horizontales de Top Días.
    """
    if df_top.empty:
        return None
        
    fig = px.bar(
        df_top,
        x='Monto Total',
        y='Fecha',
        orientation='h',
        title='Top Días con Mayor Movimiento de Dinero',
        template='plotly_white',
        text_auto='.2s',
        color='Monto Total',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(yaxis=dict(type='category'))
    return fig

def plot_income_expense_comparison(df):
    """
    Gráfico de barras agrupadas comparando Total Ingresos vs Egresos (Una sola barra comparativa).
    O Pie Chart de distribución del flujo.
    """
    if df.empty:
        return None

    # Agrupar por TipoMovimiento
    comparison = df.groupby('TipoMovimiento')['Monto'].sum().reset_index()
    # Filtrar solo Ingreso y Egreso
    comparison = comparison[comparison['TipoMovimiento'].isin(['Ingreso', 'Egreso'])]
    
    fig = px.pie(
        comparison,
        values='Monto',
        names='TipoMovimiento',
        title='Proporción Ingresos vs Egresos',
        color='TipoMovimiento',
        color_discrete_map={'Ingreso': '#28a745', 'Egreso': '#dc3545'},
        hole=0.3
    )
    return fig
