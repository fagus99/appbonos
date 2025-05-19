import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora de Bonos - Casino", layout="centered")

st.title("🎰 Calculadora de Bonos para Casino Online")

st.markdown("Subí los archivos con los datos de los usuarios:")

# Carga de archivos
jugado_file = st.file_uploader("📄 Archivo de importe jugado", type=["csv", "xlsx"])
deposito_file = st.file_uploader("📄 Archivo de depósitos", type=["csv", "xlsx"])

st.markdown("### 🧮 Parámetros de la promoción")

# Parámetros base
porcentaje_bono = st.slider("Porcentaje de bonificación (%)", min_value=0, max_value=100, value=20)
min_deposito = st.number_input("Depósito mínimo requerido", min_value=0.0, value=1000.0)
min_jugado = st.number_input("Importe jugado mínimo requerido", min_value=0.0, value=1000.0)
max_bono = st.number_input("Importe máximo de bono por usuario", min_value=0.0, value=10000.0)

# Condición opcional de rollover
usar_rollover = st.checkbox("¿Aplicar condición de rollover?")
if usar_rollover:
    factor_rollover = st.number_input("Multiplicador de rollover (ej: 5 significa jugar 5 veces el bono)", min_value=1, value=5)

# Procesamiento
if jugado_file and deposito_file:
    try:
        if jugado_file.name.endswith("csv"):
            jugado_df = pd.read_csv(jugado_file)
        else:
            jugado_df = pd.read_excel(jugado_file)

        if deposito_file.name.endswith("csv"):
            depositos_df = pd.read_csv(deposito_file)
        else:
            depositos_df = pd.read_excel(deposito_file)

        # Normalización de encabezados
        jugado_df.columns = [col.lower().strip() for col in jugado_df.columns]
        depositos_df.columns = [col.lower().strip() for col in depositos_df.columns]

        jugado_df.rename(columns={jugado_df.columns[1]: "jugado"}, inplace=True)
        depositos_df.rename(columns={depositos_df.columns[1]: "deposito"}, inplace=True)

        df = pd.merge(jugado_df, depositos_df, on="usuario", how="inner")

        # Aplicar condiciones
        bonificables = df[(df["jugado"] >= min_jugado) & (df["deposito"] >= min_deposito)].copy()
        bonificables["bono"] = (bonificables["deposito"] * porcentaje_bono / 100).clip(upper=max_bono)

        if usar_rollover:
            bonificables["rollover"] = bonificables["bono"] * factor_rollover

        st.success(f"Usuarios bonificables encontrados: {len(bonificables)}")

        st.dataframe(bonificables)

        # Exportar CSV
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode("utf-8")

        csv = convert_df(bonificables)
        st.download_button("📥 Descargar archivo con bonos", csv, "usuarios_bonificados.csv", "text/csv")

    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")

