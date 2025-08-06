import streamlit as st
import numpy as np
import pandas as pd
import base64
from io import BytesIO

st.set_page_config(page_title="Cálculo de Cuotas", layout="centered")

st.title("Simulador de Préstamo")

# Entradas
capital = st.number_input("Capital del préstamo:", min_value=0.0, step=100.0)
tasa = st.number_input("Tasa de interés anual (%):", min_value=0.0, step=0.1)
plazo = st.number_input("Plazo en meses:", min_value=1)

seguro_dano = st.checkbox("¿Incluir seguro de daño?")
monto_seguro = 0

if seguro_dano:
    monto_seguro = st.number_input("Monto fijo del seguro de daño:", min_value=0.0, step=10.0)

# Función para convertir el DataFrame a Excel (con openpyxl)
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Amortización')
    return output.getvalue()

# Función para generar enlace de descarga
def generar_link_descarga_excel(df):
    excel_data = convertir_a_excel(df)
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="tabla_amortizacion.xlsx">📥 Descargar tabla en Excel</a>'
    return href

# Cálculo
if st.button("Calcular"):
    tasa_mensual = tasa / 12 / 100
    cuota = (capital * tasa_mensual) / (1 - (1 + tasa_mensual) ** -plazo) if tasa_mensual > 0 else capital / plazo
    cuota_total = cuota + monto_seguro if seguro_dano else cuota

    st.success(f"Cuota mensual: L {cuota_total:,.2f}")

    saldo = capital
    data = []

    for mes in range(1, plazo + 1):
        interes = saldo * tasa_mensual
        abono_capital = cuota - interes
        saldo -= abono_capital
        fila = {
            "Mes": mes,
            "Cuota base": round(cuota, 2),
            "Interés": round(interes, 2),
            "Abono a capital": round(abono_capital, 2),
            "Saldo restante": round(max(saldo, 0), 2),
        }
        if seguro_dano:
            fila["Seguro"] = monto_seguro
            fila["Cuota total"] = round(cuota_total, 2)
        data.append(fila)

    df_resultado = pd.DataFrame(data)

    st.subheader("Tabla de Amortización")
    st.dataframe(df_resultado)

    st.markdown(generar_link_descarga_excel(df_resultado), unsafe_allow_html=True)
