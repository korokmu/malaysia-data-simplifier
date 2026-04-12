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
        # Calculate changes for all
        for key in ['usd', 'sgd', 'eur', 'gbp', 'aud', 'cny']:
            ex_list[i][f'{key}_chg'] = ex_list[i][key] - ex_list[i+1][key]
        
        # FIX: JPY (100 units) and IDR (10,000 units) scaling
        # Calculate change first, then scale both for display
        jpy_raw = ex_list[i]['jpy']
        prev_jpy = ex_list[i+1]['jpy']
        ex_list[i]['jpy_chg'] = (jpy_raw - prev_jpy) * 100
        ex_list[i]['jpy'] = jpy_raw * 100

        idr_raw = ex_list[i]['idr']
        prev_idr = ex_list[i+1]['idr']
        ex_list[i]['idr_chg'] = (idr_raw - prev_idr) * 10000
        ex_list[i]['idr'] = idr_raw * 10000
        
        ex_list[i]['date'] = ex_list[i]['date'].strftime('%d %b %Y')

    # 3. Grocery Stats (Price Catcher - Now State-Aware + Trend)
    df_grocery = pl.read_parquet("data/pricecatcher.parquet")
    
    # Calculate 30-day averages per state/item
    df_30d_avg = (
        df_grocery.group_by(["state", "item_code"])
        .agg(pl.col("price").mean().alias("avg_30d"))
    )

    # Get latest price per state/item (most robust)
    df_latest_state_prices = (
        df_grocery.sort("date", descending=True)
        .group_by(["state", "item_code"])
        .first() # Takes the newest row for every combo
    )
    
    # Join with 30d avg
    df_trends = df_latest_state_prices.join(df_30d_avg, on=["state", "item_code"])

    ITEM_MAP = {
        "1":    ("Chicken",      "per kg"),
        "1109": ("Eggs Grd A",   "per 30 pcs"),
        "1110": ("Eggs Grd B",   "per 30 pcs"),
        "1111": ("Eggs Grd C",   "per 30 pcs"),
        "129":  ("Onions",       "per kg"),
        "114":  ("Tomato",       "per kg"),
        "94":   ("Red Chili",    "per kg"),
    }
    
    grocery_data = []
    for row in df_trends.to_dicts():
        code_str = str(row["item_code"])
        if code_str in ITEM_MAP:
            name, unit = ITEM_MAP[code_str]
            
            # Logic for trend badge
            trend = "flat"
            if row["price"] < row["avg_30d"] * 0.98: # 2% cheaper than avg
                trend = "good"
            elif row["price"] > row["avg_30d"] * 1.02: # 2% more expensive
                trend = "high"

            grocery_data.append({
                "state": row["state"],
                "name": name,
                "unit": unit,
                "price": row["price"],
                "trend": trend,
                "date": row["date"].strftime('%d %b') # Individual date per item/state
            })

    # List of all states for the dropdown
    STATES = [
        "Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang", 
        "Pulau Pinang", "Perak", "Perlis", "Selangor", "Terengganu", "Sabah", "Sarawak",
        "W.P. Kuala Lumpur", "W.P. Labuan", "W.P. Putrajaya"
    ]

    # Map state names to capital cities for weather linking
    STATE_CAPITAL_MAP = {
        "Johor": "Johor Bahru", "Kedah": "Alor Setar", "Kelantan": "Kota Bharu",
        "Melaka": "Melaka", "Negeri Sembilan": "Seremban", "Pahang": "Kuantan",
        "Pulau Pinang": "George Town", "Perak": "Ipoh", "Perlis": "Kangar",
        "Selangor": "Shah Alam", "Terengganu": "Kuala Terengganu", "Sabah": "Kota Kinabalu",
        "Sarawak": "Kuching", "W.P. Kuala Lumpur": "Kuala Lumpur", 
        "W.P. Labuan": "Labuan", "W.P. Putrajaya": "Putrajaya"
    }

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
        "states": STATES,
        "state_capital_map": STATE_CAPITAL_MAP,
        "fuel": fuel_list[:7],
        "exchange": ex_list[:7],
        "grocery": grocery_data,
        "weather": weather_list
    }
    return stats

if __name__ == "__main__":
    stats = get_latest_stats()
    with open("docs/latest_stats.json", "w") as f:
        json.dump(stats, f)
    print("✅ Precision stats saved to docs/latest_stats.json")
