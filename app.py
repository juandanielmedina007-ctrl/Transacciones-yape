import streamlit as st
import pandas as pd
from src.data_loader import load_data
from src.metrics import calculate_kpis, get_busiest_hour
from src.charts import plot_transactions_per_hour

# Configuración de página
# Configuración de página
st.set_page_config(
    page_title="Dashboard Yape",
    page_icon="💸",
    layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS (Ocultar marcas de agua) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎛 Configuración")
    
    # 1. Subida de Archivo
    uploaded_file = st.file_uploader("📂 Subir Reporte Excel", type=['xlsx', 'xls'])
    
    st.markdown("---")
    st.subheader("📅 Filtros")

# Lógica principal
if uploaded_file is not None:
    # Carga de datos
    df_raw = load_data(uploaded_file)

    if df_raw is not None:
        # --- FILTROS ---
        with st.sidebar:
            # Filtro de Fechas
            min_date = df_raw['Fecha'].min()
            max_date = df_raw['Fecha'].max()
            
            date_range = st.date_input(
                "Rango de Fechas",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
        # Aplicar filtros
        if len(date_range) == 2:
            start_date, end_date = date_range
            mask_date = (df_raw['Fecha'] >= start_date) & (df_raw['Fecha'] <= end_date)
            df = df_raw.loc[mask_date]
        else:
            df = df_raw

        st.title("💸 Dashboard de Transacciones Yape")
        st.markdown(f"**Periodo Analizado:** {start_date if len(date_range)==2 else min_date} al {end_date if len(date_range)==2 else max_date}")
        st.markdown("---")
        
        # --- CAPA 1: ESENCIAL ---
        st.subheader("🟢 Resumen General")
        
        kpis = calculate_kpis(df)
        busiest_hour, busiest_count = get_busiest_hour(df)
        
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Total Recibido", f"S/ {kpis['total_recibido']:,.2f}")
        col2.metric("Total Enviado", f"S/ {kpis['total_enviado']:,.2f}")
        col3.metric("Balance Neto", f"S/ {kpis['balance']:,.2f}", delta_color="normal")
        col4.metric("Transacciones", kpis['count_tx'])
        
        col_a, col_b = st.columns([1, 2])
        
        with col_a:
            st.info(f"⏰ **Hora Pico**: {busiest_hour}:00 hrs ({busiest_count} txs)")
            
        with col_b:
            fig_hourly = plot_transactions_per_hour(df)
            if fig_hourly:
                st.plotly_chart(fig_hourly, use_container_width=True)

        st.markdown("---")

        # --- CAPA 2: TEMPORAL ---
        st.subheader("🟡 Patrones en el Tiempo")
        
        from src.charts import plot_daily_evolution, plot_transactions_by_day_of_week, plot_time_range_distribution
        from src.metrics import get_busiest_day

        busiest_date, bus_date_count = get_busiest_day(df)
        
        st.write(f"📅 **Día con más movimiento:** {busiest_date} ({bus_date_count} transacciones)")

        # Fila 1: Evolución
        fig_evol = plot_daily_evolution(df)
        if fig_evol:
            st.plotly_chart(fig_evol, use_container_width=True)
            
        # Fila 2: Análisis Semanal y Rangos
        c2_1, c2_2 = st.columns(2)
        
        with c2_1:
            fig_week = plot_transactions_by_day_of_week(df)
            if fig_week:
                st.plotly_chart(fig_week, use_container_width=True)
                
        with c2_2:
            fig_range = plot_time_range_distribution(df)
            if fig_range:
                st.plotly_chart(fig_range, use_container_width=True)

        st.markdown("---")

        # --- CAPA 3: ANÁLISIS DE MONTOS ---
        st.subheader("🟠 Profundidad Financiera")
        
        from src.metrics import get_amount_stats
        from src.charts import plot_amount_distribution

        amount_stats = get_amount_stats(df)
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("💵 Mayor Ingreso", f"S/ {amount_stats['max_recibido']:,.2f}")
        kpi2.metric("💸 Mayor Egreso", f"S/ {amount_stats['max_enviado']:,.2f}")
        kpi3.metric("📊 Promedio x TX", f"S/ {amount_stats['avg_monto']:,.2f}")

        fig_amounts = plot_amount_distribution(df)
        if fig_amounts:
            st.plotly_chart(fig_amounts, use_container_width=True)

        st.markdown("---")

        # --- CAPA 4: RANKINGS ---
        st.subheader("🔵 Rankings e Insights")
        
        from src.metrics import get_top_days_by_amount, get_top_movements
        from src.charts import plot_top_days_bar

        # Top Días
        top_days = get_top_days_by_amount(df)
        
        c4_1, c4_2 = st.columns([2, 1])
        
        with c4_1:
            fig_top_days = plot_top_days_bar(top_days)
            if fig_top_days:
                st.plotly_chart(fig_top_days, use_container_width=True)
                
        with c4_2:
            st.write("🏆 **Top 5 Días (Volumen Total)**")
            st.dataframe(top_days, hide_index=True, use_container_width=True)

        # Top Movimientos Individuales
        st.write("💎 **Top Transacciones Individuales**")
        
        tab1, tab2 = st.tabs(["Mayor Ingreso 📥", "Mayor Egreso 📤"])
        
        with tab1:
            top_ingresos = get_top_movements(df, 'Ingreso', 5)
            st.dataframe(top_ingresos, hide_index=True, use_container_width=True)
            
        with tab2:
            top_egresos = get_top_movements(df, 'Egreso', 5)
            st.dataframe(top_egresos, hide_index=True, use_container_width=True)

        st.markdown("---")
        
        # --- CAPA 5: COMPARACIONES ---
        st.subheader("🟣 Comparaciones y Control")
        
        from src.metrics import calculate_ratios
        from src.charts import plot_income_expense_comparison
        
        ratios = calculate_ratios(df)
        
        c5_1, c5_2 = st.columns([1, 1])
        
        with c5_1:
            st.write("📊 **Balance de Flujo**")
            # Barras de progreso simples para visualizar proporciones
            st.write(f"Ingresos: {ratios['pct_ingreso']:.1f}%")
            st.progress(int(ratios['pct_ingreso']))
            
            st.write(f"Egresos: {ratios['pct_egreso']:.1f}%")
            st.progress(int(ratios['pct_egreso']))
            
            st.metric("Ratio Gasto/Ingreso", f"{ratios['ratio']:.2f}", help="Por cada sol que ingresa, ¿cuántos salen?")
            if ratios['ratio'] > 1:
                st.error("⚠️ Estás gastando más de lo que recibes.")
            elif ratios['ratio'] > 0.8:
                st.warning("⚠️ Cuidado, tus gastos están cerca de tus ingresos.")
            else:
                st.success("✅ Saludable: Tus ingresos superan tus gastos.")
                
        with c5_2:
            fig_compare = plot_income_expense_comparison(df)
            if fig_compare:
                st.plotly_chart(fig_compare, use_container_width=True)

        st.markdown("---")
        
        # --- ALERTAS y CONTROL ---
        st.subheader("🔴 Centro de Alertas y Control")
        
        from src.metrics import get_alerts
        
        # Input del usuario para definir qué es "Alto Valor"
        user_threshold = st.number_input(
            "Definir Monto Mínimo para Alerta (S/)", 
            min_value=0.0, 
            value=50.0, 
            step=10.0,
            help="Define a partir de qué monto consideras una operación como 'Alerta'."
        )

        alerts = get_alerts(df, custom_threshold=user_threshold)
        
        if not alerts:
            st.success("✅ No se detectaron anomalías ni operaciones inusuales en este periodo.")
        else:
            for alert in alerts:
                with st.expander(f"{alert['title']} ({alert['message']})", expanded=True):
                    # Formato condicional básico para resaltar montos
                    if 'Monto' in alert['data'].columns:
                        st.dataframe(
                            alert['data'].style.background_gradient(subset=['Monto'], cmap='Reds'),
                            use_container_width=True
                        )
                    else:
                        st.dataframe(alert['data'], use_container_width=True)

        # Tabla Completa con Buscador y Formato
        st.write("📋 **Tabla Detallada de Operaciones**")
        st.markdown("Usa esta tabla para auditoría final. Puedes ordenar por cualquier columna.")
        
        # Aplicar estilo: Resaltar Egresos en rojo e Ingresos en verde
        def highlight_type(val):
            if val == 'Ingreso':
                return 'background-color: #d4edda; color: black'
            elif val == 'Egreso':
                return 'background-color: #f8d7da; color: black'
            return ''

        st.dataframe(
            df[['Fecha', 'Hora', 'TipoMovimiento', 'Origen', 'Destino', 'Monto', 'Mensaje']]
            .style.applymap(highlight_type, subset=['TipoMovimiento'])
            .format({'Monto': "S/ {:.2f}"}),
            use_container_width=True,
            height=400
        )

    else:
        st.error("No se pudieron procesar los datos del archivo.")
else:
    st.info("👋 **¡Bienvenido!** Para comenzar, sube tu reporte de transacciones de Yape en el menú de la izquierda.")
    # Imagen o texto de bienvenida
    st.markdown("""
    ### ¿Cómo usar este Dashboard?
    1. Descarga tu reporte desde la app de Yape (Movimientos -> Descargar).
    2. Sube el archivo Excel aquí.
    3. Explora tus métricas de ingresos, gastos y patrones de uso.
    """)
    st.markdown("---")
    st.markdown("### Desarrollado por: [Juan Daniel Medina](https://github.com/juandanielmedina007-ctrl)")
    st.markdown("### GitHub: [Transacciones-yape](https://github.com/juandanielmedina007-ctrl/Transacciones-yape)")
