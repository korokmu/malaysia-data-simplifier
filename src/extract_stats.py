import polars as pl
from datetime import datetime
import json

def get_latest_stats():
    # 1. Fuel Stats
    df_fuel = pl.read_parquet("data/fuel_prices.parquet")
    df_fuel = df_fuel.filter(pl.col("series_type") == "level").sort("date", descending=True)
    
    # Calculate changes for the top 7 rows
    fuel_list = df_fuel.head(8).to_dicts() 
    for i in range(len(fuel_list) - 1):
        # Calculate diffs
        fuel_list[i]['ron95_chg'] = fuel_list[i]['ron95'] - fuel_list[i+1]['ron95']
        fuel_list[i]['ron97_chg'] = fuel_list[i]['ron97'] - fuel_list[i+1]['ron97']
        fuel_list[i]['diesel_chg'] = fuel_list[i]['diesel'] - fuel_list[i+1]['diesel']
        fuel_list[i]['diesel_e_chg'] = fuel_list[i]['diesel_eastmsia'] - fuel_list[i+1]['diesel_eastmsia']
        fuel_list[i]['budi_chg'] = fuel_list[i]['ron95_budi95'] - fuel_list[i+1]['ron95_budi95']
        # Convert objects to string for JSON
        fuel_list[i]['date'] = fuel_list[i]['date'].strftime('%d %b %Y')

    # 2. Exchange Stats
    df_ex = pl.read_parquet("data/exchange_rates.parquet").sort("date", descending=True)
    
    ex_list = df_ex.head(8).to_dicts()
    for i in range(len(ex_list) - 1):
        ex_list[i]['usd_chg'] = ex_list[i]['usd'] - ex_list[i+1]['usd']
        ex_list[i]['sgd_chg'] = ex_list[i]['sgd'] - ex_list[i+1]['sgd']
        ex_list[i]['eur_chg'] = ex_list[i]['eur'] - ex_list[i+1]['eur']
        ex_list[i]['gbp_chg'] = ex_list[i]['gbp'] - ex_list[i+1]['gbp']
        ex_list[i]['jpy_chg'] = ex_list[i]['jpy'] - ex_list[i+1]['jpy']
        ex_list[i]['aud_chg'] = ex_list[i]['aud'] - ex_list[i+1]['aud']
        ex_list[i]['cny_chg'] = ex_list[i]['cny'] - ex_list[i+1]['cny']
        
        # Convert JPY to 1-unit price for the dashboard display consistency (if BNM gives per 100)
        # We'll keep the value as is but label it 'JPY/100' in UI
        ex_list[i]['date'] = ex_list[i]['date'].strftime('%d %b %Y')

    # 3. Grocery Stats (Price Catcher)
    df_grocery = pl.read_parquet("data/pricecatcher.parquet")
    # Average per item per day
    df_grocery = (
        df_grocery.group_by(["date", "item_code"])
        .agg(pl.col("price").mean())
        .sort("date", descending=True)
    )
    
    ITEM_MAP = {
        "1":    ("Chicken",      "per kg"),
        "1109": ("Eggs Grd A",   "per 30 pcs"),
        "1110": ("Eggs Grd B",   "per 30 pcs"),
        "1111": ("Eggs Grd C",   "per 30 pcs"),
        "129":  ("Onions",       "per kg"),
        "114":  ("Tomato",       "per kg"),
        "94":   ("Red Chili",    "per kg"),
    }
    
    latest_groceries = []
    for code, (name, unit) in ITEM_MAP.items():
        try:
            item_data = df_grocery.filter(pl.col("item_code") == int(code)).head(2).to_dicts()
            if len(item_data) >= 1:
                curr = item_data[0]
                prev = item_data[1] if len(item_data) > 1 else curr
                latest_groceries.append({
                    "name": name,
                    "unit": unit,
                    "price": curr["price"],
                    "chg": curr["price"] - prev["price"],
                    "date": curr["date"].strftime('%d %b')
                })
        except:
            continue

    # 4. Weather Stats
    weather_list = []
    if pl.read_parquet("data/weather.parquet").height > 0:
        df_weather = pl.read_parquet("data/weather.parquet")
        
        # WMO Weather code mapping
        WMO_MAP = {
            0: ("Clear sky", "☀️"),
            1: ("Mainly clear", "🌤️"),
            2: ("Partly cloudy", "⛅"),
            3: ("Overcast", "☁️"),
            45: ("Fog", "🌫️"),
            48: ("Depositing rime fog", "🌫️"),
            51: ("Light drizzle", "🌦️"),
            53: ("Moderate drizzle", "🌦️"),
            55: ("Dense drizzle", "🌦️"),
            61: ("Slight rain", "🌧️"),
            63: ("Moderate rain", "🌧️"),
            65: ("Heavy rain", "🌧️"),
            71: ("Slight snow fall", "❄️"),
            73: ("Moderate snow fall", "❄️"),
            75: ("Heavy snow fall", "❄️"),
            77: ("Snow grains", "❄️"),
            80: ("Slight rain showers", "🌦️"),
            81: ("Moderate rain showers", "🌦️"),
            82: ("Violent rain showers", "🌧️"),
            95: ("Thunderstorm", "⛈️"),
            96: ("Thunderstorm with slight hail", "⛈️"),
            99: ("Thunderstorm with heavy hail", "⛈️"),
        }

        cities = df_weather.select("city").unique().to_series().to_list()
        for city in cities:
            city_data = df_weather.filter(pl.col("city") == city).sort("date").head(3).to_dicts()
            forecasts = []
            for f in city_data:
                desc, emoji = WMO_MAP.get(f["weather_code"], ("Unknown", "❓"))
                # Convert 'YYYY-MM-DD' to 'DD MMM'
                dt = datetime.strptime(f["date"], "%Y-%m-%d")
                forecasts.append({
                    "day": dt.strftime("%a"), # e.g. Mon, Tue
                    "date": dt.strftime("%d %b"),
                    "emoji": emoji,
                    "desc": desc,
                    "max": f["temp_max"],
                    "min": f["temp_min"]
                })
            weather_list.append({
                "city": city,
                "forecasts": forecasts
            })

    stats = {
        "update_time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "fuel": fuel_list[:7],
        "exchange": ex_list[:7],
        "grocery": latest_groceries,
        "weather": weather_list
    }
    return stats

if __name__ == "__main__":
    stats = get_latest_stats()
    with open("docs/latest_stats.json", "w") as f:
        json.dump(stats, f)
    print("✅ Precision stats saved to docs/latest_stats.json")
