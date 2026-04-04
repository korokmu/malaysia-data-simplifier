import json
import requests
import os
from datetime import datetime

# 1. Configuration
# You will need to put your Webhook URL here or set it as an environment variable
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "YOUR_WEBHOOK_URL_HERE")
STATS_FILE = "docs/latest_stats.json"

def send_discord_notification():
    if not os.path.exists(STATS_FILE):
        print(f"❌ {STATS_FILE} not found. Run extract_stats.py first.")
        return

    with open(STATS_FILE, "r") as f:
        data = json.load(f)

    # 2. Format the Message (Discord "Embed")
    # We pick the latest items to show
    weather_txt = ""
    if data.get("weather"):
        for w in data["weather"][:3]: # Top 3 cities
            f = w["forecasts"][0] # Today's forecast
            weather_txt += f"**{w['city']}**: {f['emoji']} {f['desc']} ({f['max']}°C)\n"

    fuel = data["fuel"][0]
    fuel_txt = (
        f"⛽ **RON95:** RM {fuel['ron95']:.2f}\n"
        f"⛽ **RON97:** RM {fuel['ron97']:.2f}\n"
        f"🚛 **Diesel:** RM {fuel['diesel']:.2f}"
    )

    ex = data["exchange"][0]
    ex_txt = (
        f"💵 **USD:** RM {ex['usd']:.2f}\n"
        f"🇸🇬 **SGD:** RM {ex['sgd']:.2f}\n"
        f"🇪🇺 **EUR:** RM {ex['eur']:.2f}"
    )

    embed = {
        "title": f"🇲🇾 Malaysia Daily Data — {data['update_time']}",
        "url": "https://korokmu.github.io/malaysia-data-simplifier/",
        "color": 3447003, # Nice blue color
        "fields": [
            {"name": "🌦️ Weather (Today)", "value": weather_txt or "No data", "inline": False},
            {"name": "⛽ Fuel Prices", "value": fuel_txt, "inline": True},
            {"name": "💹 Exchange Rates", "value": ex_txt, "inline": True},
        ],
        "footer": {"text": "Data from data.gov.my | Automatically updated at 2:00 AM"}
    }

    payload = {
        "content": "🚀 **Daily update is live!** Check the dashboard for more details.",
        "embeds": [embed]
    }

    # 3. Send to Discord
    if DISCORD_WEBHOOK_URL == "YOUR_WEBHOOK_URL_HERE":
        print("⚠️ Discord Webhook URL not set. Skipping notification.")
        print("💡 Message would have been:")
        print(json.dumps(payload, indent=2))
        return

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Discord notification sent!")
    except Exception as e:
        print(f"❌ Failed to send Discord notification: {e}")

if __name__ == "__main__":
    send_discord_notification()
