# FINAL_PLAN.md: Malaysian Data Simplifier

## 1. Project Goal
An automated, resource-aware pipeline for Arch Linux to transform data.gov.my into simplified insights for Locals and Visitors.

## 2. Audience Targets
- **Locals:** Cost-of-living focus — Fuel prices, grocery prices by state, trend badges.
- **Visitors:** Travel essentials — Exchange rates (8 currencies), RM calculator, weather forecasts.

## 3. Technical Stack
- **Engine:** Python 3.14 + `polars`.
- **Format:** Parquet (fast, low-memory).
- **Visuals:** Plotly HTML (CDN mode, ~10KB per chart).
- **Environment:** Isolated `.venv` on Linux.

## 4. Pipeline Structure
- `src/fetch_*.py`: Individual data collectors (fuel, exchange, pricecatcher, weather).
- `src/chart_*.py`: Charts for fuel and grocery (exchange chart removed in v1.2).
- `src/extract_stats.py`: Builds `latest_stats.json` for the dashboard.
- `src/notify_discord.py`: Optional Discord notification (needs `.env` setup).
- `src/validate.py`: Health checks after each run.
- `docs/index.html`: Mobile-friendly dashboard with persona toggle, state selector, traveler calculator.

## 5. Automation
- `systemd` timer for 2:00 AM daily updates.
- Automatic git deployment to GitHub Pages.
- Weather fetch has retry logic + cached fallback for reliability.

## 6. Discoverability
- SEO meta tags, Open Graph, Twitter card in `docs/index.html`.
- Google Search Console verified and URL submitted for indexing.
- GitHub repo description, homepage URL, and topics all set.

## 7. Future Ideas (v1.3+)
- Discord webhook notification (infrastructure ready, needs `.env` setup).
- Price alert when RON95 changes week-on-week.
- Historical grocery chart by state.
- Sitemap.xml for better SEO.

