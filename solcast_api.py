import requests
import pandas as pd
import os
from datetime import datetime
from zoneinfo import ZoneInfo
API_KEY = os.getenv("SOLCAST_API_KEY")
LATITUDE = float(os.getenv("SOLCAST_LATITUDE"))
LONGITUDE = float(os.getenv("SOLCAST_LONGITUDE"))
RESOURCE_ID = os.getenv("SOLCAST_RESOURCE_ID")
webapp_url = os.environ["GDRIVE_WEBAPP_URL"]
upload_token = os.environ["GDRIVE_UPLOAD_TOKEN"]
# Download irradiance forecast
url = "https://api.solcast.com.au/data/forecast/radiation_and_weather"
params = {
    "latitude": LATITUDE,    
    "longitude": LONGITUDE,
    "output_parameters": "gti,ghi,dni,dhi,air_temp,albedo,relative_humidity,wind_speed_10m,wind_direction_10m",
    "period": "PT5M",
    "hours": 336,
    "format": "json"
}
headers = {
    "Authorization": f"Bearer {API_KEY}"
}
response = requests.get(url, params=params, headers=headers)
print(response.status_code)
response.raise_for_status()
data = response.json()
df = pd.DataFrame(data["forecasts"])
df["period_end"] = (pd.to_datetime(df["period_end"], utc=True))
# Download power forecast
power_url = "https://api.solcast.com.au/data/forecast/premium_pv_power"
power_params = {
    "resource_id": RESOURCE_ID,
    "output_parameters": "power,power_p10,power_p25,power_p75,power_p90",
    "period": "PT5M",
    "hours": 336,
    "format": "json"
}
power_response = requests.get(power_url, params=power_params, headers=headers)
power_response.raise_for_status()
power_data = power_response.json()
power_df = pd.DataFrame(power_data["forecasts"])
power_df["period_end"] = (pd.to_datetime(power_df["period_end"], utc=True))
# Merge
df = df.merge(
    power_df[
        ["period_end", "power", "power_p10", "power_p25", "power_p75", "power_p90"]
    ],
    on="period_end",
    how="left"
)
df["period_end"] = (
    df["period_end"]
      .dt.tz_convert("Asia/Colombo")
      .dt.strftime("%Y-%m-%d %H:%M:%S")
)
# Create the output folder if it doesn't exist
os.makedirs("data", exist_ok=True)
# Get the current Sri Lankan time
timestamp = datetime.now(
    ZoneInfo("Asia/Colombo")
).strftime("%Y-%m-%d_%H-%M")
# Create the filename
filename = f"data/solcast_forecast_{timestamp}.csv"
# Save the CSV
df.to_csv(filename, index=False)
print(f"Saved to {filename}")
# --------------------------------------------
# Create/update rolling forecast CSV
# --------------------------------------------

rolling_file = "data/rolling_forecast.csv"

# Take only the first 3 forecast timestamps
rolling_df = df.head(3).copy()

# Append to existing rolling CSV if it exists
if os.path.exists(rolling_file):
    existing_df = pd.read_csv(rolling_file)
    rolling_df = pd.concat([existing_df, rolling_df], ignore_index=True)

# Save updated rolling CSV
rolling_df.to_csv(rolling_file, index=False)

print(f"Updated {rolling_file}")
# --- Upload to Google Drive, then stop — no git commit ---
for file in [filename, rolling_file]:

    with open(file, "rb") as f:
        csv_content = f.read()

    upload = requests.post(
        f"{webapp_url}?filename={os.path.basename(file)}&token={upload_token}",
        data=csv_content,
        headers={"Content-Type": "text/csv"},
        timeout=30
    )

    if upload.status_code >= 400 or "OK" not in upload.text:
        print(f"Upload failed: {upload.status_code}")
        print(upload.text)
        upload.raise_for_status()

    print(f"Uploaded {os.path.basename(file)} to Google Drive")
