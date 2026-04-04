import polars as pl
import os
from datetime import datetime

# 1. Folders & Files
DATA_FOLDER = "data"
PRICE_FILE = f"{DATA_FOLDER}/pricecatcher.parquet"
ITEM_LOOKUP_FILE = f"{DATA_FOLDER}/lookup_item.parquet"

# Base URL for storage
BASE_URL = "https://storage.data.gov.my/pricecatcher/"

# Items we want to track
ESSENTIAL_ITEMS = [1, 1109, 1110, 1111, 129, 114, 94]

def fetch_pricecatcher_data():
    now = datetime.now()
    print(f"🚀 Fetching Price Catcher essentials (Monthly-Aware) at {now}...")
    os.makedirs(DATA_FOLDER, exist_ok=True)

    # 1. Update Lookups
    print("📋 Updating Lookups...")
    try:
        pl.read_parquet(f"{BASE_URL}lookup_item.parquet").write_parquet(ITEM_LOOKUP_FILE)
        df_premise = (
            pl.read_parquet(f"{BASE_URL}lookup_premise.parquet")
            .select(["premise_code", "state"])
            .with_columns(pl.col("premise_code").cast(pl.Int64))
        )
    except Exception as e:
        print(f"⚠️ Could not update lookups: {e}")
        return None

    # 2. Detect the current month file
    current_month_url = f"{BASE_URL}pricecatcher_{now.strftime('%Y-%m')}.parquet"
    
    # 3. Stream and Join
    print(f"🛒 Scanning {now.strftime('%B %Y')} data for essentials...")
    try:
        # Load and Join
        df_prices = (
            pl.read_parquet(current_month_url)
            .filter(pl.col("item_code").is_in(ESSENTIAL_ITEMS))
            .select(["date", "item_code", "price", "premise_code"])
            .with_columns(pl.col("premise_code").cast(pl.Int64))
        )
        
        # Join with state info
        df_final = df_prices.join(df_premise, on="premise_code").select(["date", "item_code", "price", "state"])
        
        # Save the result
        df_final.write_parquet(PRICE_FILE)
        print(f"✅ Success! Saved {len(df_final)} rows of daily essentials with state info.")
        return df_final

    except Exception as e:
        print(f"❌ Error fetching current month file: {e}")
        return None

if __name__ == "__main__":
    fetch_pricecatcher_data()
