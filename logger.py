from datetime import datetime
import os
import pandas as pd
import tinytuya

# Leemos las credenciales de forma segura desde GitHub
API_REGION = "us"
API_ID = os.getenv("API_ID")
API_SECRET = os.getenv("API_SECRET")
DEVICE_ID = os.getenv("DEVICE_ID")
CSV_FILE = "historico_energia.csv"

print("🤖 Consultando la nube de Tuya...")

try:
  cloud = tinytuya.Cloud(
      apiRegion=API_REGION, apiKey=API_ID, apiSecret=API_SECRET
  )
  status = cloud.getstatus(DEVICE_ID)
  properties = cloud.getproperties(DEVICE_ID)
  print(f"🔍 DEBUG - Especificación del dispositivo (escalas/unidades): {properties}")

  if status and "result" in status:
    dps_data = {item["code"]: item["value"] for item in status["result"]}
    print(f"🔍 DEBUG - Todos los campos del dispositivo: {dps_data}")
    potencia = float(dps_data.get("cur_power", 0))
    timestamp = pd.Timestamp.now()

    # Si ya existe el CSV lo abrimos, si no, creamos uno nuevo
    if os.path.exists(CSV_FILE):
      df = pd.read_csv(CSV_FILE, parse_dates=["Fecha y Hora"])
    else:
      df = pd.DataFrame(columns=["Fecha y Hora", "Potencia (W)", "Energía Acumulada (kWh)"])

    # Si el CSV es de antes de trackear energía, calculamos el acumulado
    # histórico por regla trapezoidal (promedio de potencia entre lecturas
    # consecutivas por el tiempo transcurrido)
    if "Energía Acumulada (kWh)" not in df.columns:
      acumulado = [0.0] * len(df)
      for i in range(1, len(df)):
        horas = (df.loc[i, "Fecha y Hora"] - df.loc[i - 1, "Fecha y Hora"]).total_seconds() / 3600
        potencia_promedio = (df.loc[i - 1, "Potencia (W)"] + df.loc[i, "Potencia (W)"]) / 2
        acumulado[i] = acumulado[i - 1] + (potencia_promedio * horas) / 1000
      df["Energía Acumulada (kWh)"] = acumulado

    # Calculamos el consumo desde la última lectura (regla trapezoidal)
    if len(df) > 0:
      ultima_fecha = df.iloc[-1]["Fecha y Hora"]
      ultima_potencia = df.iloc[-1]["Potencia (W)"]
      ultima_energia = df.iloc[-1]["Energía Acumulada (kWh)"]
      horas_transcurridas = (timestamp - ultima_fecha).total_seconds() / 3600
      potencia_promedio = (ultima_potencia + potencia) / 2
      energia_acumulada = ultima_energia + (potencia_promedio * horas_transcurridas) / 1000
    else:
      energia_acumulada = 0.0

    # Añadimos la nueva lectura
    nuevo_dato = pd.DataFrame(
        [{
            "Fecha y Hora": timestamp,
            "Potencia (W)": potencia,
            "Energía Acumulada (kWh)": round(energia_acumulada, 6),
        }]
    )
    df = pd.concat([df, nuevo_dato], ignore_index=True)

    # Guardamos los cambios
    df.to_csv(CSV_FILE, index=False)
    print(f"¡Lectura guardada con éxito: {potencia} W | Acumulado: {energia_acumulada:.4f} kWh!")
  else:
    print("Error: No se pudo obtener el estado de la nube.")

except Exception as e:
  print(f"Ocurrió un error: {e}")
