import streamlit as st
import pandas as pd
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

st.title("🧮 Calculadora de Cuotas Avanzada")

# Entradas del usuario
monto = st.number_input("💰 Monto del préstamo", min_value=0.0, value=100000.0, step=1000.0, format="%0.0f")
tasa_anual = st.number_input("📈 Tasa de interés anual (%)", min_value=0.0, value=12.0, step=0.1, format="%.2f")
plazo_total_meses = st.number_input("📅 Plazo total (en meses)", min_value=1, value=24, step=1)

frecuencia = st.selectbox(
    "🔁 Frecuencia de pago",
    [
        "Diario", "Semanal", "Quincenal", "Mensual", "Bimensual", "Trimestral",
        "Cuatrimestral", "Semestral", "Anual", "Al vencimiento"
    ]
)

tipo_cuota = st.selectbox("📊 Tipo de cuota", ["Cuota nivelada", "Saldos insolutos"])

# Opción para seguro
incluir_seguro = st.checkbox("¿Incluir seguro de préstamo?", value=True)
if incluir_seguro:
    seguro_porcentaje = st.number_input("🛡️ Porcentaje de seguro (%)", min_value=0.0, value=2.80, step=0.01, format="%.2f")
else:
    seguro_porcentaje = 0.0

if st.button("Calcular"):
    # Frecuencias y cálculos
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
    plazo_en_pagos = int(plazo_total_meses * pagos_por_año / 12)

    # Calcular cuota nivelada
    if tipo_cuota == "Cuota nivelada" and frecuencia != "Al vencimiento":
        cuota = monto * (tasa_periodica * (1 + tasa_periodica) ** plazo_en_pagos) / ((1 + tasa_periodica) ** plazo_en_pagos - 1)
    else:
        cuota = None

    saldo = monto
    tabla = []

    # Definimos el inicio del último año para evitar cobrar seguro allí
    pagos_ultimo_ano = pagos_por_año * 1  # número de pagos en un año
    inicio_ultimo_ano = plazo_en_pagos - pagos_ultimo_ano + 1  # primer periodo del último año

    for i in range(1, plazo_en_pagos + 1):
        interes = saldo * tasa_periodica

        if frecuencia == "Al vencimiento":
            abono_capital = 0.0 if i < plazo_en_pagos else monto
            cuota_actual = interes if i < plazo_en_pagos else interes + monto
        elif tipo_cuota == "Cuota nivelada":
            abono_capital = cuota - interes
            cuota_actual = cuota
        else:
            abono_capital = monto / plazo_en_pagos
            cuota_actual = abono_capital + interes

        # Seguro se cobra sólo en el inicio de cada año (periodos múltiplos de pagos_por_año + 1)
        # y nunca durante el último año
        if incluir_seguro and (i % pagos_por_año == 1) and (i < inicio_ultimo_ano):
            # El seguro se calcula sobre el saldo actual (al inicio de ese año)
            seguro_base = saldo * (seguro_porcentaje / 100)
            impuesto = seguro_base * 0.15
            bomberos = seguro_base * 0.05
            papeleria = 50.0
            seguro_actual = seguro_base + impuesto + bomberos + papeleria
        else:
            seguro_actual = 0.0

        saldo -= abono_capital
        saldo = max(0.0, saldo)
        cuota_total = cuota_actual + seguro_actual

        tabla.append([
            i, cuota_actual, interes, abono_capital,
            seguro_actual, cuota_total, saldo
        ])

    df = pd.DataFrame(tabla, columns=[
        "Período", "Cuota", "Interés", "Abono a Capital",
        "Seguro", "Pago Total", "Saldo Restante"
    ])

    st.subheader("📄 Tabla de Amortización")
    st.dataframe(df.style.format({
        "Cuota": "L. {:,.2f}",
        "Interés": "L. {:,.2f}",
        "Abono a Capital": "L. {:,.2f}",
        "Seguro": "L. {:,.2f}",
        "Pago Total": "L. {:,.2f}",
        "Saldo Restante": "L. {:,.2f}",
    }))

    seguro_cobrado = df["Seguro"].sum()
    st.subheader("📊 Resumen")
    st.write(f"🧾 Seguro total cobrado: **L. {seguro_cobrado:,.2f}**")
    if len(df) > 0:
        st.write(f"📦 Cuota inicial total (incluye seguro): **L. {df.iloc[0]['Pago Total']:,.2f}**")

    st.subheader("📁 Exportar o Imprimir")

    # Descargar Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Amortización", index=False)
    st.download_button(
        label="📥 Descargar en Excel",
        data=excel_buffer.getvalue(),
        file_name="tabla_amortizacion.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Función para PDF
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
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
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

    # Botón imprimir
    st.markdown("""
        <button onclick="window.print()" style="
            background-color:#4CAF50;
            color:white;
            padding:10px 20px;
            border:none;
            cursor:pointer;
            border-radius:5px;
            font-size:16px;
            margin-top:10px;
        ">🖨️ Imprimir</button>
        """, unsafe_allow_html=True)

