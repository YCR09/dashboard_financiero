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

def simulacion():
    
    st.title("⚡ Dashboard - Simulación Financiera - 2026", anchor = False)

    st.markdown("---")

    # 1. ENTRADAS DE DATOS (Puedes conectarlo a tu archivo cargado)
    st.sidebar.header("Simulación de Datos")
    
        
    costos_fijos = st.sidebar.number_input(
            "**Costos Fijos Totales (€)**",  
            min_value=100.0, 
            value=2000.0, 
            step=100.0
        )

    porcentaje_beneficio = (
            st.sidebar.slider(
                "**Margen de Beneficio Bruto (%)**",
                min_value=1,
                max_value=100,
                value=10,
                step=1,
            )            
        )
    st.sidebar.markdown("---")
    inversion = (
                    st.sidebar.slider(
                        "**Inversión Inicial (€)**",
                        min_value=100,
                        max_value=900000,
                        value=1000,
                        step=200,
                    )            
                )

    #*********************  Simulación de Margen para el PE ************************
        
    st.markdown("## ✔ Simulador de Margen que calcula el Punto de Equilibrio a partir de los Costos Fijos")
    

    st.success("📌 Factor Escala = Costos Fijos / (Inversión Inicial * Margen de Beneficio Bruto (%)) -> Punto de Equilibrio (€) = (Inversión Inicial * (1 + Margen de Beneficio Bruto (%)) * Factor Escala) ")
    st.markdown("---")
    st.info("✋ **¡ A L T O !... 👈** Para esta simulación, ve a la sección del menú lateral, ingresa los **Costos Fijos (€)** y el **Margen de Beneficio Bruto (%)**.")
    st.markdown("---")
       
    #*********************  KPIs de PE ************************
    col1, col2, col3, col4 = st.columns(4)
    with col1:

            # 1. Convertir el porcentaje a decimal para la fórmula
            margen_decimal = porcentaje_beneficio / 100

            # 2. Calcular la ganancia que nos da la inversión actual
            ganancia_volumen_actual = inversion * margen_decimal

            # 3. Aplicar la fórmula del Punto de Equilibrio Operativo
            factor_escala = costos_fijos / ganancia_volumen_actual

            pe = (
                    inversion * (1 + margen_decimal)
                ) * factor_escala
            
            st.metric(
                label=f"Inversión Inicial (€)",
                value=f"€{pe-costos_fijos:,.2f}",
                )

    with col2:

            st.metric(
                label=f"Costos Fijos Totales (€)",
                value=f"€{costos_fijos:,.2f}",
                
            )

    with col3:

            st.metric(
                label=f"Margen de Beneficio Bruto (%)",
                value=f"{porcentaje_beneficio:,.2f}%",
                
            )
          
    with col4:

            st.metric(
                label=f"Punto de Equilibrio (PE)",
                value=f"€{pe:,.2f}",
                delta=f"Facturación con {porcentaje_beneficio:,.2f} % de margen",
                help="Son las ventas totales para alcanzar el Punto de Equilibrio.",
                delta_color="normal",
            )

    #*********************  KPIs de enduedamiento ************************
    
    # Calvulamos el beneficio actual con la inversión y el porcentaje de beneficio
    utilidad = inversion * (porcentaje_beneficio/100)

        # Calculamos el total de ventas 
    ventas_totales = inversion * (1 + porcentaje_beneficio / 100)

        # Calculamos el limite del crédito
    limite_credito =  ((utilidad - costos_fijos) / utilidad) * ventas_totales
        
    if limite_credito < 0:
            limite_credito = 0

    # Calculamos venta contado
    contado =  ventas_totales - limite_credito
               
    st.divider()
    st.markdown("## ✔ Simulación de Cobertura de Costos de Ventas de Contado y a Crédito")
    
    st.markdown("---")
    st.info("👈 Para esta simulación, ve a la sección del menú lateral, ingresa la **Inversión Inicial (€)**, los **Costos Fijos (€)** y el **Margen de Beneficio Bruto (%)**.")
    st.markdown("---")
          
    col1, col2, col3, col4 = st.columns(4)
    with col1:
            st.metric(
                label="Ventas Totales (€)",
                value=f"€{ventas_totales:,.2f}",
                help="Es el total de ventas, inversión x Margen de Beneficio.",
                delta=f"✅ Monto Total de Ventas",
                delta_color="normal",
            )

    with col2:
            st.metric(
                label="Utilidad Bruta (€)",
                value=f"€{utilidad - costos_fijos:,.2f}",
                help="Es la utilidad bruta después de cubrir los costos fijos.",
                delta=f"**Utilidad €{utilidad:,.2f} - Costos Fijos €{costos_fijos:,.2f}**",
                delta_color="off"
                )
            
    with col3:
            if limite_credito <= 0:
                st.metric(
                    label="Límite Crédito Viable (€)",
                    value=f"€ {limite_credito:.2f}",
                    help="Es el límite de crédito permitido de venta, luego de cubrir los costos fijos.",
                    delta=f"⚠️ No es posible vender a Crédito",
                    delta_color="inverse",
                )
            else:
                st.metric(
                    label="Límite Crédito Viable (€)",
                    value=f"€{limite_credito:,.2f}",
                    help="Es el límite de crédito permitido de venta, luego de cubrir los costos fijos.",
                    delta=f"✅ Monto Viable a Crédito",
                    delta_color="normal",
                )

    with col4:
            st.metric(
                label="Venta de Contado(€)",
                value=f"€{contado:,.2f}",
                delta=f"✅ Monto de Contado",
                delta_color="normal",
                help="Es el monto de ventas que se realizan de contado para cubrir los costos fijos.",
            )
  
    if costos_fijos > utilidad:
            st.error(
                f"⚠️ Zona de Pérdida, Los costos fijos **€{costos_fijos:,.0f}** superan la utilidad actual **€ {utilidad:,.0f}**."
            )
    elif costos_fijos == utilidad:
            st.warning(
                f"⚠️ Zona de Equilibrio, Los costos fijos **€{costos_fijos:,.0f}** son iguales a la utilidad actual **€ {utilidad:,.0f}** no es posible vender a crédito."
            )
    else:
             if limite_credito > 0:
                st.success(
                    f"✅ Solo puede vender a crédito **{limite_credito/ventas_totales*100:,.2f}%** | **€{limite_credito:,.2f}** zona del límite Viable, con un beneficio de **€{(utilidad - costos_fijos):,.2f}** para ser cobrado a Plazo."
                )

            
    