# Deployment Guide - AI Agent Shop (أمين)

## Prerequisites
- Ubuntu 22.04+ server
- Docker & Docker Compose
- Domain name (optional, for SSL)
- Facebook/Instagram Developer Account
- Groq API Key
- Telegram Bot Token

## Quick Deploy

### 1. Clone & Configure
```bash
git clone <your-repo> ai-agent-shop
cd ai-agent-shop
cp .env.example .env
nano .env  # Add your API keys
```

### 2. Run with Docker
```bash
docker-compose up --build -d
```

### 3. Verify
```bash
curl http://localhost:8000/health
```

## Production Setup (with SSL)

### 1. Install Nginx & Certbot
```bash
apt update
apt install nginx certbot python3-certbot-nginx
```

### 2. Configure Domain
```nginx
# /etc/nginx/sites-available/ai-agent-shop
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Get SSL Certificate
```bash
certbot --nginx -d your-domain.com
```

### 4. Run as Service
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key |
| `FACEBOOK_APP_SECRET` | Facebook App Secret |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Facebook Page Access Token |
| `FACEBOOK_VERIFY_TOKEN` | Webhook verify token |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Instagram Business Account ID |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token |
| `TELEGRAM_STAFF_CHAT_ID` | Telegram chat ID for notifications |
| `APP_SECRET_KEY` | Secret key for the app |
| `ADMIN_USERNAME` | Admin dashboard username |
| `ADMIN_PASSWORD` | Admin dashboard password |

## Monitoring
- Prometheus metrics: `http://your-domain.com/metrics`
- Health check: `http://your-domain.com/health`
