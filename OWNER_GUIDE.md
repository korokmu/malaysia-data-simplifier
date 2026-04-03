# 📖 Owner's Guide — Malaysia Data Simplifier

Everything you need to run, maintain, and expand this project on your own.
No prior experience assumed.

---

## 🗺️ What This Project Does

Pulls Malaysian public data every night at 2 AM, processes it, and publishes a
dashboard to the internet automatically. You never have to touch it unless you
want to add something new.

**Live site:** https://korokmu.github.io/malaysia-data-simplifier/

---

## 📁 Folder Structure (What Everything Is)

```
malaysia-data-simplifier/
│
├── src/                        ← Python scripts (the brain)
│   ├── fetch_fuel.py           ← Downloads fuel price data
│   ├── fetch_exchange.py       ← Downloads exchange rate data
│   ├── fetch_pricecatcher.py   ← Downloads grocery price data
│   ├── chart_fuel.py           ← Generates the fuel chart (HTML)
│   ├── chart_exchange.py       ← Generates the exchange chart (HTML)
│   ├── chart_pricecatcher.py   ← Generates the grocery chart (HTML)
│   ├── extract_stats.py        ← Builds latest_stats.json for the dashboard
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
│   ├── fuel_chart.html         ← Fuel price chart (embedded in index.html)
│   ├── exchange_chart.html     ← Exchange rate chart (embedded)
│   └── pricecatcher_chart.html ← Grocery trend chart (embedded)
│
├── update.sh                   ← The master script that runs everything
├── requirements.txt            ← Python packages needed
├── .venv/                      ← Python virtual environment (local only)
└── update.log                  ← Log of every nightly run
```

> **Key rule:** `data/` stays on your machine only. `docs/` goes to GitHub.

---

## ⚙️ How the Pipeline Works (Step by Step)

Every night `update.sh` runs these steps in order:

```
1. fetch_fuel.py        →  downloads fuel data  →  saves data/fuel_prices.parquet
2. fetch_exchange.py    →  downloads rates       →  saves data/exchange_rates.parquet
3. fetch_pricecatcher.py→  downloads groceries   →  saves data/pricecatcher.parquet
4. chart_fuel.py        →  reads fuel parquet    →  writes docs/fuel_chart.html
5. chart_exchange.py    →  reads exchange parquet →  writes docs/exchange_chart.html
6. chart_pricecatcher.py→  reads grocery parquet →  writes docs/pricecatcher_chart.html
7. extract_stats.py     →  reads all 3 parquets  →  writes docs/latest_stats.json
8. validate.py          →  checks everything is OK
9. git push             →  sends docs/ to GitHub → website updates
```

---

## 🕑 Automation (Systemd Timer)

The project runs automatically via a systemd user timer.

### Check if the timer is running
```bash
systemctl --user list-timers
# Look for: malaysia-update.timer    (next run shown)
```

### Check the last run log
```bash
tail -50 /home/eri/workspace/malaysia-data-simplifier/update.log
```

### Manually trigger a full update (same as the nightly job)
```bash
cd /home/eri/workspace/malaysia-data-simplifier
bash update.sh
```

### Stop the nightly timer temporarily
```bash
systemctl --user stop malaysia-update.timer
```

### Start it back
```bash
systemctl --user start malaysia-update.timer
```

---

## 🐍 Python Environment

The project uses a private Python environment in `.venv/` so it doesn't touch
your system Python.

### Activate it (needed before running any script manually)
```bash
cd /home/eri/workspace/malaysia-data-simplifier
source .venv/bin/activate
```

### Run a single script manually (after activating)
```bash
python src/fetch_fuel.py        # re-download fuel data only
python src/extract_stats.py     # regenerate the dashboard JSON only
python src/validate.py          # health check
```

### Exit the environment when done
```bash
deactivate
```

### If you ever need to rebuild the environment from scratch
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📊 Data Sources

| Data | Where it comes from | How often it updates |
|------|---------------------|----------------------|
| Fuel prices | `api.data.gov.my` — dataset `fuelprice` | Weekly (every Wednesday) |
| Exchange rates | `api.data.gov.my` — dataset `exchangerates_daily_1700` | Daily (business days) |
| Grocery prices | `storage.data.gov.my/pricecatcher/` — monthly Parquet files | Daily |

All sources are free, no API key needed.

---

## ➕ How to Add a New Grocery Item

**Step 1 — Find the item code**
```bash
cd /home/eri/workspace/malaysia-data-simplifier
source .venv/bin/activate
python3 -c "
import polars as pl
lookup = pl.read_parquet('data/lookup_item.parquet')
# Search by keyword:
print(lookup.filter(pl.col('item').str.contains_any(['potato', 'kentang'], ascii_case_insensitive=True)))
"
```

**Step 2 — Add the code to the fetcher** (`src/fetch_pricecatcher.py`, line 14):
```python
ESSENTIAL_ITEMS = [1, 1109, 1110, 1111, 129, 114, 94, YOUR_NEW_CODE]
```

**Step 3 — Add to the chart** (`src/chart_pricecatcher.py`, `ITEM_MAP` dict):
```python
ITEM_MAP = {
    ...
    YOUR_NEW_CODE: "Potato (1kg)",
}
```

**Step 4 — Add to the dashboard cards** (`src/extract_stats.py`, `ITEM_MAP` dict):
```python
ITEM_MAP = {
    ...
    "YOUR_NEW_CODE": ("Potato", "per kg"),
}
```

**Step 5 — Run the update**
```bash
bash update.sh
```

---

## ➕ How to Add a New Exchange Rate Currency

**Step 1 — Check available currencies** in `fetch_exchange.py`:
The BNM API returns many currencies. Currently we save: `usd, sgd, eur, gbp`.
To add JPY for example, open `src/fetch_exchange.py` and add `"jpy"` to the `.select([...])` list.

**Step 2 — Show it in the table** (`docs/index.html`):
1. Add a `<th>JPY</th>` column header in the exchange table
2. Add `<td>...</td>` for it in the JS row-building block (search for `ex-body`)
3. Add `jpy_chg` calculation in `src/extract_stats.py`

---

## 🔧 How to Change the Dashboard (HTML)

The dashboard is one file: `docs/index.html`

- **Change colours** → edit the `:root { }` block at the top (CSS variables)
- **Change section titles** → find the `<h2>` tags
- **Change notes/disclaimers** → find the `<p class="note">` tags
- **Change the layout** → the grid/card styles are in the `<style>` block
- **After any change** → you need to push to GitHub for it to go live:

```bash
cd /home/eri/workspace/malaysia-data-simplifier
git add docs/index.html
git commit -m "your description of the change"
git push
```

---

## 🚀 How to Deploy (Push to Live Website)

The website lives on GitHub Pages. Anything inside `docs/` that gets pushed to
the `main` branch is automatically published.

```bash
cd /home/eri/workspace/malaysia-data-simplifier

git add docs/
git commit -m "describe your change"
git push
```

Wait 1–2 minutes, then hard-refresh the site (`Ctrl+Shift+R` on desktop,
or close and reopen tab on mobile).

---

## 🩺 Health Check & Troubleshooting

### Run the health check
```bash
cd /home/eri/workspace/malaysia-data-simplifier
source .venv/bin/activate
python src/validate.py
```

### Dashboard shows old data / not updating
1. Check the log: `tail -50 update.log`
2. Look for any `❌` error lines
3. Try running manually: `bash update.sh`

### A fetch script fails with a network error
- Check your internet connection
- The API might be temporarily down — try again in an hour
- Check if ProtonVPN is on (some scripts remind you at startup)

### Website updated locally but GitHub still shows old version
```bash
git status          # shows what files changed
git add docs/
git commit -m "fix"
git push
```

### Something broke and you want to undo the last change
```bash
git --no-pager log --oneline -5   # see recent commits
git revert HEAD                    # undo the last commit safely
git push
```

---

## 🤖 Working with AI Assistants

This project has two handoff files for when you use AI to help:

| File | Purpose |
|------|---------|
| `COPILOT_HANDOFF.md` | Summary for GitHub Copilot CLI of what was already changed |
| `FINAL_PLAN.md` | Original project design goals |

**When starting a new AI session**, tell it:
> "Read COPILOT_HANDOFF.md and OWNER_GUIDE.md before doing anything."

**For Gemini CLI** — resume your session with:
```
gemini --resume 54b618f7-a686-4570-abbd-0f274fc87f30
```
Or start fresh and say: *"Read COPILOT_HANDOFF.md first."*

---

## 📋 Quick Reference Card

| Task | Command |
|------|---------|
| Run full update now | `bash update.sh` |
| Check nightly timer | `systemctl --user list-timers` |
| Check last run | `tail -50 update.log` |
| Activate Python env | `source .venv/bin/activate` |
| Health check | `python src/validate.py` |
| Push website changes | `git add docs/ && git commit -m "msg" && git push` |
| See recent git history | `git --no-pager log --oneline -10` |
| Undo last commit | `git revert HEAD && git push` |
