import streamlit as st
import pandas as pd

from analisis_comercial import comercial

def datos():
    
    st.title("📤 Información", anchor = False)

    st.markdown("---")

    mensaje = st.warning(" 👈 Ve a la sección del menú lateral **Fuente de Datos** y selecciona una opción de datos para analizar")

    #st.sidebar.header("📂 Fuente de datos")

    opcion = st.sidebar.radio(
        "**Fuente de Datos :**",
        (
            "Seleccione una opción...",
            "📝 Datos de demostración",
            "📁 Cargar archivo Excel",
            #"☁️ Google Drive Sheets"
        ),
        index=0
    )

    if opcion == "Seleccione una opción...":
        #del st.session_state["df_excel"]
        #st.session_state.clear()
        #st.session_state["df_excel"] = None
        st.session_state.pop("df_excel", None)

    elif opcion == "📝 Datos de demostración":
        mensaje.empty()
        try:
            df = pd.read_excel("datos_demo.xlsx")
            st.session_state['df_excel'] = df

            st.success("Datos de demostración cargados.")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error al leer el archivo {e}")

    elif opcion == "📁 Cargar archivo Excel":
        mensaje.empty()
        uploaded_file = st.file_uploader(
            "Subir un archivo Excel con las siguientes columnas en este orden a analizar :  | **cliente** | **fecha** | **ventas** | **compras** | **region** | **estatus** | -> la columna  **cliente** es el código o id del cliente.",
            type=["xlsx"]
        )
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)

                # 2. Convertir los nombres de las columnas a minúsculas
                df.columns = df.columns.str.strip().str.lower()

                if len(df.columns) != 6:

                    # 1. Tu lista de columnas obligatorias (ya normalizadas)
                    columnas_obligatorias = {'cliente', 'fecha', 'ventas', 'compras', 'region', 'estatus'}

                    # Convertimos las columnas del DataFrame a un conjunto para compararlas
                    columnas_actuales = set(df.columns)

                    # 3. Validar si faltan columnas usando la resta de conjuntos
                    columnas_faltantes = columnas_obligatorias - columnas_actuales

                    # Mensaje de error detallado indicando qué falta exactamente
                    st.error(f"❌ Error: El archivo Excel está incompleto.")
                    st.warning(f"Faltan las siguientes columnas obligatorias: {list(columnas_faltantes)}")
                
                else:
                    # Diccionario de expresiones regulares:
                    reglas_regex = {
                    
                        r'^ven.*': 'ventas',
                        r'^com.*': 'compras',
                        r'^reg.*': 'region',
                        r'^est.*': 'estatus',
                        r'^cli.*': 'cliente',
                        r'^fec.*': 'fecha',
                        
                    }            

                    # 2. Convertir los nombres de las columnas a minúsculas
                    df.columns = df.columns.str.replace(reglas_regex, regex=True)

                    # Normalizar los valores de la columna estatus 
                    df['estatus'] = df['estatus'].str.lower().replace({
                        '^cobr.*': 'cobrada',
                        '^pend.*': 'pendiente'
                    }, regex=True)
                    
                    st.session_state['df_excel'] = df

                    st.success(" ✔ Carga exitosa de archivo | ¡Validación exitosa! Columnas completas ")
                    st.dataframe(df.head())
            except Exception as e:
                st.error(f"Error al leer el archivo {e}")

    elif opcion == "☁️ Google Drive Sheets":

        enlace = st.text_input(
            "Pegue el enlace de Google Drive"
        )

        if enlace:

            try:

                file_id = enlace.split("/d/")[1].split("/")[0]

                url = f"https://drive.google.com/uc?id={file_id}"

                df = pd.read_excel(url)

                st.success("Archivo cargado correctamente.")

            except:

                st.error("El enlace no es válido.")

                st.stop()

