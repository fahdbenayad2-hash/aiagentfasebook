# Telegram Bot Setup Guide

## Prerequisites
- Telegram account
- Docker & Docker Compose (for running the app)

## 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the prompts
3. Choose a name (e.g., "متجر أمين - إشعارات")
4. Choose a username (e.g., `amin_shop_bot`)
5. Copy the API token (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## 2. Get Your Staff Chat ID

### Option A: Group Chat
1. Create a new Telegram group
2. Add your bot to the group as admin
3. Send a message in the group
4. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
5. Find your group chat ID (negative number, e.g., `-1001234567890`)

### Option B: Direct Messages
1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find `chat.id` from the response

## 3. Configure Environment

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_STAFF_CHAT_ID=-1001234567890
```

## 4. Test Notifications

After starting the app, place a test order through the bot. You should receive a notification in your Telegram chat:

```
🛒 طلب جديد!
━━━━━━━━━━━━━━
👤 العميل: أحمد محمد
📱 الهاتف: 0555123456
📍 الولاية: الجزائر
🏠 العنوان: باب الزوار، حي 5 جويلية
━━━━━━━━━━━━━━
📦 المنتجات:
• تيشيرت - 1500 دج × 1
━━━━━━━━━━━━━━
💰 الإجمالي: 1500 دج
🆔 رقم الطلب: #1
```

## Troubleshooting

**No notifications received:**
- Ensure bot is added to the group and is admin
- Check `TELEGRAM_STAFF_CHAT_ID` is correct (negative for groups)
- Verify `TELEGRAM_BOT_TOKEN` is correct
- Check app logs: `docker-compose logs app`
