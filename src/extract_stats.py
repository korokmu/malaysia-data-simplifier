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
        ex_list[i]['date'] = ex_list[i]['date'].strftime('%d %b %Y')

    # 3. Grocery Stats (Price Catcher)
    df_grocery = pl.read_parquet("data/pricecatcher.parquet")
    # Average per item per day
    df_grocery = (
        df_grocery.group_by(["date", "item_code"])
        .agg(pl.col("price").mean())
        .sort("date", descending=True)
    )
    
    # Map item codes to names and units for the dashboard (codes verified against live data)
    ITEM_MAP = {
        "1":    ("Chicken",      "per kg"),
        "1109": ("Eggs Grd A",   "per 30 pcs"),
        "1110": ("Eggs Grd B",   "per 30 pcs"),
        "1111": ("Eggs Grd C",   "per 30 pcs"),
        "129":  ("Onions",       "per kg"),
        "114":  ("Tomato",       "per kg"),
        "94":   ("Red Chili",    "per kg"),
    }
    
    # We want the latest prices for each item
    latest_groceries = []
    for code, (name, unit) in ITEM_MAP.items():
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

    stats = {
        "update_time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "fuel": fuel_list[:7],
        "exchange": ex_list[:7],
        "grocery": latest_groceries
    }
    return stats

if __name__ == "__main__":
    stats = get_latest_stats()
    # Save to 'docs' folder so the web server can see it
    with open("docs/latest_stats.json", "w") as f:
        json.dump(stats, f)
    print("✅ Precision stats saved to docs/latest_stats.json")
