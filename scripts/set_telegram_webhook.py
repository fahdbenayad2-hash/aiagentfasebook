import httpx
import sys

TOKEN = sys.argv[1] if len(sys.argv) > 1 else input("TELEGRAM_BOT_TOKEN: ")
WEBHOOK_URL = sys.argv[2] if len(sys.argv) > 2 else input("Webhook URL (ex: https://ton-domaine.com/webhooks/telegram): ")

url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
r = httpx.post(url, json={"url": WEBHOOK_URL})
print(r.json())
