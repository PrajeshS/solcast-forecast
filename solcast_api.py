import requests
import csv


# API endpoint
url = "https://api.solcast.com.au/data/forecast/premium_pv_power"

# Parameters

params = {
    "resource_id": "7f72-69a6-9138-089",
    "api_key": "Ltmj-pqWaCVKTAni0yrsexlj3ZKMUv_S",
    "output_parameters": "power,power_p10,power_p90",
    "period": "PT5M",
    "hours": 24,
    "format": "json"
}

try:
    print("🔄 Fetching data from Solcast...")

    response = requests.get(url, params=params)
    print(response.url)
    
    response.raise_for_status()

    data = response.json()
    forecasts = data["forecasts"]

    print("✅ Data received!\n")

    # Print first 10 rows
    for f in forecasts[:10]:
        print(f"{f['period_end']} -> {f['power']} kW")

    # Save CSV
    with open("forecast.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "Power", "P10", "P90"])

        for f in forecasts:
            writer.writerow([
                f["period_end"],
                f["power"],
                f["power_p10"],
                f["power_p90"]
            ])

    print("\n✅ CSV file saved as forecast.csv")

except requests.exceptions.RequestException as e:
    print("Error:", e)