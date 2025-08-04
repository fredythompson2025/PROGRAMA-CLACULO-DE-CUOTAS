import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Cuotas de Préstamo", layout="centered")
st.markdown("""
    <div style='text-align: center;'>
        <img src='https://cdn-icons-png.flaticon.com/512/2910/2910768.png' width='80'/>
        <h1 style='color: #003366;'>Cuotas de Préstamo</h1>
    </div>
""", unsafe_allow_html=True)
st.markdown("##")

def calcular_seguro_dano(papeleria):
    total_anual = papeleria
    pago_mensual = total_anual / 12
    return total_anual, pago_mensual

def calcular_cuotas_df(monto, tasa_anual, plazo_meses, frecuencia, tipo_cuota,
                       incluir_seguro, porcentaje_seguro,
                       incluir_seguro_dano, pago_mensual_seguro_dano):
    freq_dict = {
        'Mensual': 12,
        'Bimensual': 6,
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
        seguro_prestamo = 0
        seguro_dano = pago_mensual_seguro_dano if incluir_seguro_dano == 'Sí' else 0
        cuota_total = interes + abono + seguro_prestamo + seguro_dano

        fila = {
            "Pago": 1,
            "Cuota": cuota_total,
            "Interés": interes,
            "Abono": abono,
            "Seguro Préstamo": seguro_prestamo,
            "Saldo": 0
        }
        if incluir_seguro_dano == 'Sí':
            fila["Seguro Daño"] = seguro_dano
        return pd.DataFrame([fila])

    n_pagos = int(plazo_meses * pagos_por_año / 12)
    tasa_periodo = tasa_anual / 100 / pagos_por_año
    saldo = monto

    ref_cuota_dict = {'Mensual': 12, 'Bimensual': 6, 'Trimestral': 4, 'Semestral': 2, 'Anual': 1}
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

    seguro_prestamo_unitario = 0
    if incluir_seguro == 'Sí':
        divisor = freq_dict[frecuencia]
        seguro_prestamo_unitario = (saldo_referencia / 1000) * porcentaje_seguro * 12 / divisor

    cuotas_con_seguro = n_pagos - pagos_por_año
    saldo = monto
    datos = []

    for i in range(1, n_pagos + 1):
        interes = saldo * tasa_periodo
        if tipo_cuota == 'Nivelada':
            abono = cuota_base - interes
            cuota_base_calc = cuota_base
        else:
            abono = monto / n_pagos
            cuota_base_calc = abono + interes

        saldo -= abono
        saldo = max(saldo, 0)

        seguro_prestamo = seguro_prestamo_unitario if incluir_seguro == 'Sí' and i <= cuotas_con_seguro else 0
        seguro_dano = pago_mensual_seguro_dano if incluir_seguro_dano == 'Sí' else 0

        cuota_total = cuota_base_calc + seguro_prestamo + seguro_dano

        fila = {
            "Pago": i,
            "Cuota": cuota_total,
            "Interés": interes,
            "Abono": abono,
            "Seguro Préstamo": seguro_prestamo,
            "Saldo": saldo
        }

        if incluir_seguro_dano == 'Sí':
            fila["Seguro Daño"] = seguro_dano

        datos.append(fila)

    return pd.DataFrame(datos)

# Panel de entrada
with st.form("formulario"):
    col1, col2 = st.columns(2)

    with col1:
        monto = st.number_input("💰 Monto del préstamo", value=10000.0, step=100.0, format="%.2f")
        tasa = st.number_input("📈 Tasa de interés anual (%)", value=12.0, step=0.1)
        plazo = st.number_input("🗕 Plazo (meses)", value=36, step=1)

    with col2:
        frecuencia = st.selectbox("🗖 Frecuencia de pago", ['Mensual', 'Bimensual', 'Trimestral', 'Semestral', 'Anual', 'Al vencimiento'])
        tipo_cuota = st.selectbox("🔁 Tipo de cuota", ['Nivelada', 'Saldos Insolutos'])
        incluir_seguro = st.selectbox("🛡 ¿Incluir seguro préstamo?", ['No', 'Sí'])
        porcentaje_seguro = st.number_input("📌 % Seguro préstamo por cada Lps. 1,000", value=0.50, step=0.01)

        incluir_seguro_dano = st.selectbox("🛡 ¿Incluir seguro daño?", ['No', 'Sí'])
        papeleria_dano = st.number_input("📌 Costo fijo seguro daño (anual)", value=0.0, step=1.0)

    st.markdown("---")
    calcular = st.form_submit_button("🔍 Calcular cuotas")

if calcular:
    if incluir_seguro_dano == 'Sí':
        total_anual, pago_mensual = calcular_seguro_dano(papeleria_dano)

        st.markdown(f"### Detalle Seguro de Daño:")
        st.write(f"Papelería: Lps. {papeleria_dano:,.2f}")
        st.write(f"**Total anual:** Lps. {total_anual:,.2f}")
        st.write(f"**Pago mensual:** Lps. {pago_mensual:,.2f}")
    else:
        pago_mensual = 0.0

    df_resultado = calcular_cuotas_df(
        monto, tasa, plazo, frecuencia, tipo_cuota,
        incluir_seguro, porcentaje_seguro,
        incluir_seguro_dano, pago_mensual)

    cuota_final = df_resultado["Cuota"].iloc[0]
    st.info(f"💵 **Cuota a pagar:** Lps. {cuota_final:,.2f}")

    df_format = df_resultado.copy()

    for col in ["Cuota", "Interés", "Abono", "Seguro Préstamo", "Saldo"]:
        df_format[col] = df_format[col].apply(lambda x: f"Lps. {x:,.2f}")

    if incluir_seguro_dano == 'Sí' and "Seguro Daño" in df_format.columns:
        df_format["Seguro Daño"] = df_resultado["Seguro Daño"].apply(lambda x: f"Lps. {x:,.2f}")
    elif "Seguro Daño" in df_format.columns:
        df_format.drop("Seguro Daño", axis=1, inplace=True)

    st.subheader("🧾 Tabla de amortización:")
    st.dataframe(df_format, use_container_width=True)
