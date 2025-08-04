import streamlit as st
import numpy as np

st.set_page_config(page_title="programa de calculo de Cuotas", layout="centered")
st.markdown("<h1 style='text-align: center; color: #003366;'>Cuotas de Préstamo</h1>", unsafe_allow_html=True)
st.markdown("##")

def calcular_cuotas(monto, tasa_anual, plazo_meses, frecuencia, tipo_cuota, incluir_seguro, porcentaje_seguro):
    freq_dict = {
        'Mensual': 12,
        'Trimestral': 4,
        'Semestral': 2,
        'Anual': 1,
        'Al vencimiento': 0
    }

    pagos_por_año = freq_dict.get(frecuencia)
    if pagos_por_año == 0:
        tasa_total = tasa_anual / 100 * (plazo_meses / 12)
        interes = monto * tasa_total
        abono = monto
        seguro = 0
        cuota_total = interes + abono
        lines = [f"{'Pago':<5} {'Cuota':<15} {'Interés':<15} {'Abono':<15} {'Seguro':<15} {'Saldo':<15}"]
        lines.append(f"{1:<5} {cuota_total:>15,.2f} {interes:>15,.2f} {abono:>15,.2f} {seguro:>15,.2f} {0.0:>15,.2f}")
        return "\n".join(lines)

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
    if incluir_seguro == 'Sí' and frecuencia != 'Al vencimiento':
        divisor = freq_dict[frecuencia]
        seguro_unitario = (saldo_referencia / 1000) * porcentaje_seguro * 12 / divisor

    cuotas_con_seguro = n_pagos - pagos_por_año
    saldo = monto
    lines = [f"{'Pago':<5} {'Cuota':<15} {'Interés':<15} {'Abono':<15} {'Seguro':<15} {'Saldo':<15}"]

    if tipo_cuota == 'Nivelada':
        for i in range(1, n_pagos + 1):
            interes = saldo * tasa_periodo
            abono = cuota_base - interes
            saldo -= abono
            saldo = max(saldo, 0)
            seguro_aplicado = seguro_unitario if (incluir_seguro == 'Sí' and i <= cuotas_con_seguro) else 0
            cuota_total = cuota_base + seguro_aplicado
            lines.append(
                f"{i:<5} {cuota_total:>15,.2f} {interes:>15,.2f} {abono:>15,.2f} {seguro_aplicado:>15,.2f} {saldo:>15,.2f}"
            )
    else:
        abono_fijo = monto / n_pagos
        for i in range(1, n_pagos + 1):
            interes = saldo * tasa_periodo
            cuota_base = abono_fijo + interes
            saldo -= abono_fijo
            saldo = max(saldo, 0)
            seguro_aplicado = seguro_unitario if (incluir_seguro == 'Sí' and i <= cuotas_con_seguro) else 0
            cuota_total = cuota_base + seguro_aplicado
            lines.append(
                f"{i:<5} {cuota_total:>15,.2f} {interes:>15,.2f} {abono_fijo:>15,.2f} {seguro_aplicado:>15,.2f} {saldo:>15,.2f}"
            )

    return "\n".join(lines)

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
    resultado = calcular_cuotas(monto, tasa, plazo, frecuencia, tipo_cuota, incluir_seguro, porcentaje_seguro)
    st.subheader("🧾 Tabla de amortización:")
    st.code(resultado)
