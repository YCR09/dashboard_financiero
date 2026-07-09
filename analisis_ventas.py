import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import openpyxl
import io
from dotenv import load_dotenv
import os

def ventas():
    
    st.title("📈 Dashboard - Ejecutivo de Análisis de Ventas - 2026", anchor = False)

    st.markdown("---")

    if 'df_excel' in st.session_state:
        
        df = st.session_state['df_excel']

        # Convertir la fecha a datetime
        df["fecha"] = pd.to_datetime(df["fecha"])

        # 3. Extraer la fecha mínima y máxima
        fecha_inicio = df['fecha'].min().strftime('%d/%m/%Y')
        fecha_fin = df['fecha'].max().strftime('%d/%m/%Y')

         # 4. Mostrar el período en un contenedor llamativo al inicio
        st.info(f"📅 **Período de Análisis detectado:** Del **{fecha_inicio}** al **{fecha_fin}**")

        st.divider() 

        # Suma de ventas por mes
        df_ventas_mes = (
            df.groupby(df["fecha"].dt.to_period("M"))
            .agg(total_ventas=("ventas", "sum"))
            .reset_index()
            )
        # Renombrar la columna del período
        df_ventas_mes.rename(columns={"fecha": "mes"}, inplace=True)

        # Convertir el período a texto
        df_ventas_mes["mes"] = df_ventas_mes["mes"].astype(str)

        # Calcular crecimiento mensual (%)
        df_ventas_mes["crecimiento"] = (
            df_ventas_mes["total_ventas"].pct_change() * 100
            )
        
        # El primer mes no tiene crecimiento
        df_ventas_mes["crecimiento"] = (
            df_ventas_mes["crecimiento"].fillna(0)
            )
        
        # Formato con signo + y - y 2 decimales
        df_ventas_mes["label"] = df_ventas_mes["crecimiento"].apply(
            lambda x: f"{x:+.2f}%"
        )

        # Agrupar ventas por región
        df_region = (
            df.groupby("region")
            .agg(total_ventas=("ventas", "sum"))
            .reset_index()
        )

        # Ordenar de mayor a menor
        df_region = df_region.sort_values("total_ventas", ascending=False)

        df_region["porcentaje"] = (
            df_region["total_ventas"] / df_region["total_ventas"].sum() * 100
        )

        # Cálculo del Beneficio
        beneficio = (df['ventas'].sum() - df['compras'].sum())

        # Cálculo del Roi
        roi = ((df['ventas'].sum() - df['compras'].sum()) / df['compras'].sum()) *100

        # Agrupar ventas por estatus
        df_estatus = (
            df.groupby("estatus")
            .agg(total_ventas=("ventas", "sum"))
            .reset_index()
        )

    # ******************  KPIs  ************************

        st.markdown("## ✔ KPI's de Ventas")

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        col1.metric(
            "Total Ventas", 
            f"€{df['ventas'].sum():,.0f}"
        )

        col2.metric(
            "Promedio Mensual", 
            f"€{df_ventas_mes['total_ventas'].mean():,.0f}"
        )

        col3.metric(
            "Ticket Medio",
            f"€{df['ventas'].abs().mean():,.0f}"
        )

        col4.metric(
            
            "Beneficio", 
            f"€{beneficio:,.0f}"
            )
        
        with col5:
            if roi <= 0:
                st.metric(
                    label="ROI", 
                    value=f"{roi:,.0f}%",
                    delta=f"-⚠️ Roi Negativo",
            )
            else:
                st.metric(
                    label="ROI", 
                     value=f"{roi:,.0f}%",
                    delta=f"✅ Roi Positivo",
                    delta_color="normal",
                )

        with col6:
            if df_ventas_mes['crecimiento'].sum() <= 0:
                st.metric(
                    label="Crecimiento Acumulado",
                    value=f"{df_ventas_mes['crecimiento'].sum():,.0f}%",
                    delta=f"-⚠️ Crecimiento Negativo ",
                   
                )
            else:
                st.metric(
                    label="Crecimiento Acumulado",
                    value=f"{df_ventas_mes['crecimiento'].sum():,.0f}%",
                    delta=f"✅Crecimiento Positivo",
                    delta_color="normal",
                )

        st.divider()

        # ******************* Gráficos **************************

        st.markdown('## ✔ Análisis de Tendencia')
        # Gráfico de líneas
        fig_1 = px.bar(
            df_ventas_mes,
            x="mes",
            y="total_ventas",
            text='total_ventas',
            title="📊 Evolución de las ventas mensuales"
            )
        
        st.plotly_chart(fig_1, use_container_width=True)

        # Gráfico de líneas
        fig_2 = px.line(
            df_ventas_mes,
            x="mes",
            y="crecimiento",
            markers=True,
            text="label",
            title="📈 Crecimiento mensual de las ventas (%)"
        )

        fig_2.update_traces(
                textposition="top center"
            )

        fig_2.add_hline(
            y=0,
            line_dash="dash",
            line_color="red"
        )

        st.plotly_chart(fig_2, use_container_width=True)

        st.markdown('## ✔ Análisis Geográfico')
        col1, col2 = st.columns(2)
        with col1:
                # Gráfico
                fig_3 = px.bar(
                    df_region,
                    x="region",
                    y="total_ventas",
                    text="total_ventas",
                    color="total_ventas", 
                    color_continuous_scale='Viridis',
                    title="🌎 Ventas (€) por Región"
                )
                fig_3.update_layout(template="plotly_white", showlegend=False)   
        
                st.plotly_chart(fig_3, use_container_width=True)

        with col2:        

                fig_4 = px.pie(
                    df_region,
                    names="region",
                    values="total_ventas",
                    title="✅ % Participación de ventas por Región"
                )

                st.plotly_chart(fig_4, use_container_width=True)

        st.markdown('## ✔ Análisis de Enduedamiento')
        col1, col2 = st.columns(2)

        with col1:
                # Gráfico
                fig_3 = px.bar(
                    df_estatus,
                    x="estatus",
                    y="total_ventas",
                    text="total_ventas",
                    color="total_ventas", 
                    color_continuous_scale='Viridis',
                    title="🛒 Ventas (€) por Estatus"
                )
                fig_3.update_layout(template="plotly_white", showlegend=False)   
        
                st.plotly_chart(fig_3, use_container_width=True)

        with col2:        

                fig_4 = px.pie(
                    df_estatus,
                    names="estatus",
                    values="total_ventas",
                    title="✅ % Participación de ventas por Estatus"
                )

                st.plotly_chart(fig_4, use_container_width=True)

        credito = df_estatus[df_estatus['estatus'] != 'cobrada']['total_ventas'].sum()
        contado = df_estatus[df_estatus['estatus'] == 'cobrada']['total_ventas'].sum()
        dif_cred_cont = contado - credito

        if len(df_ventas_mes['crecimiento']) != 1:

            st.divider()
            st.markdown("## 🚨 Sistema Alerta Inteligente 🚨")
            st.divider()
            aumento = df_ventas_mes['crecimiento'].iloc[-1] - df_ventas_mes['crecimiento'].iloc[-2]
            if df_ventas_mes['crecimiento'].iloc[-1] < df_ventas_mes['crecimiento'].iloc[-2]:
               
                st.error(f'⚠️ ¡Advertencia! hay una caida en las ventas del **{aumento:,.2f}** %, con respecto al mes anterior ⚠️')
            else:
                
                st.success(f'✅ ¡Excelente! hay Crecimiento en las ventas con respecto al mes anterior del **{aumento:,.2f}** % ✅')

        if dif_cred_cont < 0:
            st.error(f'⚠️ ¡Advertencia! las ventas a Crédito superan las ventas de Contado ⚠️') 

    else:
        st.warning("👈 Ve a la sección del menú 📤 Información en **Fuente de Datos** y selecciona una opción de datos para analizar")
