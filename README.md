# 🇲🇾 Malaysia Data Simplifier

A fully automated daily dashboard that pulls Malaysian public data and presents it in a clean, mobile-friendly website — updated every night at 2 AM automatically.

**Live site:** https://korokmu.github.io/malaysia-data-simplifier/

---

## 📊 What It Shows

| Section | Data | Source |
|---|---|---|
| ⛽ Fuel Prices | RON95, RON97, Diesel weekly prices + trend | data.gov.my |
| 💹 Exchange Rates | USD, SGD, EUR, GBP, JPY, AUD, CNY vs MYR + trend | Bank Negara Malaysia via data.gov.my |
| 🧮 Traveler Calculator | Convert any currency to RM instantly | BNM live rate |
| 🛒 Grocery Prices | Chicken, eggs, onions, tomatoes, chili per state | PriceCatcher via data.gov.my |
| 🌦️ Weather | 3-day forecast for all 16 states/territories | Open-Meteo |

---

## ✨ Features

- **State selector** — switch between all 16 Malaysian states/federal territories, grouped by region
- **Persona toggle** — Local view (cost of living focus) vs Visitor view (travel essentials)
- **Trend badges** — "Good Deal" / "Price Hike" on grocery items vs 30-day average
- **Price change indicators** — ▲/▼ arrows on fuel and exchange rates vs previous week/day
- **Fully automated** — runs daily via systemd timer, commits and pushes to GitHub Pages

---

## 🛠️ Tech Stack

- **Python 3** + [Polars](https://pola.rs/) — fast data processing
- **Plotly** — interactive HTML charts
- **Parquet** — efficient data storage
- **GitHub Pages** — free hosting
- **systemd timer** — daily automation on Linux

---

## 📁 Project Structure

```
malaysia-data-simplifier/
├── src/
│   ├── fetch_fuel.py           ← Downloads weekly fuel price data
│   ├── fetch_exchange.py       ← Downloads daily exchange rates
│   ├── fetch_pricecatcher.py   ← Downloads monthly grocery prices
│   ├── fetch_weather.py        ← Downloads 3-day weather forecasts
│   ├── chart_fuel.py           ← Generates fuel trend chart
│   ├── chart_exchange.py       ← Generates exchange rate chart
│   ├── chart_pricecatcher.py   ← Generates grocery price chart
│   ├── extract_stats.py        ← Builds latest_stats.json for dashboard
│   ├── notify_discord.py       ← Optional Discord update notification
│   └── validate.py             ← Health checks after each run
├── docs/                       ← GitHub Pages website (auto-generated)
│   ├── index.html
│   ├── latest_stats.json
│   └── *.html (charts)
├── update.sh                   ← Master script — fetch → chart → push
└── requirements.txt
```

---

## 🚀 Running Locally

```bash
git clone https://github.com/korokmu/malaysia-data-simplifier.git
cd malaysia-data-simplifier
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash update.sh
```

---

## 📦 Data Sources

All data is free and publicly available — no API keys required.

- **[data.gov.my](https://data.gov.my)** — Malaysian government open data portal
- **[Open-Meteo](https://open-meteo.com)** — Free open-source weather API
