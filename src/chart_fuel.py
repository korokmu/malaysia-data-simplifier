import polars as pl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta

FUEL_FILE = "data/fuel_prices.parquet"
OUTPUT_HTML = "docs/fuel_chart.html"

def generate_fuel_chart():
    print("🎨 Generating Locked Fuel Trend Chart (No Zoom)...")
    
    df = pl.read_parquet(FUEL_FILE).filter(pl.col("series_type") == "level")
    sixty_days_ago = datetime.now() - timedelta(days=60)
    df_recent = df.filter(pl.col("date") > sixty_days_ago.date())

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Semenanjung", "Sabah & Sarawak"),
        vertical_spacing=0.1
    )

    fig.add_trace(go.Scatter(x=df_recent["date"], y=df_recent["ron95"], name="RON95", line=dict(color='#f1c40f', width=4)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_recent["date"], y=df_recent["ron97"], name="RON97", line=dict(color='#2ecc71', width=4)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_recent["date"], y=df_recent["diesel"], name="Diesel", line=dict(color='#2c3e50', width=4)), row=1, col=1)

    fig.add_trace(go.Scatter(x=df_recent["date"], y=df_recent["ron95"], name="RON95", line=dict(color='#f1c40f', width=4), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_recent["date"], y=df_recent["ron97"], name="RON97", line=dict(color='#2ecc71', width=4), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_recent["date"], y=df_recent["diesel_eastmsia"], name="Diesel", line=dict(color='#2c3e50', width=4), showlegend=False), row=2, col=1)

    fig.update_layout(
        height=600,
        template="plotly_white",
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    
    # LOCK THE ZOOM
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    
    config = {'displayModeBar': False}
    
    os.makedirs("docs", exist_ok=True)
    fig.write_html(OUTPUT_HTML, include_plotlyjs="cdn", full_html=False, config=config)
    
    print(f"✅ Success! Locked fuel trend chart saved to {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_fuel_chart()
