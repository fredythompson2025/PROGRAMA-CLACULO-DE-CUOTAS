import numpy as np
import ipywidgets as widgets
from IPython.display import display, clear_output

def calcular_cuotas(monto, tasa_anual, plazo_meses, frecuencia, tipo_cuota, incluir_seguro, porcentaje_seguro):
    freq_dict = {
        'Mensual': 12,
        'Trimestral': 4,
        'Semestral': 2,
        'Anual': 1,
        'Al vencimiento': 0
    }
    pagos_por_año = freq_dict.get(frecuencia)
    if pagos_por_año == 0:  # Al vencimiento
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
    ref_cuota = ref_cuota_dict.get(frecuencia, 1)
    ref_cuota = min(ref_cuota, n_pagos)

    saldo_referencia = monto
    if tipo_cuota == 'Nivelada':
        cuota_base = monto * (tasa_periodo * (1 + tasa_periodo) ** n_pagos) / ((1 + tasa_periodo) ** n_pagos - 1)
        for i in range(1, ref_cuota + 1):
            interes = saldo_referencia * tasa_periodo
            abono = cuota_base - interes
            saldo_referencia -= abono
    else:
        abono_fijo = monto / n_pagos
        for i in range(1, ref_cuota + 1):
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
            lines.append(f"{i:<5} {cuota_total:>15,.2f} {interes:>15,.2f} {abono:>15,.2f} {seguro_aplicado:>15,.2f} {saldo:>15,.2f}")
    else:
        abono_fijo = monto / n_pagos
        for i in range(1, n_pagos + 1):
            interes = saldo * tasa_periodo
            cuota_base = abono_fijo + interes
            saldo -= abono_fijo
            saldo = max(saldo, 0)
            seguro_aplicado = seguro_unitario if (incluir_seguro == 'Sí' and i <= cuotas_con_seguro) else 0
            cuota_total = cuota_base + seguro_aplicado
            lines.append(f"{i:<5} {cuota_total:>15,.2f} {interes:>15,.2f} {abono_fijo:>15,.2f} {seguro_aplicado:>15,.2f} {saldo:>15,.2f}")

    return "\n".join(lines)

# Widgets
monto_w = widgets.FloatText(value=10000, description='Monto:')
tasa_w = widgets.FloatText(value=12.0, description='Tasa %:')
plazo_w = widgets.IntText(value=36, description='Plazo (meses):')

frecuencia_w = widgets.Dropdown(
    options=['Mensual', 'Trimestral', 'Semestral', 'Anual', 'Al vencimiento'],
    description='Frecuencia:'
)

tipo_cuota_w = widgets.Dropdown(
    options=['Nivelada', 'Saldos Insolutos'],
    description='Tipo cuota:'
)

seguro_w = widgets.Dropdown(
    options=['No', 'Sí'],
    description='¿Seguro?'
)

porcentaje_seguro_w = widgets.FloatText(
    value=0.50,
    description='% Seguro:',
    step=0.01
)

output = widgets.Output()

def on_change(change):
    with output:
        clear_output()
        resultado = calcular_cuotas(
            monto_w.value,
            tasa_w.value,
            plazo_w.value,
            frecuencia_w.value,
            tipo_cuota_w.value,
            seguro_w.value,
            porcentaje_seguro_w.value
        )
        print(resultado)

for w in [monto_w, tasa_w, plazo_w, frecuencia_w, tipo_cuota_w, seguro_w, porcentaje_seguro_w]:
    w.observe(on_change, names='value')

display(monto_w, tasa_w, plazo_w, frecuencia_w, tipo_cuota_w, seguro_w, porcentaje_seguro_w, output)

on_change(None)
