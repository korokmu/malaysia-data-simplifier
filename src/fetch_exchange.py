import polars as pl
import requests
import os
from datetime import datetime

# 1. Where to save the data
DATA_FOLDER = "data"
EXCHANGE_FILE = f"{DATA_FOLDER}/exchange_rates.parquet"

# 2. Where the data lives (from data.gov.my)
# Dataset ID for Daily Exchange Rates (17:00 Ref Rate)
EXCHANGE_API_URL = "https://api.data.gov.my/data-catalogue?id=exchangerates_daily_1700"

def fetch_exchange_data():
    """
    Fetch daily exchange rates from data.gov.my and save to Parquet.
    """
    print(f"🚀 Fetching daily exchange rates at {datetime.now()}...")

    try:
        # Fetch JSON data
        response = requests.get(EXCHANGE_API_URL)
        response.raise_for_status()
        data = response.json()

        # Load into Polars
        df = pl.from_dicts(data, infer_schema_length=None)

        # Clean the data:
        # 1. Convert 'date' string to actual Date type
        # 2. Keep only important columns
        df = df.filter(pl.col("rate_type") == "middle").with_columns(
            pl.col("date").str.to_date()
        ).select([
            "date", "usd", "sgd", "eur", "gbp", "jpy", "aud", "cny"
        ])

        
        # Save as Parquet
        os.makedirs(DATA_FOLDER, exist_ok=True)
        df.write_parquet(EXCHANGE_FILE)
        
        print(f"✅ Success! Saved {len(df)} rows to {EXCHANGE_FILE}")
        return df

    except Exception as e:
        print(f"❌ Error fetching exchange data: {e}")
        return None

if __name__ == "__main__":
    fetch_exchange_data()
