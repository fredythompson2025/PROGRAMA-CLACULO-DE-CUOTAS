import streamlit as st
import pandas as pd
import numpy as np

st.title("Calculadora de Cuotas de Préstamo")

# Entradas del usuario
monto = st.number_input("Monto del préstamo", min_value=0.0, value=50000.0, step=1000.0)
tasa_interes_anual = st.number_input("Tasa de interés anual (%)", min_value=0.0, value=12.0, step=0.1)
plazo = st.number_input("Plazo (en meses)", min_value=1, value=12)
seguro_porcentaje = st.number_input("Porcentaje de seguro (%)", min_value=0.0, value=2.80, step=0.01)

# Calcular cuota mensual nivelada
tasa_mensual = tasa_interes_anual / 100 / 12
cuota = monto * (tasa_mensual * (1 + tasa_mensual)**plazo) / ((1 + tasa_mensual)**plazo - 1)

# Calcular seguro
seguro_base = monto * (seguro_porcentaje / 100)
impuesto = seguro_base * 0.15
bomberos = seguro_base * 0.05
papeleria = 50.0
seguro_total = seguro_base + impuesto + bomberos + papeleria
seguro_mensual = seguro_total / 12

# Mostrar resultados
st.subheader("Resultados")
st.write(f"💰 Cuota mensual: **L. {cuota:,.2f}**")
st.write(f"🛡️ Seguro anual total: **L. {seguro_total:,.2f}**")
st.write(f"🧾 Pago mensual de seguro: **L. {seguro_mensual:,.2f}**")
st.write(f"📦 Cuota total mensual (préstamo + seguro): **L. {cuota + seguro_mensual:,.2f}**")

# Generar tabla de amortización
st.subheader("Tabla de Amortización (Resumen)")
saldo = monto
tabla = []
for i in range(1, plazo + 1):
    interes = saldo * tasa_mensual
    abono_capital = cuota - interes
    saldo -= abono_capital
    tabla.append([i, cuota, abono_capital, interes, saldo if saldo > 0 else 0.0])

df = pd.DataFrame(tabla, columns=["Mes", "Cuota", "Abono a Capital", "Interés", "Saldo Restante"])
st.dataframe(df.style.format({"Cuota": "L. {:.2f}", "Abono a Capital": "L. {:.2f}", "Interés": "L. {:.2f}", "Saldo Restante": "L. {:.2f}"}))
