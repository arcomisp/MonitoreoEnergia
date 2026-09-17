import os
import sys

import pandas as pd
import tinytuya

# Leemos las credenciales de forma segura desde GitHub
API_REGION = "us"
API_ID = os.getenv("API_ID")
API_SECRET = os.getenv("API_SECRET")
DEVICE_ID = os.getenv("DEVICE_ID")
CSV_FILE = "historico_energia.csv"

print("🤖 Trayendo el histórico disponible desde la nube de Tuya...")

cloud = tinytuya.Cloud(apiRegion=API_REGION, apiKey=API_ID, apiSecret=API_SECRET)

# Tuya solo retiene los logs un tiempo limitado (varía según el plan del
# proyecto); pedimos un rango generoso y dejamos que la nube devuelva lo que
# realmente tenga disponible.
ret = cloud.getdevicelog(
    deviceid=DEVICE_ID,
    start=-365,
    end=0,
    evtype=7,  # 7 = reportes de DPs (valores del dispositivo)
    size=0,
    max_fetches=200,
)

if not ret or "result" not in ret:
    print(f"Error consultando el histórico: {ret}")
    sys.exit(1)

logs = ret["result"].get("logs", [])
lecturas = []
for log in logs:
    if log.get("code") != "cur_power":
        continue
    try:
        potencia = float(log["value"])
    except (TypeError, ValueError):
        continue
    timestamp = pd.to_datetime(int(log["event_time"]), unit="ms")
    lecturas.append({"Fecha y Hora": timestamp, "Potencia (W)": potencia})

print(f"Tuya devolvió {len(logs)} eventos; {len(lecturas)} son lecturas de potencia (cur_power).")

if os.path.exists(CSV_FILE):
    df_actual = pd.read_csv(CSV_FILE, parse_dates=["Fecha y Hora"])[["Fecha y Hora", "Potencia (W)"]]
else:
    df_actual = pd.DataFrame(columns=["Fecha y Hora", "Potencia (W)"])

df_historico = pd.DataFrame(lecturas, columns=["Fecha y Hora", "Potencia (W)"])
df = pd.concat([df_actual, df_historico], ignore_index=True)
df = df.drop_duplicates(subset="Fecha y Hora").sort_values("Fecha y Hora").reset_index(drop=True)

# Recalculamos la energía acumulada desde cero (regla trapezoidal)
acumulado = [0.0] * len(df)
for i in range(1, len(df)):
    horas = (df.loc[i, "Fecha y Hora"] - df.loc[i - 1, "Fecha y Hora"]).total_seconds() / 3600
    potencia_promedio = (df.loc[i - 1, "Potencia (W)"] + df.loc[i, "Potencia (W)"]) / 2
    acumulado[i] = acumulado[i - 1] + (potencia_promedio * horas) / 1000
df["Energía Acumulada (kWh)"] = acumulado

df.to_csv(CSV_FILE, index=False)

if len(df) > 0:
    print(
        f"CSV actualizado: {len(df)} lecturas en total, "
        f"desde {df.iloc[0]['Fecha y Hora']} hasta {df.iloc[-1]['Fecha y Hora']}."
    )
else:
    print("No se encontraron lecturas para guardar.")
