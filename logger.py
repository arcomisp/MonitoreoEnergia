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

  if status and "result" in status:
    dps_data = {item["code"]: item["value"] for item in status["result"]}
    potencia = float(dps_data.get("cur_power", 0))
    timestamp = pd.Timestamp.now()

    # Si ya existe el CSV lo abrimos, si no, creamos uno nuevo
    if os.path.exists(CSV_FILE):
      df = pd.read_csv(CSV_FILE)
    else:
      df = pd.DataFrame(columns=["Fecha y Hora", "Potencia (W)"])

    # Añadimos la nueva lectura
    nuevo_dato = pd.DataFrame(
        [{"Fecha y Hora": timestamp, "Potencia (W)": potencia}]
    )
    df = pd.concat([df, nuevo_dato], ignore_index=True)

    # Guardamos los cambios
    df.to_csv(CSV_FILE, index=False)
    print(f"¡Lectura guardada con éxito: {potencia} W!")
  else:
    print("Error: No se pudo obtener el estado de la nube.")

except Exception as e:
  print(f"Ocurrió un error: {e}")
