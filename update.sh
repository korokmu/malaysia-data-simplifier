#!/bin/bash
# Daily update script for Malaysia Data Simplifier
# Fetches fresh data, regenerates charts, and pushes to GitHub Pages

set -e  # stop if any command fails

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$PROJECT_DIR/update.log"
PYTHON="$PROJECT_DIR/.venv/bin/python3"

echo "==============================" >> "$LOG_FILE"
echo "$(date): Starting daily update" >> "$LOG_FILE"

cd "$PROJECT_DIR"

# Fetch fresh data
$PYTHON src/fetch_fuel.py         >> "$LOG_FILE" 2>&1
$PYTHON src/fetch_exchange.py     >> "$LOG_FILE" 2>&1
$PYTHON src/fetch_pricecatcher.py >> "$LOG_FILE" 2>&1

# Regenerate charts and stats
$PYTHON src/chart_fuel.py         >> "$LOG_FILE" 2>&1
$PYTHON src/chart_exchange.py     >> "$LOG_FILE" 2>&1
$PYTHON src/chart_pricecatcher.py >> "$LOG_FILE" 2>&1
$PYTHON src/extract_stats.py      >> "$LOG_FILE" 2>&1

# Validate everything looks OK
$PYTHON src/validate.py           >> "$LOG_FILE" 2>&1

# Commit and push updated docs/ to GitHub Pages
git add docs/
git diff --cached --quiet && echo "$(date): No changes to commit" >> "$LOG_FILE" && exit 0

git commit -m "chore: daily data update $(date '+%Y-%m-%d')"
git push

echo "$(date): Update complete ✅" >> "$LOG_FILE"
