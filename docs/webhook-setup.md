# Facebook & Instagram Webhook Setup Guide

## Facebook Messenger

### 1. Create Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app (type: Business)
3. Add "Messenger" product

### 2. Get Page Access Token
1. Go to Messenger → Settings
2. Generate a Page Access Token
3. Copy the token to `FACEBOOK_PAGE_ACCESS_TOKEN`

### 3. Configure Webhook
1. Messenger → Settings → Webhooks
2. Callback URL: `https://your-domain.com/webhooks/facebook`
3. Verify Token: Same as `FACEBOOK_VERIFY_TOKEN`
4. Subscribe to: `messages`, `messaging_postbacks`

### 4. Get App Secret
1. Settings → Basic → App Secret
2. Copy to `FACEBOOK_APP_SECRET`

### 5. Test
Send a message to your Facebook Page. The bot should reply.

## Instagram Direct

### 1. Instagram Business Account
1. Convert your Instagram to a Business/Creator account
2. Connect it to your Facebook Page

### 2. Get Instagram Business Account ID
1. Go to Graph API Explorer: `https://developers.facebook.com/tools/explorer/`
2. GET `me/accounts` → get Page ID
3. GET `{page_id}?fields=instagram_business_account`
4. Copy `id` to `INSTAGRAM_BUSINESS_ACCOUNT_ID`

### 3. Configure Webhook
Same as Facebook webhook, add Instagram events:
- Webhook URL: `https://your-domain.com/webhooks/instagram`
- Subscribe to Instagram events

### 4. Test
Send a DM to your Instagram account. The bot should reply.

## Troubleshooting

### Common Issues

**403 Verification Failed**
- Check `FACEBOOK_VERIFY_TOKEN` matches both .env and Facebook settings
- Ensure webhook URL is publicly accessible (not localhost)

**401 Invalid Signature**
- Verify `FACEBOOK_APP_SECRET` is correct
- Check server time is accurate (NTP sync)

**No Response to Messages**
- Verify `FACEBOOK_PAGE_ACCESS_TOKEN` has proper permissions
- Check webhook is subscribed to `messages` event
- Check logs: `docker-compose logs app`
