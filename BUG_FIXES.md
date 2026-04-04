# Bug Fixes Report — Malaysia Data Simplifier

## Mobile UI & Navigation Fixes (v1.0 — April 2026)

| Issue | Root Cause | Fix |
|-------|------------|-----|
| **Table scroll gradient "sticking"** | Absolute-positioned pseudo-elements (`::after`) on iPhone Safari often lag or misalign during momentum scrolling. | Replaced with a **pure CSS-only scroll shadow** using `background-attachment: local, scroll`. This uses the browser's native background rendering which is perfectly sync'ed with scroll. |
| **Sticky nav "double highlight"** | `IntersectionObserver` triggered multiple times when sections crossed the viewport, causing two links to be blue at once. | Replaced with a **single scroll listener** that calculates the most prominent section based on offset and clears all other highlights explicitly. |
| **Mobile "sticky hover" state** | Mobile browsers simulate "hover" on tap, which keeps the blue background on a link even after the finger is removed. | 1. Wrapped hover styles in `@media (hover: hover)` so they only apply to mouse users.<br>2. Added `link.blur()` on click to force the mobile browser to release the focus state. |
| **Top-of-page highlight** | Nav links sometimes stayed highlighted when scrolling back to the very top header. | Added a fallback check: if `window.scrollY < 80`, all navigation highlights are cleared. |

---

## Weather Reliability Fix (v1.2 — April 2026)

| Issue | Root Cause | Fix |
|-------|------------|-----|
| **3 states missing weather** | Open-Meteo API randomly times out for some cities. When a city failed, it was simply dropped — the parquet was written without it. | `fetch_weather.py` now: (1) retries once on timeout with a 2s delay, (2) falls back to the previous run's cached data for any city that fails both attempts. All 16 states now always present. |
| **Hardcoded chart title** | `chart_pricecatcher.py` had `"April 2026"` hardcoded in the chart title. | Replaced with `datetime.now().strftime('%B %Y')` — updates automatically each month. |
| **Exchange chart incomplete** | `chart_exchange.py` only plotted 3 of 8 currencies (USD, SGD, EUR). | Chart removed entirely. The table + traveler calculator cover all 8 currencies more clearly. |

