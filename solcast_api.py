import requests
import pandas as pd
import os
from datetime import datetime
from zoneinfo import ZoneInfo

API_KEY = "Ltmj-pqWaCVKTAni0yrsexlj3ZKMUv_S"

url = "https://api.solcast.com.au/data/forecast/radiation_and_weather"

params = {
    "latitude": 6.9271,    
    "longitude": 79.8612,
    "output_parameters": "ghi,dni,dhi,air_temp",
    "period": "PT5M",
    "hours": 336,
    "format": "json"
}

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

response = requests.get(url, params=params, headers=headers)
response.raise_for_status()
data = response.json()
df = pd.DataFrame(data["forecasts"])
# ----------------------------
# Download power forecast
# ----------------------------

power_url = "https://api.solcast.com.au/data/forecast/premium_pv_power"

power_params = {
    "resource_id": "7f72-69a6-9138-089",
    "output_parameters": "power,power_p10,power_p90",
    "period": "PT5M",
    "hours": 24,
    "format": "json"
}

power_response = requests.get(
    power_url,
    params=power_params,
    headers=headers,
    timeout=30
)
power_response.raise_for_status()

power_data = power_response.json()

power_df = pd.DataFrame(power_data["forecasts"])
df = df.merge(
    power_df[
        ["period_end", "power", "power_p10", "power_p90"]
    ],
    on="period_end",
    how="left"
)
print(df.head())

# Create the output folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# Get the current Sri Lankan time
timestamp = datetime.now(
    ZoneInfo("Asia/Colombo")
).strftime("%Y-%m-%d_%H-%M")

# Create the filename
filename = f"data/irradiance_forecast_{timestamp}.csv"

# Save the CSV
df.to_csv(filename, index=False)

print(f"Saved to {filename}")
