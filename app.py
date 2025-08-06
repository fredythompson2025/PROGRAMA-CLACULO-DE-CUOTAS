import streamlit as st
import pandas as pd
import io
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

st.title("🧮 Calculadora de Cuotas Avanzada")

# Entradas del usuario
monto = st.number_input("💰 Monto del préstamo", min_value=0.0, value=100000.0, step=1000.0)
tasa_anual = st.number_input("📈 Tasa de interés anual (%)", min_value=0.0, value=12.0, step=0.1)
plazo_total_meses = st.number_input("📅 Plazo total (en meses)", min_value=1, value=12)

frecuencia = st.selectbox(
    "🔁 Frecuencia de pago",
    [
        "Diario", "Semanal", "Quincenal", "Mensual", "Bimensual", "Trimestral",
        "Cuatrimestral", "Semestral", "Anual", "Al vencimiento"
    ]
)

tipo_cuota = st.selectbox("📊 Tipo de cuota", ["Cuota nivelada", "Saldos insolutos"])
seguro_porcentaje = st.number_input("🛡️ Porcentaje de seguro (%)", min_value=0.0, value=2.80, step=0.01)

# Configuración de frecuencias
frecuencias = {
    "Diario": 360,
    "Semanal": 52,
    "Quincenal": 24,
    "Mensual": 12,
    "Bimensual": 6,
    "Trimestral": 4,
    "Cuatrimestral": 3,
    "Semestral": 2,
    "Anual": 1,
    "Al vencimiento": 1
}

pagos_por_año = frecuencias[frecuencia]
tasa_periodica = tasa_anual / 100 / pagos_por_año
plazo_en_pagos = int(plazo_total_meses * (pagos_por_año / 12))

# Cálculo de cuota
if tipo_cuota == "Cuota nivelada" and frecuencia != "Al vencimiento":
    cuota = monto * (tasa_periodica * (1 + tasa_periodica)**plazo_en_pagos) / ((1 + tasa_periodica)**plazo_en_pagos - 1)
else:
    cuota = None

# Seguro
seguro_base = monto * (seguro_porcentaje / 100)
impuesto = seguro_base * 0.15
bomberos = seguro_base * 0.05
papeleria = 50.0
seguro_total = seguro_base + impuesto + bomberos + papeleria
seguro_periodico = seguro_total / plazo_en_pagos if plazo_en_pagos > 0 else 0.0

# Generar tabla
saldo = monto
tabla = []

for i in range(1, plazo_en_pagos + 1):
    interes = saldo * tasa_periodica

    if frecuencia == "Al vencimiento":
        abono_capital = 0.0 if i < plazo_en_pagos else monto
        cuota = interes if i < plazo_en_pagos else interes + monto
    elif tipo_cuota == "Cuota nivelada":
        abono_capital = cuota - interes
    else:
        abono_capital = monto / plazo_en_pagos
        cuota = abono_capital + interes

    saldo -= abono_capital
    saldo = max(0.0, saldo)
    cuota_total = cuota + seguro_periodico

    tabla.append([
        i, cuota, interes, abono_capital,
        seguro_periodico, cuota_total, saldo
    ])

# DataFrame
df = pd.DataFrame(tabla, columns=[
    "Período", "Cuota", "Interés", "Abono a Capital",
    "Seguro", "Pago Total", "Saldo Restante"
])

# Mostrar tabla
st.subheader("📄 Tabla de Amortización")
st.dataframe(df.style.format("L. {:.2f}"))

# Resumen
st.subheader("📊 Resumen")
st.write(f"🧾 Seguro total: **L. {seguro_total:,.2f}**")
if len(df) > 0:
    st.write(f"📦 Cuota inicial total (incluye seguro): **L. {df.iloc[0]['Pago Total']:,.2f}**")

# ========== BOTONES DE EXPORTACIÓN ==========
st.subheader("📁 Exportar o Imprimir")

# Excel
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Amortización", index=False)
st.download_button(
    label="📥 Descargar en Excel",
    data=excel_buffer.getvalue(),
    file_name="tabla_amortizacion.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# PDF
def generar_pdf(dataframe):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Tabla de Amortización", styles['Title']))
    elements.append(Spacer(1, 12))

    table_data = [list(dataframe.columns)] + dataframe.round(2).values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black)
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

pdf_data = generar_pdf(df)
st.download_button(
    label="📄 Descargar en PDF",
    data=pdf_data,
    file_name="tabla_amortizacion.pdf",
    mime="application/pdf"
)

# Botón de impresión
st.markdown("""
    <button onclick="window.print()" style="
        background-color:#4CAF50;
        color:white;
        padding:10px 20px;
        border:none;
        cursor:pointer;
        border-radius:5px;
        font-size:16px;
    ">🖨️ Imprimir</button>
    """, unsafe_allow_html=True)

