import polars as pl
import requests
import os
from datetime import datetime

# 1. Configuration
DATA_FOLDER = "data"
WEATHER_FILE = f"{DATA_FOLDER}/weather.parquet"

# Coordinates for all 13 States + 3 Federal Territories Capitals
LOCATIONS = {
    "Kuala Lumpur": {"lat": 3.1390, "lon": 101.6869},  # FT Kuala Lumpur
    "Putrajaya": {"lat": 2.9264, "lon": 101.6964},     # FT Putrajaya
    "Labuan": {"lat": 5.2831, "lon": 115.2308},        # FT Labuan
    "Alor Setar": {"lat": 6.1210, "lon": 100.3601},    # Kedah
    "George Town": {"lat": 5.4141, "lon": 100.3288},   # Penang
    "Ipoh": {"lat": 4.5975, "lon": 101.0901},          # Perak
    "Kangar": {"lat": 6.4449, "lon": 100.2048},        # Perlis
    "Kota Bharu": {"lat": 6.1254, "lon": 102.2386},    # Kelantan
    "Kuala Terengganu": {"lat": 5.3302, "lon": 103.1408}, # Terengganu
    "Kuantan": {"lat": 3.8077, "lon": 103.3260},       # Pahang
    "Shah Alam": {"lat": 3.0738, "lon": 101.5183},     # Selangor
    "Seremban": {"lat": 2.7258, "lon": 101.9424},      # Negeri Sembilan
    "Melaka": {"lat": 2.1896, "lon": 102.2501},        # Melaka
    "Johor Bahru": {"lat": 1.4854, "lon": 103.7618},   # Johor
    "Kuching": {"lat": 1.5533, "lon": 110.3592},       # Sarawak
    "Kota Kinabalu": {"lat": 5.9788, "lon": 116.0753}  # Sabah
}

def fetch_weather():
    """Fetch 3-day forecast for major cities from Open-Meteo."""
    print(f"🌦️ Fetching weather for {len(LOCATIONS)} locations...")
    
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    all_weather = []

    for city, coords in LOCATIONS.items():
        try:
            # Fixing typo in LOCATIONS: llon -> lon
            lon = coords.get("lon") or coords.get("llon")
            
            # API: Open-Meteo (Free, no key)
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": coords["lat"],
                "longitude": lon,
                "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
                "timezone": "Asia/Singapore",
                "forecast_days": 3
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            daily = data["daily"]
            for i in range(len(daily["time"])):
                all_weather.append({
                    "city": city,
                    "date": daily["time"][i],
                    "weather_code": daily["weather_code"][i],
                    "temp_max": daily["temperature_2m_max"][i],
                    "temp_min": daily["temperature_2m_min"][i],
                    "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            
            print(f"✅ {city} data fetched.")
        except Exception as e:
            print(f"❌ Failed to fetch weather for {city}: {e}")

    if all_weather:
        df = pl.DataFrame(all_weather)
        df.write_parquet(WEATHER_FILE)
        print(f"💾 Saved {len(all_weather)} forecasts to {WEATHER_FILE}")

if __name__ == "__main__":
    fetch_weather()
