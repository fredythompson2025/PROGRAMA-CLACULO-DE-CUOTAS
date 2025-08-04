import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Simulador de Cuotas", layout="centered")
st.markdown("<h1 style='text-align: center; color: #003366;'>Simulador de Cuotas de Préstamo</h1>", unsafe_allow_html=True)
st.markdown("##")

def calcular_cuotas_df(monto, tasa_anual, plazo_meses, frecuencia, tipo_cuota, incluir_seguro, porcentaje_seguro):
    freq_dict = {
        'Mensual': 12,
        'Trimestral': 4,
        'Semestral': 2,
        'Anual': 1,
        'Al vencimiento': 0
    }

    pagos_por_año = freq_dict[frecuencia]
    if pagos_por_año == 0:
        tasa_total = tasa_anual / 100 * (plazo_meses / 12)
        interes = monto * tasa_total
        abono = monto
        seguro = 0
        cuota_total = interes + abono
        return pd.DataFrame([{
            "Pago": 1,
            "Cuota": cuota_total,
            "Interés": interes,
            "Abono": abono,
            "Seguro": seguro,
            "Saldo": 0
        }])

    n_pagos = int(plazo_meses * pagos_por_año / 12)
    tasa_periodo = tasa_anual / 100 / pagos_por_año
    saldo = monto

    ref_cuota_dict = {'Mensual': 12, 'Trimestral': 4, 'Semestral': 2, 'Anual': 1}
    ref_cuota = min(ref_cuota_dict.get(frecuencia, 1), n_pagos)
    saldo_referencia = monto

    if tipo_cuota == 'Nivelada':
        cuota_base = monto * (tasa_periodo * (1 + tasa_periodo) ** n_pagos) / ((1 + tasa_periodo) ** n_pagos - 1)
        for _ in range(ref_cuota):
            interes = saldo_referencia * tasa_periodo
            abono = cuota_base - interes
            saldo_referencia -= abono
    else:
        abono_fijo = monto / n_pagos
        for _ in range(ref_cuota):
            interes = saldo_referencia * tasa_periodo
            saldo_referencia -= abono_fijo

    seguro_unitario = 0
    if incluir_seguro == 'Sí':
        divisor = freq_dict[frecuencia]
        seguro_unitario = (saldo_referencia / 1000) * porcentaje_seguro * 12 / divisor

    cuotas_con_seguro = n_pagos - pagos_por_año
    saldo = monto
    datos = []

    if tipo_cuota == 'Nivelada':
        for i in range(1, n_pagos + 1):
            interes = saldo * tasa_periodo
            abono = cuota_base - interes
            saldo -= abono
            saldo = max(saldo, 0)
            seguro_aplicado = seguro_unitario if incluir_seguro == 'Sí' and i <= cuotas_con_seguro else 0
            cuota_total = cuota_base + seguro_aplicado

            datos.append({
                "Pago": i,
                "Cuota": cuota_total,
                "Interés": interes,
                "Abono": abono,
                "Seguro": seguro_aplicado,
                "Saldo": saldo
            })
    else:
        abono_fijo = monto / n_pagos
        for i in range(1, n_pagos + 1):
            interes = saldo * tasa_periodo
            cuota_base = abono_fijo + interes
            saldo -= abono_fijo
            saldo = max(saldo, 0)
            seguro_aplicado = seguro_unitario if incluir_seguro == 'Sí' and i <= cuotas_con_seguro else 0
            cuota_total = cuota_base + seguro_aplicado

            datos.append({
                "Pago": i,
                "Cuota": cuota_total,
                "Interés": interes,
                "Abono": abono_fijo,
                "Seguro": seguro_aplicado,
                "Saldo": saldo
            })

    df = pd.DataFrame(datos)
    return df

# Panel de entrada
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

    st.markdown("---")
    calcular = st.form_submit_button("🔍 Calcular cuotas")

# Resultado
if calcular:
    st.subheader("📊 Resultados:")
    st.markdown(f"**Monto del préstamo:** Lps. {monto:,.2f}  \n**Tasa anual:** {tasa:.2f}%  \n**Plazo:** {plazo} meses")

    df_resultado = calcular_cuotas_df(monto, tasa, plazo, frecuencia, tipo_cuota, incluir_seguro, porcentaje_seguro)

    # Formatear los valores con separador de miles
    df_format = df_resultado.copy()
    for col in ["Cuota", "Interés", "Abono", "Seguro", "Saldo"]:
        df_format[col] = df_format[col].apply(lambda x: f"Lps. {x:,.2f}")

    st.subheader("🧾 Tabla de amortización:")
    st.dataframe(df_format, use_container_width=True)
