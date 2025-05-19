
import streamlit as st
import pandas as pd

st.title("Calculadora de Bonos - Casino Online")

# Subida de archivos
jugado_file = st.file_uploader("Subí el archivo con el importe jugado por usuario", type=["csv", "xlsx"])
depositos_file = st.file_uploader("Subí el archivo con los depósitos por usuario", type=["csv", "xlsx"])

# Parámetros de promoción
bono_pct = st.number_input("Porcentaje del bono (%)", min_value=0, max_value=100, value=50)
min_deposito = st.number_input("Depósito mínimo requerido ($)", min_value=0, value=100)
min_jugado = st.number_input("Monto mínimo jugado ($)", min_value=0, value=100)
rollover = st.number_input("Rollover (opcional)", min_value=0, value=0)

if st.button("Calcular usuarios bonificables"):
    if jugado_file and depositos_file:
        # Leer archivos
        if jugado_file.name.endswith(".csv"):
            jugado_df = pd.read_csv(jugado_file)
        else:
            jugado_df = pd.read_excel(jugado_file)

        if depositos_file.name.endswith(".csv"):
            depositos_df = pd.read_csv(depositos_file)
        else:
            depositos_df = pd.read_excel(depositos_file)

        # Unir por usuario
        df = pd.merge(jugado_df, depositos_df, on="usuario", how="inner")
        df = df.rename(columns={"jugado": "jugado", "deposito": "deposito"})

        # Aplicar condiciones
        bonificables = df[(df["jugado"] >= min_jugado) & (df["deposito"] >= min_deposito)].copy()
        bonificables["bono"] = (bonificables["deposito"] * bono_pct / 100).round(2)
        if rollover > 0:
            bonificables["rollover_requerido"] = bonificables["bono"] * rollover

        st.success(f"{len(bonificables)} usuarios califican para el bono")
        st.dataframe(bonificables)

        # Descargar archivo
        csv = bonificables.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar archivo CSV", csv, "usuarios_bonificables.csv", "text/csv")
    else:
        st.warning("Subí ambos archivos para continuar.")
