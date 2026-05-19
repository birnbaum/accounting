import urllib.request
import urllib.parse
import json
import csv
import time
import os

ZONES = [
    "DE", "US-CAL-CISO", "IE", "US-TEX-ERCO", "DK"
]

# The API only allows downloading 10 days of past data at a time.
# April has 30 days, so we split it into 3 batches of 10 days each.
BATCHES = [
    ("2026-05-01T00:00:00.000Z", "2026-05-11T00:00:00.000Z")
]

AUTH_TOKEN = "ZJdkEgYRNNuhWB7Xnqss"

def fetch_data(zone, start, end):
    url = (
        f"https://api.electricitymaps.com/v3/carbon-intensity/past-range"
        f"?zone={zone}"
        f"&start={urllib.parse.quote(start)}"
        f"&end={urllib.parse.quote(end)}"
        f"&temporalGranularity=hourly"
    )
    
    req = urllib.request.Request(
        url, 
        headers={
            "auth-token": AUTH_TOKEN,
            "User-Agent": "curl/7.81.0"
        }
    )
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            # The API typically returns a dictionary with a "data" list
            return data.get("data", [])
    except Exception as e:
        print(f"Error fetching data for {zone} ({start} - {end}): {e}")
        return []

def main():
    # Make sure we write output into the script's directory (./data)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "carbon_intensity_2026-05_10d.csv")

    # A dictionary to hold pivoted data: { datetime: { "datetime": dt, "region1": val, ... } }
    data_by_time = {}

    for zone in ZONES:
        print(f"Fetching data for zone: {zone}")
        zone_data = []
        for start, end in BATCHES:
            print(f"  Batch: {start} to {end}")
            batch_data = fetch_data(zone, start, end)
            zone_data.extend(batch_data)
            time.sleep(1) # Be a good API citizen and rate-limit slightly
        
        # Add to data_by_time
        for entry in zone_data:
            dt = entry.get("datetime")
            intensity = entry.get("carbonIntensity")
            if dt not in data_by_time:
                data_by_time[dt] = {"datetime": dt}
            data_by_time[dt][zone] = intensity

    if not data_by_time:
        print("No data was fetched. Please check the API token or your connection.")
        return

    # Sort data by datetime
    sorted_data = sorted(data_by_time.values(), key=lambda x: x["datetime"])

    # Write all downloaded data into a single CSV
    fieldnames = ["datetime"] + ZONES
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted_data:
            writer.writerow(row)
            
    print(f"\nSuccessfully saved data to {output_file}")

if __name__ == "__main__":
    main()
