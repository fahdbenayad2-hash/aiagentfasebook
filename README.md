# 🤖 AI Agent Shop - أمين

نظام رد آلي ذكي للمتاجر الإلكترونية الجزائرية عبر فيسبوك وإنستجرام.

## المميزات
- 🤖 رد آلي باستخدام Groq AI (llama-3.3-70b-versatile)
- 📱 دعم فيسبوك ماسنجر وإنستجرام دايركت
- 🛒 استقبال طلبات COD (الدفع عند الاستلام)
- 📍 دعم الولايات الجزائرية الـ 58
- 🔔 إشعارات Telegram للموظفين
- 🖥️ لوحة تحكم مع إحصائيات ورسوم بيانية (Chart.js)
- 🛡️ Rate Limiting + HTTP Basic Auth
- 📊 تصدير الطلبات CSV
- 📝 سجل محادثات كامل
- 🐳 Docker + Docker Compose
- 📈 Prometheus metrics

## التشغيل السريع
```bash
cp .env.example .env
# عدل ملف .env بمفاتيح API
docker-compose up --build -d
```

## الوصول
| الخدمة | الرابط |
|--------|--------|
| API | http://localhost:8000 |
| Admin | http://localhost:8000/admin/ |
| Docs | http://localhost:8000/docs |
| Metrics | http://localhost:8000/metrics |

## الإنتاج
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

## التوثيق
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Webhook Setup](docs/webhook-setup.md)
- [Telegram Bot Setup](docs/telegram-setup.md)

## التشغيل المحلي
```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## الاختبارات
```bash
pip install pytest pytest-asyncio pytest-cov
pytest tests/ -v --cov=app
```
