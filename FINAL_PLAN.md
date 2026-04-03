# FINAL_PLAN.md: Malaysian Data Simplifier

## 1. Project Goal
An automated, resource-aware pipeline for Arch Linux to transform data.gov.my into simplified insights for Locals and Visitors.

## 2. Audience Targets
- **Locals:** Focus on cost-of-living (Fuel, Price Catcher).
- **Visitors:** Focus on travel essentials (Exchange Rates, Weather).

## 3. Technical Stack (Celeron Optimized)
- **Engine:** Python 3.14 + `polars[rtcompat]` (No-AVX support).
- **Format:** Parquet (Fast, low-memory).
- **Visuals:** Plotly HTML (CDN mode, ~10KB per chart).
- **Environment:** Isolated `.venv` on Arch Linux.

## 4. Pipeline Structure
- `src/fetch_*.py`: Individual data collectors (VPN-protected).
- `src/chart_*.py`: Regional-aware charts (Peninsular vs. East Malaysia).
- `docs/index.html`: A mobile-friendly dashboard (POCO F3 optimized).

## 5. Automation
- `systemd` timer for 2:00 AM daily updates.
- Automatic git deployment to GitHub Pages.
