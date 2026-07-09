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

def finanzas():
    
    st.title("🧮 Dashboard - Ejecutivo de Análisis Financiero - 2026", anchor = False)

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

        # *****************  KPIs de optimización de Margen / Beneficio  *****************
        st.markdown("## ✔ Optimización de Margen para Punto de Equilibrio")
        st.info("👈 Ve a la sección del menú lateral, en  | **Costos Fijos Totales(€)** |   ingresa los costos fijos acumulados del período a analizar.")
        st.divider()
        

        # 1. ENTRADAS DE DATOS (Puedes conectarlo a tu archivo cargado)
        st.sidebar.header("Situación Financiera Actual")
        costos_fijos = st.sidebar.number_input(
            "Costos Fijos Totales (CF) (€)",
            min_value=100.0, 
            value=2000.0, 
            step=100.0
        )

        # 1. Realizas el cálculo matemático puro y lo guardas de forma segura
        ventas_actuales = float(df["ventas"].sum())

        # 1. Realizas el cálculo matemático puro y lo guardas de forma segura
        compras_actuales = float(df["compras"].sum())

        # 2. Dibujas la métrica en la barra lateral sin asignarla a ninguna variable
        st.sidebar.metric(
            "Facturación/Ventas Actuales (FA) (€)", f"€{ventas_actuales:,.0f}"
        )

        # 2. Dibujas la métrica en la barra lateral sin asignarla a ninguna variable
        st.sidebar.metric(
            "Costos de Compras Actuales (CCA) (€)", f"€{compras_actuales:,.0f}"
        )

        # 2. Dibujas la métrica en la barra lateral sin asignarla a ninguna variable
        st.sidebar.metric(
            "Beneficio Bruto Actual (BBA) (€)", f"€{ventas_actuales - compras_actuales:,.0f}"
        )

        # Cálculo del Roi
        margen_actual_pct = ((df['ventas'].sum() - df['compras'].sum()) / df['compras'].sum()) *100
         
        st.sidebar.metric("Margen Actual (MA) (%)", f"{margen_actual_pct:,.0f}%")
       
        # 2. CÁLCULOS FINANCIEROS INVERSOS
        # Margen necesario para equilibrar la balanza con las ventas de hoy
        
        if ventas_actuales > 0:
            margen_necesario_pct = costos_fijos  / ventas_actuales
        else:
            margen_necesario_pct = 0.0
        
        # Incremento requerido
        incremento_margen_requerido = margen_necesario_pct - (margen_actual_pct/100)

        #*********************  KPIs  ************************

        # 3. INTERPRETACIÓN DE RESULTADOS EN PANTALLA
        st.subheader("📊 Diagnóstico del Margen de Beneficio Actual")
        st.success("📌 MCM = CF / FA   |  DM = MCM - MA  |  BNA = (CCA * MCM) - CF")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="Margen de Contribución Mínimo (MCM)",
                value=f"{margen_necesario_pct * 100:.1f}%",
                help="Es el porcentaje de ganancia bruta que cada venta debe dejar para cubrir los costos fijos.",
            )
        with col2:
            if incremento_margen_requerido > 0:
                st.metric(
                    label="Diferencia de Margen (DM)",
                    value=f"+{incremento_margen_requerido * 100:.1f}%",
                    help="Es la diferencia en porcentaje entre el margen de Contribución mínima y el % que representan los costos operativos con lo facturado.",
                    delta=f"-⚠️ Zona de Pérdida",
                    #delta_color="inverse",
                )
            else:
                # 1. Calculamos la variable de forma independiente en su propia línea
                absorber_margen = abs(incremento_margen_requerido) * 100

                # 2. Mostramos el resultado limpiamente en el componente de Streamlit
                st.metric(
                    label="Margen Excedente",
                    value=f"{absorber_margen:.1f}%",
                    delta="✅ Zona de Ganancia",
                    delta_color="normal",
                )
                          
        with col3:
            utilidad_actual = (compras_actuales * margen_actual_pct/100) - costos_fijos
            if utilidad_actual <= 0:
                st.metric(label="Beneficio Neto Actual (BNA) (€)",
                        value=f"€ {utilidad_actual:,.2f}",
                        help="Es la utilidad neta que se obtiene tras cubrir todos los costos fijos.",
                        delta=f"-⚠️ Zona de Pérdida",
                        )
            else:
                st.metric(label="Beneficio Neto Actual (BNA) (€)",
                        value=f"€ {utilidad_actual:,.2f}",
                        help="Es la utilidad neta que se obtiene tras cubrir todos los costos fijos.",
                        delta=f"✅ Zona de Ganancia",
                        delta_color="normal",
                        )

        st.divider()
     
        # 4. PLAN DE ACCIÓN 
      
        if incremento_margen_requerido*100 > 0:
            st.subheader("✋ Análisis de resultados")
            st.warning(
                f"Los productos actuales ganan el **{margen_actual_pct:.2f}%**, sin embargo se necesita que promedien **{margen_necesario_pct*100:.2f}%** con tu nivel de ventas actual de contado."
            )              
               
        # Simulación de estrategias
            incremento = ((costos_fijos + compras_actuales)-compras_actuales) / compras_actuales
            
            reduccion_costo = (margen_necesario_pct - margen_actual_pct/100) / (
                1 - margen_actual_pct/100
            )

            st.write("Posibles opciones estratégicas:")
            st.markdown(
                f"*   **Opción A (Subir Precios):**  Incrementar los productos en un **{incremento * 100:.1f}%** para alcanzar el Punto de Equilibrio (asumiendo que se mantiene el mismo volumen de ventas de contado)."
            )
            st.markdown(
                f"*   **Opción B (Bajar Costos):** Negociar con los proveedores, mejorar procesos, bajar los costos en un **{reduccion_costo * 100:.1f}%**."
            )
        elif incremento_margen_requerido*100 < 0 and incremento_margen_requerido*100 > -5:
            st.warning("🟡 ¡Excelente! El margen actual es suficiente para cubrir los costos fijos con el nivel de facturación actual, sin embargo la rentabilidad es baja.")
        else:
            st.success("🟢 ¡Excelente! El negocio presenta una rentabilidad del " + f"{-1*incremento_margen_requerido*100:.1f}" + "%.")
       
        # 5. GRÁFICO VISUAL DEL DESAFÍO
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=["Margen Actual", "Margen Requerido (PE)"],
                y=[margen_actual_pct, margen_necesario_pct * 100],
                marker_color=["#EF553B", "#636EFA"]
                if incremento_margen_requerido > 0
                else ["#00CC96", "#636EFA"],
                text=[f"{margen_actual_pct:.0f}%", f"{margen_necesario_pct*100:.0f}%"],
                textposition="auto",
            )
        )
        fig.update_layout(
            title="Comparativa: Margen Actual vs Margen Necesario para el Punto de Equilibrio (PE)",
            yaxis_title="Porcentaje (%)",
            yaxis=dict(range=[0, 100]),
        )
        st.plotly_chart(fig, use_container_width=True)

         #*********************  KPIs de enduedamiento ************************
       
        st.divider()
        st.markdown("## ✔ Análisis de Capacidad de Cobertura de Costos")
        st.divider()
  
        limite_credito =  (utilidad_actual/ (margen_actual_pct/100)) + utilidad_actual

        if limite_credito < 0:
            limite_credito = 0

        # Agrupar ventas por estatus
        df_estatus = (
            df.groupby("estatus")
            .agg(total_ventas=("ventas", "sum"))
            .reset_index()
        )
        
        credito = df_estatus[df_estatus['estatus'] != 'cobrada']['total_ventas'].sum()
        contado = df_estatus[df_estatus['estatus'] == 'cobrada']['total_ventas'].sum()

        pct_contado = contado / ventas_actuales if ventas_actuales > 0 else 0
        
        col1, col2, col3  = st.columns(3)
        with col1:
            st.metric(
                label="Ventas Contado",
                value=f"€{contado:,.2f}",
               
            )
        with col2:
            st.metric(
                label="Ventas Crédito",
                value=f"€{credito:,.2f}",
            )
      
        with col3:
            if limite_credito <= 0:
                st.metric(
                    label="Límite Crédito Necesario",
                    value=f"€ {limite_credito:,.2f}",
                    delta=f"⚠️ No es posible vender a Crédito",
                    delta_color="inverse",
                )
            else:
                st.metric(
                    label="Límite Necesario",
                    value=f"€{limite_credito:,.2f}",
                    delta=f"✅ Monto Necesario a Crédito",
                    delta_color="normal",
                )

        if costos_fijos > (ventas_actuales - compras_actuales):
            st.error(
                f"⚠️ Zona de Pérdida, Los costos fijos **€{costos_fijos:,.0f}** superan la utilidad actual **€ {ventas_actuales - compras_actuales:,.0f}** del cual solo de contado es **{pct_contado*100:.2f}%** -> **€ {pct_contado * (ventas_actuales - compras_actuales):,.2f}**."
            )
        else:

            if credito > limite_credito and limite_credito > 0:
                st.warning(
                    f"⚠️ El monto de ventas a crédito **€{credito:,.2f}** supera el límite necesario de **€{limite_credito:,.2f}**. No cubre los costos operativos."
                )
            elif credito <= limite_credito and limite_credito > 0:
                st.success(
                    f"✅ El monto de ventas a crédito **€{credito:,.2f}** está dentro del límite necesario de **€{limite_credito:,.2f}**. Se puede mantener la exposición a crédito."
                )
      
    else:
        st.warning("👈 Ve a la sección del menú 📤 Información y sube el archivo Excel a analizar")
