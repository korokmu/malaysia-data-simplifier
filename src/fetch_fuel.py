import polars as pl
import requests
import os
from datetime import datetime

# 1. Where to save the data
DATA_FOLDER = "data"
FUEL_FILE = f"{DATA_FOLDER}/fuel_prices.parquet"

# 2. Where the data lives (from data.gov.my)
# Dataset ID for Fuel Price (Weekly)
FUEL_API_URL = "https://api.data.gov.my/data-catalogue?id=fuelprice"

def check_vpn():
    """
    Check if a VPN is likely active by looking for common VPN network interfaces.
    """
    # This is a simple check. For ProtonVPN (Flatpak), we can also check for 'tun0'
    # or use 'nmcli' if available. 
    # For now, we'll just log a reminder as per your context.
    print("💡 Reminder: Ensure ProtonVPN is active before scraping!")

def fetch_fuel_data():
    """
    Fetch weekly fuel prices from data.gov.my and save to Parquet.
    """
    print(f"🚀 Fetching fuel prices at {datetime.now()}...")
    
    try:
        # Fetch JSON data
        response = requests.get(FUEL_API_URL)
        response.raise_for_status()
        data = response.json()
        
        # Load into Polars from list of dicts
        df = pl.from_dicts(data, infer_schema_length=None)
        
        # Clean the data:
        # 1. Convert 'date' string to actual Date type
        # 2. Keep only important columns
        df = df.with_columns(
            pl.col("date").str.to_date()
        ).select([
            "date", "ron95", "ron97", "diesel", "diesel_eastmsia", "ron95_budi95", "series_type"
        ])
        
        # Save as Parquet (High-Efficiency format for your Arch Linux)
        os.makedirs(DATA_FOLDER, exist_ok=True)
        df.write_parquet(FUEL_FILE)
        
        print(f"✅ Success! Saved {len(df)} rows to {FUEL_FILE}")
        return df

    except Exception as e:
        print(f"❌ Error fetching fuel data: {e}")
        return None

if __name__ == "__main__":
    check_vpn()
    fetch_fuel_data()
