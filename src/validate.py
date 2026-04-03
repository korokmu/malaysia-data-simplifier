import os
import json
import polars as pl
from datetime import datetime

def check_health():
    print(f"🔍 Starting System Health Check at {datetime.now()}...")
    errors = []
    warnings = []

    # 1. Check Directories
    for folder in ["data", "docs", "src"]:
        if not os.path.exists(folder):
            errors.append(f"❌ Missing folder: {folder}")

    # 2. Check Data Files (Parquet)
    data_files = {
        "data/fuel_prices.parquet": "Fuel Prices",
        "data/exchange_rates.parquet": "Exchange Rates",
        "data/pricecatcher.parquet": "Grocery Prices"
    }

    for path, name in data_files.items():
        if not os.path.exists(path):
            errors.append(f"❌ Missing data file: {path}")
        else:
            try:
                df = pl.read_parquet(path)
                if len(df) == 0:
                    errors.append(f"❌ Data file is empty: {path}")
                else:
                    print(f"✅ {name}: {len(df)} rows found.")
            except Exception as e:
                errors.append(f"❌ Error reading {path}: {e}")

    # 3. Check JSON Stats
    stats_path = "docs/latest_stats.json"
    if not os.path.exists(stats_path):
        errors.append(f"❌ Missing stats file: {stats_path}")
    else:
        try:
            with open(stats_path, "r") as f:
                stats = json.load(f)
            
            # Check for keys
            for key in ["fuel", "exchange", "grocery", "update_time"]:
                if key not in stats:
                    errors.append(f"❌ Missing key in JSON: {key}")
            
            if not stats["grocery"]:
                warnings.append("⚠️ Grocery stats are empty in JSON.")
            
            print(f"✅ JSON Stats: Valid (Updated {stats['update_time']})")
        except Exception as e:
            errors.append(f"❌ Error parsing JSON: {e}")

    # 4. Check HTML Charts
    html_files = ["docs/index.html", "docs/fuel_chart.html", "docs/exchange_chart.html", "docs/pricecatcher_chart.html"]
    for html in html_files:
        if not os.path.exists(html):
            errors.append(f"❌ Missing HTML: {html}")
        else:
            size = os.path.getsize(html)
            if size < 1000:
                errors.append(f"❌ HTML file too small (likely broken): {html}")
    
    print("✅ HTML Dashboard & Charts: Present")

    # Final Report
    print("\n--- HEALTH REPORT ---")
    if not errors and not warnings:
        print("🟢 ALL SYSTEMS GO! Everything is okay.")
    else:
        for err in errors:
            print(err)
        for warn in warnings:
            print(warn)
    print("----------------------\n")
    return len(errors) == 0

if __name__ == "__main__":
    success = check_health()
    exit(0 if success else 1)
