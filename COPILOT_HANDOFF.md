# Copilot Handoff — Malaysia Data Simplifier

Read this before continuing work on the project. It summarises what was changed
during the GitHub Copilot CLI session so you don't repeat or undo anything.

---

## Live Site
https://korokmu.github.io/malaysia-data-simplifier/

## What the project does
Automated daily pipeline that pulls Malaysian public data (fuel prices, grocery
prices, exchange rates) and publishes a lightweight, mobile-friendly dashboard
to GitHub Pages. Runs on a Celeron (no-AVX) Arch Linux machine via systemd
timer at 2:00 AM.

---

## Changes Made in This Session

### `docs/index.html` — Dashboard UI

| What | Detail |
|------|--------|
| **Grocery chart** | Fixed to show last 6 months ending on the latest available date (was using hardcoded end date) |
| **Egg grades** | Added Grade B and Grade C eggs to the grocery grid + pricecatcher chart ITEM_MAP (previously only Grade A was shown) |
| **BUDI RON95** | Added BUDI RON95 (subsidised fuel with IC/MyKad) column to the fuel table — fetched alongside the other weekly fuel prices |
| **Exchange rate format** | Rates now display as `RM4.44` (with RM prefix, 2 decimal places) to be immediately readable |
| **Notes for viewers** | Added disclaimer notes under Grocery, Fuel, and Exchange sections explaining price variance, subsidy eligibility, and BNM as data source |
| **Data tables fix** | Tables were not rendering — fixed JS data-binding so fuel and exchange rows populate correctly |
| **Sticky nav bar** | Added sticky top nav: `Jump to: 🛒 Grocery  ⛽ Fuel  💹 Exchange` |
| **Active nav highlight** | Current section highlights blue in the nav as you scroll (IntersectionObserver) |
| **Back-to-top button** | Fixed floating ↑ button appears after scrolling 300 px |
| **Scroll gradient** | White fade on right edge of fuel/exchange tables signals hidden columns on mobile; disappears when fully scrolled. Bug fixed: was checking before fetch filled the table, now `checkAllTables()` is called inside the fetch callback |

### `src/` — Python scripts

| File | Change |
|------|--------|
| `fetch_fuel.py` | Added BUDI RON95 price fetch from DOSM/MOF weekly data |
| `chart_pricecatcher.py` | Added Grade B & Grade C eggs to `ITEM_MAP`; chart end date now uses latest available date dynamically |
| `extract_stats.py` | Updated to include `ron95_budi95` and `budi_chg` fields in `latest_stats.json` |

### `docs/latest_stats.json`
Updated schema — fuel objects now include `ron95_budi95` and `budi_chg` fields.

---

## Current Dashboard Sections

1. **🛒 Grocery** — national average prices (cards grid) + 6-month Plotly chart
   - Items: Rice, Sugar, Cooking Oil, Chicken, Beef, Fish, Eggs (Grade A/B/C), Flour
2. **⛽ Fuel** — weekly price table with change indicators
   - Columns: Date | RON95 | BUDI RON95 | RON97 | Diesel | Diesel (East M'sia)
3. **💹 Exchange Rates** — weekly BNM rates with change indicators
   - Columns: Date | USD | SGD | EUR

---

## Data Sources
| Data | Source |
|------|--------|
| Fuel prices | DOSM / MOF weekly APM |
| Grocery prices | data.gov.my PriceCatcher API |
| Exchange rates | Bank Negara Malaysia (BNM) API |

---

## Automation
- **Script:** `update.sh` runs all `src/fetch_*.py` → `src/chart_*.py` → `src/extract_stats.py` → git push
- **Schedule:** systemd timer, daily 2:00 AM
- **Log:** `update.log`

---

## What's NOT Done / Ideas for Next
- Weather section (was in FINAL_PLAN.md audience targets for visitors)
- More exchange rate currencies (JPY, GBP, AUD, etc.)
- Price trend alerts (e.g. highlight if fuel jumped significantly)
- No tests — validate.py exists but coverage is minimal

---

## Known Issues at Handoff
- None critical. All sections render correctly on mobile (POCO F3) and desktop.
- The gradient scroll hint relies on `checkAllTables()` being called after the
  fetch — if you refactor the data loading, make sure to keep that call.
