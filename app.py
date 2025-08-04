import streamlit as st
import numpy as np
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Simulador de Cuotas", layout="centered")
st.markdown("<h1 style='text-align: center; color: #003366;'>Cuotas de Préstamo</h1>", unsafe_allow_html=True)

def calcular_cuotas_df(monto, tasa_anual, plazo_meses, frecuencia, tipo_cuota, incluir_seguro, porcentaje_seguro):
    freq_dict = {'Mensual': 12, 'Trimestral': 4, 'Semestral': 2, 'Anual': 1, 'Al vencimiento': 0}
    pagos_por_año = freq_dict[frecuencia]

    if pagos_por_año == 0:
        tasa_total = tasa_anual / 100 * (plazo_meses / 12)
        interes = monto * tasa_total
        cuota_total = monto + interes
        return pd.DataFrame([{
            "Pago": 1,
            "Cuota": cuota_total,
            "Interés": interes,
            "Abono": monto,
            "Seguro": 0,
            "Saldo": 0
        }])

    n_pagos = int(plazo_meses * pagos_por_año / 12)
    tasa_periodo = tasa_anual / 100 / pagos_por_año
    saldo = monto

    if tipo_cuota == 'Nivelada':
        cuota_base = monto * (tasa_periodo * (1 + tasa_periodo) ** n_pagos) / ((1 + tasa_periodo) ** n_pagos - 1)
    else:
        abono_fijo = monto / n_pagos

    seguro_unitario = 0
    if incluir_seguro == 'Sí':
        seguro_unitario = (monto / 1000) * porcentaje_seguro * 12 / pagos_por_año

    datos = []
    for i in range(1, n_pagos + 1):
        interes = saldo * tasa_periodo
        if tipo_cuota == 'Nivelada':
            abono = cuota_base - interes
            cuota = cuota_base
        else:
            abono = abono_fijo
            cuota = abono + interes

        saldo -= abono
        saldo = max(saldo, 0)
        seguro = seguro_unitario if incluir_seguro == 'Sí' else 0
        cuota_total = cuota + seguro

        datos.append({
            "Pago": i,
            "Cuota": cuota_total,
            "Interés": interes,
            "Abono": abono,
            "Seguro": seguro,
            "Saldo": saldo
        })

    df = pd.DataFrame(datos)
    return df

# FORMULARIO
with st.form("formulario"):
    col1, col2 = st.columns(2)
    with col1:
        monto = st.number_input("💰 Monto del préstamo", value=10000.0, step=100.0, format="%.2f")
        tasa = st.number_input("📈 Tasa de interés anual (%)", value=12.0, step=0.1)
        plazo = st.number_input("📅 Plazo (meses)", value=36, step=1)

    with col2:
        frecuencia = st.selectbox("📆 Frecuencia de pago", ['Mensual', 'Trimestral', 'Semestral', 'Anual', 'Al vencimiento'])
        tipo_cuota = st.selectbox("🔁 Tipo de cuota", ['Nivelada', 'Saldos Insolutos'])
        incluir_seguro = st.selectbox("🛡 ¿Incluir seguro?", ['No', 'Sí'])
        porcentaje_seguro = st.number_input("📌 % Seguro por cada Lps. 1,000", value=0.50, step=0.01)

    calcular = st.form_submit_button("🔍 Calcular cuotas")

# RESULTADOS
if calcular:
    df_resultado = calcular_cuotas_df(monto, tasa, plazo, frecuencia, tipo_cuota, incluir_seguro, porcentaje_seguro)

    total_pago = df_resultado["Cuota"].sum()

    st.markdown("---")
    st.markdown(
        f"""<div style='background-color:#e6f2ff; padding:20px; border-radius:10px; text-align:center;'>
        <h3 style='color:#004080;'>💳 Cuota total a pagar:</h3>
        <h2 style='color:#003366;'>Lps. {total_pago:,.2f}</h2>
        </div>""",
        unsafe_allow_html=True
    )

    # Formatear valores
    df_mostrar = df_resultado.copy()
    for col in ["Cuota", "Interés", "Abono", "Seguro", "Saldo"]:
        df_mostrar[col] = df_mostrar[col].apply(lambda x: f"Lps. {x:,.2f}")

    st.subheader("📋 Tabla de amortización:")
    st.dataframe(df_mostrar, use_container_width=True)

    # EXPORTAR ARCHIVOS
    st.markdown("### 📁 Exportar tabla:")

    colpdf, colexcel, colsalir = st.columns([1, 1, 1])

    with colpdf:
        # PDF (solo texto simple en .txt simulado)
        pdf_buffer = io.StringIO()
        pdf_buffer.write("Tabla de amortización\n\n")
        pdf_buffer.write(df_mostrar.to_string(index=False))
        pdf_bytes = io.BytesIO(pdf_buffer.getvalue().encode("utf-8"))
        st.download_button("📄 Descargar PDF", data=pdf_bytes, file_name="amortizacion.txt", mime="text/plain")

    with colexcel:
        # Excel
        excel_bytes = io.BytesIO()
        with pd.ExcelWriter(excel_bytes, engine='xlsxwriter') as writer:
            df_resultado.to_excel(writer, index=False, sheet_name='Amortización')
        st.download_button("📊 Descargar Excel", data=excel_bytes.getvalue(), file_name="amortizacion.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with colsalir:
        st.button("🔁 Salir / Reiniciar", on_click=lambda: st.experimental_rerun())
