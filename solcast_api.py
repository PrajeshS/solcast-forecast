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
