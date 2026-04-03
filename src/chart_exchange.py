import polars as pl
import plotly.express as px
import os
from datetime import datetime, timedelta

EXCHANGE_FILE = "data/exchange_rates.parquet"
OUTPUT_HTML = "docs/exchange_chart.html"

def generate_exchange_chart():
    print("🎨 Generating Daily Exchange Rate Chart...")
    
    df = pl.read_parquet(EXCHANGE_FILE).sort("date")
    
    # Filter for the last 365 days
    three_hundred_sixty_five_days_ago = datetime.now() - timedelta(days=365)
    df_recent = df.filter(pl.col("date") > three_hundred_sixty_five_days_ago.date())

    fig = px.line(
        df_recent, 
        x="date", 
        y=["usd", "sgd", "eur"],
        labels={"value": "RM", "date": "Date"},
        template="plotly_white"
    )
    
    fig.update_layout(
        height=380, # Reduced height to fit in the dashboard without scrollbar
        margin=dict(l=40, r=40, t=20, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    
    # LOCK THE ZOOM
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    
    config = {'displayModeBar': False}
    
    os.makedirs("docs", exist_ok=True)
    fig.write_html(OUTPUT_HTML, include_plotlyjs="cdn", full_html=False, config=config)
    
    print(f"✅ Success! Locked exchange charts saved to {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_exchange_chart()
