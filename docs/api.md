# API Documentation - AI Agent Shop (أمين)

## Base URL
```
http://localhost:8000
```

## Endpoints

### Webhooks

#### `GET /webhooks/facebook`
Facebook Messenger webhook verification.

**Query Parameters:**
- `hub_mode` (string) - Must be "subscribe"
- `hub_verify_token` (string) - Your verify token
- `hub_challenge` (string) - Challenge string to return

**Response:** `200` with challenge string

#### `POST /webhooks/facebook`
Receive Facebook Messenger messages.

**Headers:**
- `X-Hub-Signature-256` - HMAC-SHA256 signature

**Body:** Facebook webhook payload

**Rate Limit:** 10/minute

#### `GET /webhooks/instagram`
Instagram webhook verification (same as Facebook).

#### `POST /webhooks/instagram`
Receive Instagram Direct messages.

### Health

#### `GET /health`
Service health check.

#### `GET /metrics`
Prometheus metrics endpoint.

### Admin

All admin endpoints require HTTP Basic Auth.

#### `GET /admin/`
Dashboard with statistics and charts.

#### `GET /admin/products`
List and manage products.

#### `POST /admin/products`
Create a new product.

#### `GET /admin/products/{id}`
Edit product form.

#### `POST /admin/products/{id}/edit`
Update product.

#### `POST /admin/products/{id}/delete`
Delete product.

#### `GET /admin/orders`
List all orders.

#### `GET /admin/orders/{id}`
Order detail with status management.

#### `POST /admin/orders/{id}/status`
Update order status.

#### `GET /admin/customers`
List all customers.

#### `GET /admin/customers/{id}`
Customer detail with order history.

#### `GET /admin/conversations`
List all conversations.

#### `GET /admin/orders/export`
Export orders as CSV.

### Interactive API Docs
- Swagger: `/docs`
- ReDoc: `/redoc`
