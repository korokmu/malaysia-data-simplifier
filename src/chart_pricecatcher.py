import polars as pl
import plotly.express as px
import os
from datetime import datetime

# 1. Folders & Files
PRICE_FILE = "data/pricecatcher.parquet"
ITEM_LOOKUP_FILE = "data/lookup_item.parquet"
OUTPUT_HTML = "docs/pricecatcher_chart.html"

# Item Map for display (codes verified against live pricecatcher data)
ITEM_MAP = {
    1:    "Standard Chicken (1kg)",
    1109: "Grade A Eggs (30pcs)",
    129:  "Large Onions (1kg)",
    114:  "Tomato (1kg)",
    94:   "Red Chili (1kg)"
}

def generate_pricecatcher_chart():
    print("🎨 Generating Daily Grocery Trend Chart...")
    
    # Load and Join
    df = pl.read_parquet(PRICE_FILE)
    
    # Average the price per day per item (National Average)
    df_avg = (
        df.group_by(["date", "item_code"])
        .agg(pl.col("price").mean())
        .sort("date")
    )
    
    # Map Item Names using map_elements (safe for int→str mapping)
    df_avg = df_avg.with_columns(
        pl.col("item_code").map_elements(
            lambda x: ITEM_MAP.get(x, str(x)), return_dtype=pl.String
        ).alias("item_name")
    )

    # Create the chart
    fig = px.line(
        df_avg, 
        x="date", 
        y="price",
        color="item_name",
        labels={"price": "Average Price (RM)", "date": "Date", "item_name": "Essential Item"},
        title="Essential Grocery Price Trends (April 2026)",
        template="plotly_white"
    )
    
    fig.update_layout(
        height=500,
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    
    # LOCK THE ZOOM
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    
    config = {'displayModeBar': False}
    
    os.makedirs("docs", exist_ok=True)
    fig.write_html(OUTPUT_HTML, include_plotlyjs="cdn", full_html=False, config=config)
    
    print(f"✅ Success! Grocery trend charts saved to {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_pricecatcher_chart()
