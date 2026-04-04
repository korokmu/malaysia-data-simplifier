# 📖 Owner's Guide — Malaysia Data Simplifier

Everything you need to run, maintain, and expand this project on your own.

---

## 🗺️ What This Project Does

Pulls Malaysian public data every night at 2 AM, processes it, and publishes a
dashboard to the internet automatically.

**Live site:** https://korokmu.github.io/malaysia-data-simplifier/

---

## 📁 Folder Structure

```
malaysia-data-simplifier/
│
├── src/                        ← Python scripts (the brain)
│   ├── fetch_fuel.py           ← Downloads fuel price data
│   ├── fetch_exchange.py       ← Downloads exchange rate data
│   ├── fetch_pricecatcher.py   ← Downloads grocery price data
│   ├── chart_fuel.py           ← Generates fuel chart (HTML)
│   ├── chart_exchange.py       ← Generates exchange chart (HTML)
│   ├── chart_pricecatcher.py   ← Generates grocery chart (HTML)
│   ├── extract_stats.py        ← Builds latest_stats.json for dashboard
│   └── validate.py             ← Checks everything is healthy
│
├── data/                       ← Raw data files (NOT uploaded to GitHub)
│   ├── fuel_prices.parquet
│   ├── exchange_rates.parquet
│   ├── pricecatcher.parquet
│   └── lookup_item.parquet
│
├── docs/                       ← The website (uploaded to GitHub Pages)
│   ├── index.html              ← Main dashboard page
│   ├── latest_stats.json       ← Data the dashboard reads (auto-generated)
│   ├── fuel_chart.html         ← Fuel price chart (embedded)
│   ├── exchange_chart.html     ← Exchange rate chart (embedded)
│   └── pricecatcher_chart.html ← Grocery trend chart (embedded)
│
├── update.sh                   ← Master script that runs everything
├── requirements.txt            ← Python packages needed
├── .venv/                      ← Python virtual environment (local only)
└── update.log                  ← Log of every nightly run
```

> `data/` stays on your machine only. `docs/` goes to GitHub.

---

## ⚙️ How the Pipeline Works

Every night `update.sh` runs in order:

```
1. fetch_fuel.py         → data/fuel_prices.parquet
2. fetch_exchange.py     → data/exchange_rates.parquet
3. fetch_pricecatcher.py → data/pricecatcher.parquet
4. chart_fuel.py         → docs/fuel_chart.html
5. chart_exchange.py     → docs/exchange_chart.html
6. chart_pricecatcher.py → docs/pricecatcher_chart.html
7. extract_stats.py      → docs/latest_stats.json
8. validate.py           → checks everything is OK
9. git push              → website goes live
```

---

## 🕑 Automation (Systemd Timer)

```bash
# Check if timer is running (and when next run is)
systemctl --user list-timers

# Check last run log
tail -50 update.log

# Manually trigger full update
bash update.sh

# Stop/start the nightly timer
systemctl --user stop malaysia-update.timer
systemctl --user start malaysia-update.timer
```

---

## 🐍 Python Environment

```bash
# Activate (needed before running any script manually)
source .venv/bin/activate

# Run a single script
python src/fetch_fuel.py
python src/validate.py

# Exit when done
deactivate

# Rebuild from scratch if needed
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📊 Data Sources

| Data | Source | Updates |
|------|--------|---------|
| Fuel prices | `api.data.gov.my` — `fuelprice` | Weekly (Wednesday) |
| Exchange rates | `api.data.gov.my` — `exchangerates_daily_1700` | Daily |
| Grocery prices | `storage.data.gov.my/pricecatcher/` | Daily |

All free, no API key needed.

---

## ➕ How to Add a New Grocery Item

**Step 1 — Find the item code**
```bash
source .venv/bin/activate
python3 -c "
import polars as pl
lookup = pl.read_parquet('data/lookup_item.parquet')
print(lookup.filter(pl.col('item').str.contains_any(['potato'], ascii_case_insensitive=True)))
"
```

**Step 2 — Add to fetcher** (`src/fetch_pricecatcher.py` line 14):
```python
ESSENTIAL_ITEMS = [..., YOUR_NEW_CODE]
```

**Step 3 — Add to chart** (`src/chart_pricecatcher.py`, `ITEM_MAP`):
```python
YOUR_NEW_CODE: "Potato (1kg)",
```

**Step 4 — Add to dashboard cards** (`src/extract_stats.py`, `ITEM_MAP`):
```python
"YOUR_NEW_CODE": ("Potato", "per kg"),
```

**Step 5 — Run update**
```bash
bash update.sh
```

---

## ➕ How to Add a New Exchange Currency

1. Open `src/fetch_exchange.py` → add e.g. `"jpy"` to the `.select([...])` list
2. Add `<th>JPY</th>` column in `docs/index.html` exchange table
3. Add the `<td>` data cell in the JS row-builder (search `ex-body`)
4. Add `jpy_chg` calculation in `src/extract_stats.py`

---

## 🔧 Changing the Dashboard

File: `docs/index.html`

- **Colours** → `:root { }` CSS block at the top
- **Section titles** → `<h2>` tags
- **Notes/disclaimers** → `<p class="note">` tags

After any change, push to go live:
```bash
git add docs/index.html
git commit -m "describe change"
git push
```

---

## 🚀 Deploy to Live Website

```bash
git add docs/
git commit -m "describe change"
git push
# Wait 1–2 min, then hard-refresh: Ctrl+Shift+R
```

---

## 🩺 Troubleshooting

```bash
# Health check
python src/validate.py

# See what went wrong in last run
tail -50 update.log

# Website shows old data — push manually
bash update.sh

# Undo last commit safely
git revert HEAD && git push
```

---

## 📋 Quick Reference

| Task | Command |
|------|---------|
| Full update now | `bash update.sh` |
| Check timer | `systemctl --user list-timers` |
| Last run log | `tail -50 update.log` |
| Activate Python | `source .venv/bin/activate` |
| Health check | `python src/validate.py` |
| Push website | `git add docs/ && git commit -m "msg" && git push` |
| Recent history | `git --no-pager log --oneline -10` |
| Undo last commit | `git revert HEAD && git push` |
