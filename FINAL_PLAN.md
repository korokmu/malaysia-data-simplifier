# FINAL_PLAN.md: Malaysian Data Simplifier

## 1. Project Goal
An automated, resource-aware pipeline for Arch Linux to transform data.gov.my into simplified insights for Locals and Visitors.

## 2. Audience Targets
- **Locals:** Focus on cost-of-living (Fuel, Price Catcher).
- **Visitors:** Focus on travel essentials (Exchange Rates, Weather).

## 3. Technical Stack
- **Engine:** Python 3.14 + `polars`.
- **Format:** Parquet (fast, low-memory).
- **Visuals:** Plotly HTML (CDN mode, ~10KB per chart).
- **Environment:** Isolated `.venv` on Linux.

## 4. Pipeline Structure
- `src/fetch_*.py`: Individual data collectors.
- `src/chart_*.py`: Regional-aware charts (Peninsular vs. East Malaysia).
- `docs/index.html`: Mobile-friendly dashboard.

## 5. Automation
- `systemd` timer for 2:00 AM daily updates.
- Automatic git deployment to GitHub Pages.
