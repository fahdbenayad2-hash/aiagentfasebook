import secrets
import csv
import html
import io
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Product, Order, Customer, Conversation
from app.config import get_settings
from app.services.conversation_manager import invalidate_products_cache
from app.services.logging_service import logger
from app.services.notification_service import send_telegram_notification

router = APIRouter(prefix="/admin", tags=["admin"])
settings = get_settings()


def verify_admin_auth(request: Request):
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"})
    try:
        scheme, token = auth.split()
        if scheme.lower() != "basic":
            raise ValueError
        decoded = base64.b64decode(token).decode()
        username, password = decoded.split(":", 1)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid auth",
            headers={"WWW-Authenticate": "Basic"})
    if username != settings.ADMIN_USERNAME or password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"})


PAGE = """<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - MARIA</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Segoe UI',Tahoma,sans-serif;background:#f5f5f5}}
.sidebar{{width:250px;background:#1a237e;color:white;position:fixed;height:100vh;padding:20px;overflow-y:auto}}
.sidebar h1{{font-size:1.5rem;margin-bottom:30px}}.sidebar a{{display:block;color:white;text-decoration:none;padding:12px;border-radius:8px;margin:5px 0;transition:background .2s}}
.sidebar a:hover{{background:#3949ab}}.sidebar a.active{{background:#3949ab}}
.main{{margin-right:250px;padding:30px}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-bottom:30px}}
.stat-card{{background:white;padding:25px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
.stat-card h3{{color:#666;font-size:.9rem;margin-bottom:10px}}.stat-card .number{{font-size:2rem;font-weight:bold;color:#1a237e}}
.stat-card .small{{font-size:.85rem;color:#999;margin-top:5px}}
table{{width:100%;background:white;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
th,td{{padding:15px;text-align:right;border-bottom:1px solid #eee}}th{{background:#f8f9fa;font-weight:600;color:#555}}
tr:hover{{background:#f8f9fa}}
.btn{{padding:10px 20px;background:#1a237e;color:white;border:none;border-radius:8px;cursor:pointer;font-size:.9rem;transition:background .2s;text-decoration:none;display:inline-block}}
.btn:hover{{background:#3949ab}}.btn-sm{{padding:6px 14px;font-size:.8rem}}.btn-danger{{background:#d32f2f}}.btn-danger:hover{{background:#b71c1c}}
.btn-success{{background:#2e7d32}}.btn-success:hover{{background:#1b5e20}}
.badge{{padding:5px 12px;border-radius:20px;font-size:.8rem}}
.badge-pending{{background:#fff3e0;color:#e65100}}.badge-confirmed{{background:#e8f5e9;color:#2e7d32}}
.badge-shipped{{background:#e3f2fd;color:#1565c0}}.badge-delivered{{background:#f3e5f5;color:#6a1b9a}}
.badge-cancelled{{background:#ffebee;color:#c62828}}
.badge-IDLE,.badge-GREETING,.badge-FAQ,.badge-BROWSE,.badge-COLLECT_NAME,.badge-COLLECT_PHONE,.badge-COLLECT_STATE,.badge-COLLECT_ADDRESS,.badge-CONFIRM,.badge-ORDER_COMPLETE,.badge-HANDOFF{{background:#e8eaf6;color:#1a237e}}
.card{{background:white;border-radius:12px;padding:25px;box-shadow:0 2px 8px rgba(0,0,0,0.1);margin-bottom:20px}}
.form-group{{margin-bottom:15px}}.form-group label{{display:block;margin-bottom:5px;color:#555;font-weight:600}}
.form-control{{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:.9rem;box-sizing:border-box}}
select.form-control{{padding:10px}}
.mt-20{{margin-top:20px}}.mb-20{{margin-bottom:20px}}.flex{{display:flex;gap:10px;align-items:center}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.text-muted{{color:#999;font-size:.85rem}}
.chart-container{{background:white;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.1);margin-bottom:20px}}
@media(max-width:768px){{.sidebar{{width:100%;height:auto;position:relative}}.main{{margin-right:0}}.stats{{grid-template-columns:1fr 1fr}}.grid-2{{grid-template-columns:1fr}}}}
</style></head><body>
<div class="sidebar"><h1>✦ MARIA</h1>
<a href="/admin/" class="{s_dash}">الرئيسية</a>
<a href="/admin/products" class="{s_prod}">المنتجات</a>
<a href="/admin/orders" class="{s_ord}">الطلبات</a>
<a href="/admin/customers" class="{s_cust}">العملاء</a>
<a href="/admin/conversations" class="{s_conv}">المحادثات</a>
<a href="/admin/facebook/connections" class="{s_acct}">🔗 الحسابات المتصلة</a>
<a href="/admin/token" class="{s_tok}">🔑 التوكن</a>
<a href="/admin/learning" class="{s_learn}">📊 التعلم</a>
<hr style="border-color:#3949ab;margin:20px 0">
<a href="/admin/orders/export">📥 تصدير CSV</a>
</div>
<div class="main">{content}</div></body></html>"""


def render_page(title: str, content: str, active: str = "") -> str:
    return PAGE.format(
        title=title,
        content=content,
        s_dash="active" if active == "dashboard" else "",
        s_prod="active" if active == "products" else "",
        s_ord="active" if active == "orders" else "",
        s_cust="active" if active == "customers" else "",
        s_conv="active" if active == "conversations" else "",
        s_acct="active" if active == "accounts" else "",
        s_tok="active" if active == "token" else "",
        s_learn="active" if active == "learning" else "",
    )


@router.get("/")
async def dashboard_redirect(request: Request):
    return RedirectResponse(url="/dashboard")

    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
    rows = ""
    for o in recent_orders:
        cname = html.escape(o.customer.name) if o.customer else 'غير معروف'
        rows += f"<tr><td>#{o.id}</td><td>{cname}</td><td><span class='badge badge-{html.escape(o.status)}'>{html.escape(o.status)}</span></td><td>{o.total_price} دج</td><td>{o.created_at.strftime('%Y-%m-%d %H:%M')}</td><td><a href='/admin/orders/{o.id}' class='btn btn-sm'>عرض</a></td></tr>"

    statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    sc = {}
    for s in statuses:
        sc[s] = db.query(Order).filter(Order.status == s).count()

    weekly_data = []
    for i in range(6, -1, -1):
        day = today_start - timedelta(days=i)
        next_day = day + timedelta(days=1)
        count = db.query(Order).filter(
            Order.created_at >= day,
            Order.created_at < next_day
        ).count()
        weekly_data.append(count)

    from app.services.facebook import facebook_send
    token_status = facebook_send.token_status if hasattr(facebook_send, "token_status") else "unknown"
    tk_icon = {"valid": "✅", "expired": "🚨", "unknown": "❓"}.get(token_status, "❓")
    tk_text = {"valid": "صالح", "expired": "منتهي", "unknown": "غير معروف"}.get(token_status, "غير معروف")
    tk_color = {"valid": "#2e7d32", "expired": "#c62828", "unknown": "#e65100"}.get(token_status, "#e65100")

    content = f"""<h2 class="mb-20">لوحة التحكم</h2>
<div class="stats">
<div class="stat-card"><h3>إجمالي الطلبات</h3><div class="number">{total_orders}</div><div class="small">منذ البدء</div></div>
<div class="stat-card"><h3>طلبات معلقة</h3><div class="number">{pending_orders}</div><div class="small">بحاجة للمراجعة</div></div>
<div class="stat-card"><h3>العملاء</h3><div class="number">{total_customers}</div><div class="small">مسجلين</div></div>
<div class="stat-card"><h3>المنتجات النشطة</h3><div class="number">{total_products}</div><div class="small">متاحة للبيع</div></div>
<div class="stat-card" style="border-right:4px solid {tk_color}"><h3>🔑 توكن فيسبوك</h3><div class="number" style="color:{tk_color}">{tk_icon} {tk_text}</div><div class="small"><a href="/admin/token" style="color:{tk_color}">تجديد</a></div></div>
</div>
<div class="grid-2">
<div class="stat-card"><h3>طلبات اليوم</h3><div class="number">{today_orders}</div></div>
<div class="stat-card"><h3>الإيرادات</h3><div class="number">{revenue} دج</div><div class="small">من الطلبات المكتملة</div></div>
</div>
<div class="chart-container"><h3 class="mb-20">حالة الطلبات</h3><canvas id="ordersChart" height="80"></canvas></div>
<div class="chart-container"><h3 class="mb-20">الطلبات آخر 7 أيام</h3><canvas id="weeklyChart" height="80"></canvas></div>
<script>
new Chart(document.getElementById('ordersChart'),{{type:'doughnut',data:{{labels:['معلق','مؤكد','تم الشحن','تم التوصيل','ملغي'],datasets:[{{data:[{sc['pending']},{sc['confirmed']},{sc['shipped']},{sc['delivered']},{sc['cancelled']}],backgroundColor:['#e65100','#2e7d32','#1565c0','#6a1b9a','#c62828']}}]}}}});
new Chart(document.getElementById('weeklyChart'),{{type:'bar',data:{{labels:['قبل 6','قبل 5','قبل 4','قبل 3','قبل 2','أمس','اليوم'],datasets:[{{label:'الطلبات',data:[{','.join(map(str,weekly_data))}],backgroundColor:'#1a237e'}}]}}}});
</script>
<h3 class="mb-20 mt-20">آخر الطلبات</h3>
<table><thead><tr><th>رقم الطلب</th><th>العميل</th><th>الحالة</th><th>المبلغ</th><th>التاريخ</th><th></th></tr></thead><tbody>{rows}</tbody></table>"""

    return HTMLResponse(content=render_page("لوحة التحكم", content, "dashboard"))


@router.get("/products", response_class=HTMLResponse)
async def products_list(request: Request, db: Session = Depends(get_db)):
    verify_admin_auth(request)
    products = db.query(Product).order_by(Product.created_at.desc()).all()
    rows = ""
    for p in products:
        badge = "confirmed" if p.active else "cancelled"
        status = "نشط" if p.active else "معطل"
        rows += f"<tr><td>{p.id}</td><td>{html.escape(p.name)}</td><td>{p.price} دج</td><td>{p.stock}</td>"
        rows += f"<td>{html.escape(p.category) if p.category else '-'}</td>"
        rows += f"<td><span class='badge badge-{badge}'>{status}</span></td>"
        cols = "".join(f"<span class='badge'>{html.escape(c)}</span>" for c in p.get_colors())
        sizes = "".join(f"<span class='badge'>{html.escape(s)}</span>" for s in p.get_sizes())
        rows += f"<td>{cols}</td><td>{sizes}</td>"
        rows += f"<td class='flex'><a href='/admin/products/{p.id}' class='btn btn-sm'>تعديل</a>"
        rows += f"<form method='post' action='/admin/products/{p.id}/delete' style='display:inline'>"
        rows += f"<button type='submit' class='btn btn-sm btn-danger' onclick=\"return confirm('تأكيد الحذف؟')\">حذف</button></form></td></tr>"

    content = f"""<h2 class="mb-20">إدارة المنتجات</h2>
<div class="card"><h3 class="mb-20">إضافة منتج جديد</h3>
<form method="post" action="/admin/products">
<div class="grid-2">
<div class="form-group"><label>اسم المنتج</label><input name="name" class="form-control" required></div>
<div class="form-group"><label>السعر (دج)</label><input name="price" type="number" class="form-control" required></div>
<div class="form-group"><label>القسم</label><input name="category" class="form-control" placeholder="قنادر, بيجامات, ..."></div>
<div class="form-group"><label>الوصف</label><input name="description" class="form-control"></div>
<div class="form-group"><label>المخزون</label><input name="stock" type="number" class="form-control" value="0"></div>
<div class="form-group"><label>الألوان</label><input name="colors" class="form-control" placeholder="أبيض, أسود, وردي"></div>
<div class="form-group"><label>المقاسات</label><input name="sizes" class="form-control" placeholder="S, M, L, XL, XXL"></div>
<div class="form-group"><label>معرفات المنتجات المكملة</label><input name="complementary_product_ids" class="form-control" placeholder="2,3,5"></div>
</div>
<button type="submit" class="btn mt-20">➕ إضافة منتج</button>
</form></div>
<table><thead><tr><th>ID</th><th>الاسم</th><th>السعر</th><th>المخزون</th><th>القسم</th><th>الألوان</th><th>المقاسات</th><th>الحالة</th><th>إجراءات</th></tr></thead><tbody>{rows}</tbody></table>"""
    return HTMLResponse(content=render_page("المنتجات", content, "products"))


@router.post("/products")
async def create_product(
    request: Request, name: str = Form(...), price: int = Form(...),
    category: str = Form(""), description: str = Form(""),
    stock: int = Form(0), complementary_product_ids: str = Form(""),
    colors: str = Form(""), sizes: str = Form(""),
    db: Session = Depends(get_db)
):
    verify_admin_auth(request)
    product = Product(
        name=name.strip(), price=price, category=category.strip() or None,
        description=description.strip(), stock=stock,
        complementary_product_ids=complementary_product_ids.strip() or None
    )
    if colors.strip():
        product.set_colors([c.strip() for c in colors.split(",") if c.strip()])
    if sizes.strip():
        product.set_sizes([s.strip() for s in sizes.split(",") if s.strip()])
    db.add(product)
    db.commit()
    invalidate_products_cache()
    return RedirectResponse(url="/admin/products", status_code=303)


@router.get("/products/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: int, db: Session = Depends(get_db)):
    verify_admin_auth(request)
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    content = f"""<h2 class="mb-20">تعديل المنتج: {html.escape(p.name)}</h2>
<div class="card"><form method="post" action="/admin/products/{p.id}/edit">
<div class="grid-2">
<div class="form-group"><label>اسم المنتج</label><input name="name" class="form-control" value="{html.escape(p.name)}" required></div>
<div class="form-group"><label>السعر (دج)</label><input name="price" type="number" class="form-control" value="{p.price}" required></div>
<div class="form-group"><label>القسم</label><input name="category" class="form-control" value="{html.escape(p.category or '')}"></div>
<div class="form-group"><label>الوصف</label><textarea name="description" class="form-control">{html.escape(p.description or '')}</textarea></div>
<div class="form-group"><label>المخزون</label><input name="stock" type="number" class="form-control" value="{p.stock}"></div>
<div class="form-group"><label>الألوان</label><input name="colors" class="form-control" value="{html.escape(p.colors or '')}" placeholder="أبيض, أسود, وردي"></div>
<div class="form-group"><label>المقاسات</label><input name="sizes" class="form-control" value="{html.escape(p.sizes or '')}" placeholder="S, M, L, XL, XXL"></div>
<div class="form-group"><label>معرفات المنتجات المكملة</label><input name="complementary_product_ids" class="form-control" value="{html.escape(p.complementary_product_ids or '')}"></div>
<div class="form-group"><label>حالة المنتج</label>
<select name="active" class="form-control"><option value="1"{' selected' if p.active else ''}>نشط</option><option value="0"{' selected' if not p.active else ''}>معطل</option></select></div>
</div>
<button type="submit" class="btn mt-20">💾 حفظ التغييرات</button>
</form></div>"""
    return HTMLResponse(content=render_page("تعديل منتج", content, "products"))


@router.post("/products/{product_id}/edit")
async def edit_product(
    request: Request, product_id: int, name: str = Form(...),
    price: int = Form(...), category: str = Form(""),
    description: str = Form(""), stock: int = Form(0),
    active: int = Form(1), complementary_product_ids: str = Form(""),
    colors: str = Form(""), sizes: str = Form(""),
    db: Session = Depends(get_db)
):
    verify_admin_auth(request)
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    p.name = name.strip()
    p.price = price
    p.category = category.strip() or None
    p.description = description.strip()
    p.stock = stock
    p.active = bool(active)
    p.complementary_product_ids = complementary_product_ids.strip() or None
    if colors.strip():
        p.set_colors([c.strip() for c in colors.split(",") if c.strip()])
    else:
        p.colors = None
    if sizes.strip():
        p.set_sizes([s.strip() for s in sizes.split(",") if s.strip()])
    else:
        p.sizes = None
    db.commit()
    invalidate_products_cache()
    return RedirectResponse(url="/admin/products", status_code=303)


@router.post("/products/{product_id}/delete")
async def delete_product(request: Request, product_id: int, db: Session = Depends(get_db)):
    verify_admin_auth(request)
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(p)
    db.commit()
    invalidate_products_cache()
    return RedirectResponse(url="/admin/products", status_code=303)


@router.get("/orders", response_class=HTMLResponse)
async def orders_list(request: Request, db: Session = Depends(get_db)):
    verify_admin_auth(request)
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    rows = ""
    for o in orders:
        cname = html.escape(o.customer.name) if o.customer else 'غير معروف'
        rows += f"<tr><td>#{o.id}</td><td>{cname}</td><td><span class='badge badge-{html.escape(o.status)}'>{html.escape(o.status)}</span></td>"
        rows += f"<td>{o.total_price} دج</td><td>{o.created_at.strftime('%Y-%m-%d %H:%M')}</td>"
        rows += f"<td><a href='/admin/orders/{o.id}' class='btn btn-sm'>تفاصيل</a></td></tr>"

    content = f"""<h2 class="mb-20">الطلبات</h2>
<table><thead><tr><th>رقم الطلب</th><th>العميل</th><th>الحالة</th><th>المبلغ</th><th>التاريخ</th><th></th></tr></thead><tbody>{rows}</tbody></table>"""
    return HTMLResponse(content=render_page("الطلبات", content, "orders"))


@router.get("/orders/export")
async def export_orders(request: Request, db: Session = Depends(get_db)):
    verify_admin_auth(request)
    orders = db.query(Order).order_by(Order.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "العميل", "الهاتف", "الولاية", "العنوان", "الحالة", "الإجمالي", "ملاحظات", "التاريخ", "المنصة"])

    for o in orders:
        c = o.customer
        writer.writerow([
            o.id, c.name if c else "", c.phone if c else "",
            c.state if c else "", c.address if c else "",
            o.status, o.total_price, o.notes or "",
            o.created_at.strftime("%Y-%m-%d %H:%M"),
            c.platform if c else ""
        ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders_export.csv"}
    )


@router.get("/orders/{order_id}", response_class=HTMLResponse)
async def order_detail(request: Request, order_id: int, db: Session = Depends(get_db)):
    verify_admin_auth(request)
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")

    items_rows = ""
    for item in o.items:
        pname = html.escape(item.product.name) if item.product else 'غير معروف'
        items_rows += f"<tr><td>{pname}</td><td>{item.quantity}</td><td>{item.price_at_time} دج</td>"
        items_rows += f"<td>{item.price_at_time * item.quantity} دج</td></tr>"

    statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    status_opts = "".join(f"<option value='{s}'{' selected' if s == o.status else ''}>{s}</option>" for s in statuses)

    c = o.customer
    content = f"""<h2 class="mb-20">تفاصيل الطلب #{o.id}</h2>
<div class="grid-2">
<div class="card"><h3 class="mb-20">معلومات العميل</h3>
<p><strong>الاسم:</strong> {html.escape(c.name) if c else 'غير معروف'}</p>
<p><strong>الهاتف:</strong> {html.escape(c.phone) if c and c.phone else 'غير متوفر'}</p>
<p><strong>الولاية:</strong> {html.escape(c.state) if c and c.state else 'غير متوفر'}</p>
<p><strong>العنوان:</strong> {html.escape(c.address) if c and c.address else 'غير متوفر'}</p>
<p><strong>المنصة:</strong> {html.escape(c.platform) if c else 'غير معروف'}</p></div>
<div class="card"><h3 class="mb-20">معلومات الطلب</h3>
<p><strong>الحالة:</strong> <span class='badge badge-{html.escape(o.status)}'>{html.escape(o.status)}</span></p>
<p><strong>الإجمالي:</strong> {o.total_price} دج</p>
<p><strong>تاريخ الإنشاء:</strong> {o.created_at.strftime('%Y-%m-%d %H:%M')}</p>
<p><strong>آخر تحديث:</strong> {o.updated_at.strftime('%Y-%m-%d %H:%M')}</p>
<p><strong>ملاحظات:</strong> {html.escape(o.notes) if o.notes else 'لا توجد'}</p></div></div>
<div class="card"><h3 class="mb-20">تغيير الحالة</h3>
<form method="post" action="/admin/orders/{o.id}/status" class="flex">
<select name="status" class="form-control" style="width:200px">{status_opts}</select>
<button type="submit" class="btn btn-sm">تحديث الحالة</button>
</form></div>
<div class="card"><h3 class="mb-20">المنتجات</h3>
<table><thead><tr><th>المنتج</th><th>الكمية</th><th>السعر</th><th>المجموع</th></tr></thead><tbody>{items_rows}</tbody></table></div>"""
    return HTMLResponse(content=render_page(f"طلب #{o.id}", content, "orders"))


@router.post("/orders/{order_id}/status")
async def update_order_status(
    request: Request, order_id: int, status: str = Form(...), db: Session = Depends(get_db)
):
    verify_admin_auth(request)
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    o.status = status
    db.commit()
    return RedirectResponse(url=f"/admin/orders/{order_id}", status_code=303)


@router.get("/customers", response_class=HTMLResponse)
async def customers_list(request: Request, db: Session = Depends(get_db)):
    verify_admin_auth(request)
    customers = db.query(Customer).order_by(Customer.created_at.desc()).all()
    rows = ""
    for c in customers:
        order_count = db.query(Order).filter(Order.customer_id == c.id).count()
        rows += f"<tr><td>{c.id}</td><td>{html.escape(c.name) if c.name else 'غير معروف'}</td><td>{html.escape(c.phone) if c.phone else 'غير متوفر'}</td>"
        rows += f"<td>{html.escape(c.state) if c.state else 'غير متوفر'}</td><td>{html.escape(c.platform)}</td><td>{order_count}</td>"
        rows += f"<td>{c.created_at.strftime('%Y-%m-%d')}</td><td><a href='/admin/customers/{c.id}' class='btn btn-sm'>عرض</a></td></tr>"

    content = f"""<h2 class="mb-20">العملاء</h2>
<table><thead><tr><th>ID</th><th>الاسم</th><th>الهاتف</th><th>الولاية</th><th>المنصة</th><th>الطلبات</th><th>تاريخ التسجيل</th><th></th></tr></thead><tbody>{rows}</tbody></table>"""
    return HTMLResponse(content=render_page("العملاء", content, "customers"))


@router.get("/customers/{customer_id}", response_class=HTMLResponse)
async def customer_detail(request: Request, customer_id: int, db: Session = Depends(get_db)):
    verify_admin_auth(request)
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    orders = db.query(Order).filter(Order.customer_id == c.id).order_by(Order.created_at.desc()).all()
    orders_rows = ""
    for o in orders:
        orders_rows += f"<tr><td>#{o.id}</td><td><span class='badge badge-{o.status}'>{o.status}</span></td>"
        orders_rows += f"<td>{o.total_price} دج</td><td>{o.created_at.strftime('%Y-%m-%d')}</td>"
        orders_rows += f"<td><a href='/admin/orders/{o.id}' class='btn btn-sm'>عرض</a></td></tr>"

    total_spent = sum(o.total_price for o in orders)
    content = f"""<h2 class="mb-20">العميل: {html.escape(c.name) if c.name else 'غير معروف'}</h2>
<div class="grid-2">
<div class="card"><h3 class="mb-20">معلومات العميل</h3>
<p><strong>الاسم:</strong> {html.escape(c.name) if c.name else 'غير معروف'}</p>
<p><strong>الهاتف:</strong> {html.escape(c.phone) if c.phone else 'غير متوفر'}</p>
<p><strong>الولاية:</strong> {html.escape(c.state) if c.state else 'غير متوفر'}</p>
<p><strong>العنوان:</strong> {html.escape(c.address) if c.address else 'غير متوفر'}</p>
<p><strong>المنصة:</strong> {html.escape(c.platform)}</p>
<p><strong>آخر نشاط:</strong> {c.updated_at.strftime('%Y-%m-%d %H:%M')}</p></div>
<div class="card"><h3 class="mb-20">إحصائيات</h3>
<p><strong>إجمالي الطلبات:</strong> {len(orders)}</p>
<p><strong>إجمالي المشتريات:</strong> {total_spent} دج</p></div></div>
<div class="card"><h3 class="mb-20">طلبات العميل</h3>
<table><thead><tr><th>رقم الطلب</th><th>الحالة</th><th>المبلغ</th><th>التاريخ</th><th></th></tr></thead><tbody>{orders_rows}</tbody></table></div>"""
    return HTMLResponse(content=render_page(f"العميل {c.name or ''}", content, "customers"))


@router.get("/conversations", response_class=HTMLResponse)
async def conversations_list(request: Request, db: Session = Depends(get_db)):
    verify_admin_auth(request)
    conversations = db.query(Conversation).order_by(Conversation.last_message_at.desc()).all()
    rows = ""
    for conv in conversations:
        cname = html.escape(conv.customer.name) if conv.customer else 'غير معروف'
        msg_count = len(conv.messages) if conv.messages else 0
        last_msg = ""
        if conv.messages and len(conv.messages) > 0:
            last_msg = html.escape(conv.messages[-1].get("content", "")[:50])
        platform_icon = "📘" if conv.platform == "facebook" else "📸"
        state_class = conv.current_state.lower().replace("_", "-")
        rows += f"<tr><td>{conv.id}</td><td>{cname}</td><td>{platform_icon} {html.escape(conv.platform)}</td>"
        rows += f"<td><span class='badge badge-{state_class}'>{html.escape(conv.current_state)}</span></td>"
        rows += f"<td>{msg_count}</td><td>{last_msg}</td>"
        rows += f"<td>{conv.last_message_at.strftime('%Y-%m-%d %H:%M')}</td></tr>"

    content = f"""<h2 class="mb-20">المحادثات</h2>
<table><thead><tr><th>ID</th><th>العميل</th><th>المنصة</th><th>الحالة</th><th>الرسائل</th><th>آخر رسالة</th><th>آخر نشاط</th></tr></thead><tbody>{rows}</tbody></table>"""
    return HTMLResponse(content=render_page("المحادثات", content, "conversations"))


@router.get("/accounts")
async def admin_accounts_redirect():
    return RedirectResponse(url="/admin/facebook/connections")


@router.get("/facebook/connect", response_class=RedirectResponse)
async def facebook_oauth_connect(request: Request):
    verify_admin_auth(request)
    from app.services.facebook_oauth import generate_csrf_token
    callback_url = settings.FB_REDIRECT_URI or f"{request.base_url}admin/facebook/callback"
    state = generate_csrf_token()
    redirect_url = (
        f"https://www.facebook.com/{settings.FB_API_VERSION}/dialog/oauth"
        f"?client_id={settings.FB_APP_ID}"
        f"&redirect_uri={callback_url}"
        f"&scope=pages_messaging,pages_manage_metadata,pages_read_engagement,pages_show_list"
        f"&state={state}"
    )
    return RedirectResponse(url=redirect_url)


@router.get("/facebook/callback")
async def facebook_oauth_callback(request: Request, code: str = "", state: str = ""):
    verify_admin_auth(request)
    from app.services.facebook_oauth import (
        verify_csrf_token, exchange_code_for_token, exchange_for_long_lived,
        get_user_pages, upsert_facebook_connection, mask_token,
    )

    if not verify_csrf_token(state):
        content = """<h2 class="mb-20">❌ خطأ في التحقق</h2>
<div class="card"><p>رمز CSRF غير صالح. حاول مرة أخرى.</p>
<a href="/admin/facebook/connect" class="btn">🔗 حاول مرة أخرى</a></div>"""
        return HTMLResponse(content=render_page("خطأ", content, "accounts"))

    callback_url = settings.FB_REDIRECT_URI or f"{request.base_url}admin/facebook/callback"
    try:
        short_token = await exchange_code_for_token(code, callback_url)
        long_token, expires_in = await exchange_for_long_lived(short_token)
        pages = await get_user_pages(long_token)
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=expires_in)

        connected = 0
        for page in pages:
            tasks = page.get("tasks", [])
            if "MESSAGING" in tasks:
                await upsert_facebook_connection(
                    page_id=page["id"],
                    page_name=page["name"],
                    page_access_token=page["access_token"],
                    user_access_token=long_token,
                    user_token_expires_at=expires_at,
                )
                connected += 1

        await send_telegram_notification(
            f"✅ تم ربط {connected} صفحة فيسبوك عبر OAuth!\n"
            f"{' | '.join(p['name'] for p in pages if 'MESSAGING' in p.get('tasks', []))}"
        )

        rows = ""
        for page in pages:
            has_messaging = "✅" if "MESSAGING" in page.get("tasks", []) else "❌"
            rows += f"<tr><td>{page['name']}</td><td>{page['id']}</td><td>{has_messaging}</td></tr>"

        content = f"""<h2 class="mb-20">✅ تم ربط {connected} صفحة بنجاح!</h2>
<div class="card"><table><thead><tr><th>اسم الصفحة</th><th>ID</th><th>المراسلة</th></tr></thead><tbody>{rows}</tbody></table>
<a href="/admin/facebook/connections" class="btn mt-20">🔗 إدارة الحسابات المتصلة</a></div>"""
        return HTMLResponse(content=render_page("✅ تم الربط", content, "accounts"))

    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        content = f"""<h2 class="mb-20">❌ فشل ربط الصفحة</h2>
<div class="card"><p>حدث خطأ: {html.escape(str(e))}</p>
<p>تأكد من:
<ul><li>تعيين FB_APP_ID و FB_APP_SECRET في .env</li>
<li>إضافة {html.escape(callback_url)} في Facebook App → Valid OAuth Redirect URIs</li>
<li>أن التطبيق في وضع النشر (Live mode)</li></ul>
</p><a href="/admin/facebook/connect" class="btn">🔗 حاول مرة أخرى</a></div>"""
        return HTMLResponse(content=render_page("❌ فشل الربط", content, "accounts"))


@router.get("/facebook/connections", response_class=HTMLResponse)
async def facebook_connections_page(request: Request):
    verify_admin_auth(request)
    from app.services.facebook_oauth import get_active_connections, delete_connection, mask_token, decrypt_token

    connections = await get_active_connections()
    rows = ""
    for conn in connections:
        token_preview = mask_token(decrypt_token(conn.page_access_token_encrypted))
        rows += f"""<tr>
<td>✅</td><td>{html.escape(conn.page_name)}</td>
<td style="direction:ltr">{conn.page_id}</td>
<td>{token_preview}</td>
<td style="direction:ltr">{conn.connected_at.strftime('%Y-%m-%d') if conn.connected_at else '-'}</td>
<td>{'لا ينتهي أبداً ✅' if conn.is_active else 'غير نشط'}</td>
<td>
<form method="post" action="/admin/facebook/disconnect" style="display:inline">
<input type="hidden" name="conn_id" value="{conn.id}">
<button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('تأكيد فصل الصفحة؟')">فصل</button>
</form>
</td></tr>"""

    content = f"""<h2 class="mb-20">🔗 صفحات فيسبوك المتصلة</h2>
<div class="card" style="text-align:center">
<a href="/admin/facebook/connect" class="btn">➕ ربط صفحة جديدة بفيسبوك</a>
<p class="text-muted" style="margin-top:10px">سيتم توجيهك إلى فيسبوك لتسجيل الدخول ومنح الصلاحيات.</p>
</div>
<div class="card">
<table><thead><tr><th></th><th>اسم الصفحة</th><th>ID</th><th>التوكن</th><th>متصل منذ</th><th>الحالة</th><th></th></tr></thead><tbody>{rows if rows else '<tr><td colspan="7" style="text-align:center">ماكاش صفحات متصلة 😊</td></tr>'}</tbody></table>
</div>"""
    return HTMLResponse(content=render_page("🔗 الحسابات المتصلة", content, "accounts"))


@router.post("/facebook/disconnect")
async def facebook_disconnect(request: Request, conn_id: int = Form(...)):
    verify_admin_auth(request)
    from app.services.facebook_oauth import delete_connection
    await delete_connection(conn_id)
    return RedirectResponse(url="/admin/facebook/connections", status_code=303)


@router.get("/learning", response_class=HTMLResponse)
async def admin_learning(request: Request, db: Session = Depends(get_db)):
    verify_admin_auth(request)
    from app.models import ConversationLog

    total = db.query(ConversationLog).count()
    completed = db.query(ConversationLog).filter(ConversationLog.completed_order == True).count()
    escalated = db.query(ConversationLog).filter(ConversationLog.escalated == True).count()
    success_rate = f"{completed / total * 100:.1f}" if total > 0 else "0.0"

    recent = db.query(ConversationLog).order_by(ConversationLog.created_at.desc()).limit(20).all()
    rows = ""
    for log in recent:
        icon = "✅" if log.completed_order else "🚨" if log.escalated else "💬"
        pname = html.escape(log.product_name) if log.product_name else "-"
        rows += f"<tr><td>{icon}</td><td>{html.escape(log.sender_id[-12:])}</td><td>{pname}</td><td>{log.message_count}</td><td>{log.created_at.strftime('%Y-%m-%d %H:%M') if log.created_at else '-'}</td></tr>"

    content = f"""<h2 class="mb-20">📊 التعلم — تحليل المحادثات</h2>
<div class="stats">
<div class="stat-card"><h3>إجمالي المحادثات</h3><div class="number">{total}</div></div>
<div class="stat-card"><h3>طلبات مكتملة</h3><div class="number">{completed}</div></div>
<div class="stat-card"><h3>تحويل لبشري</h3><div class="number">{escalated}</div></div>
<div class="stat-card"><h3>نسبة النجاح</h3><div class="number">{success_rate}%</div></div>
</div>
<h3 class="mb-20 mt-20">آخر المحادثات</h3>
<table><thead><tr><th></th><th>المرسل</th><th>المنتج</th><th>الرسائل</th><th>التاريخ</th></tr></thead><tbody>{rows}</tbody></table>"""
    return HTMLResponse(content=render_page("📊 التعلم", content, "learning"))


@router.get("/token", response_class=HTMLResponse)
async def admin_token(request: Request):
    verify_admin_auth(request)
    from app.services.facebook import facebook_send
    token_raw = settings.FB_PAGE_ACCESS_TOKEN or settings.FACEBOOK_PAGE_ACCESS_TOKEN
    token_status = facebook_send.token_status if hasattr(facebook_send, "token_status") else "unknown"
    short_preview = (token_raw[:12] + "...") if token_raw and len(token_raw) > 16 else "غير مضبوط"

    status_icon = {"valid": "✅", "expired": "🚨", "unknown": "❓"}
    status_text = {"valid": "صالح", "expired": "منتهي الصلاحية", "unknown": "غير معروف"}
    icon = status_icon.get(token_status, "❓")
    text = status_text.get(token_status, "غير معروف")

    has_app_id = bool(settings.FB_APP_ID and settings.FB_APP_SECRET)
    refresh_disabled = "" if has_app_id else "disabled"
    refresh_note = "" if has_app_id else "<p style='color:#c62828'>⚠️ يجب تعيين FB_APP_ID و FB_APP_SECRET في .env أولاً</p>"

    content = f"""<h2 class="mb-20">🔑 توكن فيسبوك</h2>
<div class="grid-2">
<div class="card">
    <h3 class="mb-20">حالة التوكن</h3>
    <p style="font-size:2rem;text-align:center">{icon}</p>
    <p style="text-align:center;font-size:1.2rem"><strong>{text}</strong></p>
    <p style="text-align:center;direction:ltr" class="text-muted">{short_preview}</p>
</div>
<div class="card">
    <h3 class="mb-20">تجديد التوكن</h3>
    {refresh_note}
    <form method="post" action="/admin/token/refresh" style="text-align:center">
        <button type="submit" class="btn" {refresh_disabled}>🔄 تجديد التوكن</button>
    </form>
    <p class="text-muted" style="margin-top:12px">يولّد توكن جديد صالح لـ 60 يوماً</p>
</div>
</div>
<div class="card">
    <h3 class="mb-20">التعليمات</h3>
    <ol style="padding-right:20px">
        <li>تأكد من تعيين <code>FB_APP_ID</code> و <code>FB_APP_SECRET</code> في <code>.env</code></li>
        <li>اضغط "تجديد التوكن" — سيتم تبادل التوكن الحالي بتوكن طويل الأمد (60 يوم)</li>
        <li>انسخ التوكن الجديد من الرد وضعه في <code>.env</code></li>
        <li>إذا ما جاز الإطالة، روح <a href="https://developers.facebook.com/apps/" target="_blank">لـ Facebook Developers</a> وولّد توكن يدوي</li>
    </ol>
</div>"""
    return HTMLResponse(content=render_page("🔑 التوكن", content, "token"))


@router.post("/token/refresh")
async def admin_token_refresh(request: Request):
    verify_admin_auth(request)
    import httpx
    from app.services.facebook import facebook_send

    current_token = settings.FB_PAGE_ACCESS_TOKEN or settings.FACEBOOK_PAGE_ACCESS_TOKEN
    if not current_token:
        raise HTTPException(status_code=400, detail="ماكش توكن في الإعدادات")
    if not settings.FB_APP_ID or not settings.FB_APP_SECRET:
        raise HTTPException(status_code=400, detail="FB_APP_ID و FB_APP_SECRET مطلوبين في .env")

    url = (
        f"https://graph.facebook.com/{settings.FB_API_VERSION}/oauth/access_token"
        f"?grant_type=fb_exchange_token"
        f"&client_id={settings.FB_APP_ID}"
        f"&client_secret={settings.FB_APP_SECRET}"
        f"&fb_exchange_token={current_token}"
    )
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        if response.is_error:
            detail = response.json().get("error", {}).get("message", "فشل التبديل")
            raise HTTPException(status_code=400, detail=detail)

    data = response.json()
    new_token = data.get("access_token", "")
    expires_in = data.get("expires_in", 0)
    days = expires_in // 86400

    settings.FB_PAGE_ACCESS_TOKEN = new_token
    settings.FACEBOOK_PAGE_ACCESS_TOKEN = ""
    facebook_send.access_token = new_token
    facebook_send.token_status = "valid"

    html = f"""<h2 class="mb-20">✅ تم تجديد التوكن</h2>
<div class="card">
    <p><strong>التوكن الجديد:</strong></p>
    <pre style="background:#f5f5f5;padding:16px;border-radius:8px;margin:16px 0;direction:ltr;text-align:left;word-break:break-all">{new_token}</pre>
    <p><strong>مدة الصلاحية:</strong> {days} يوم</p>
    <p style="color:#c62828;margin-top:12px">⚠️ انسخ التوكن وحطه في <code>.env</code> باش ما يضيعش عند إعادة التشغيل</p>
    <a href="/admin/token" class="btn mt-20">🔙 رجع لصفحة التوكن</a>
</div>"""
    return HTMLResponse(content=render_page("✅ تم التجديد", html, "token"))


MANUAL_CONNECT_PAGE = """<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - MARIA</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Segoe UI',Tahoma,sans-serif;background:#f5f5f5;direction:rtl}}
.container{{max-width:600px;margin:40px auto;padding:20px}}
h2{{margin-bottom:20px}}.card{{background:white;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,.1);margin-bottom:20px}}
.form-group{{margin-bottom:16px}}
label{{display:block;margin-bottom:6px;font-weight:600;font-size:14px}}
input[type=text],input[type=password]{{width:100%;padding:12px;border:2px solid #ddd;border-radius:8px;font-size:15px;font-family:monospace}}
input:focus{{border-color:#1a237e;outline:none}}
.btn{{display:inline-block;padding:12px 24px;border:none;border-radius:8px;font-size:15px;cursor:pointer;text-decoration:none}}
.btn-primary{{background:#1a237e;color:white}}.btn-primary:hover{{background:#3949ab}}
.btn-secondary{{background:#e0e0e0;color:#333}}.btn-secondary:hover{{background:#bdbdbd}}
.text-muted{{color:#666;font-size:13px;margin-top:4px}}
.alert{{padding:12px;border-radius:8px;margin-bottom:16px}}
.alert-success{{background:#e8f5e9;color:#2e7d32}}
.alert-error{{background:#ffebee;color:#c62828}}
code{{background:#f5f5f5;padding:2px 6px;border-radius:4px;font-size:13px}}
</style></head><body>
<div class="container">
<h2>{title}</h2>
{content}
</div></body></html>"""


@router.get("/facebook/manual-connect", response_class=HTMLResponse)
async def facebook_manual_connect_page(request: Request):
    verify_admin_auth(request)
    content = """<div class="alert alert-success">
    <strong>System User Token</strong><br>
    هذه الطريقة تستعمل Business Manager → System User باش تجيب توكن ما ينتهيش أبداً.
</div>
<div class="card">
    <h3 class="mb-20">إضافة توكن يدوي</h3>
    <form method="post" action="/admin/facebook/manual-connect">
        <div class="form-group">
            <label>Page ID</label>
            <input type="text" name="page_id" required placeholder="مثال: 123456789012345" dir="ltr">
        </div>
        <div class="form-group">
            <label>Page Name</label>
            <input type="text" name="page_name" required placeholder="اسم الصفحة">
        </div>
        <div class="form-group">
            <label>Page Access Token</label>
            <input type="password" name="page_access_token" required placeholder="EAA..." dir="ltr">
            <div class="text-muted">التوكن لي جبتو من Business Manager → System User</div>
        </div>
        <div class="form-group">
            <label>اسم المتجر (اختياري)</label>
            <input type="text" name="store_name" placeholder="مثال: متجري">
        </div>
        <button type="submit" class="btn btn-primary">💾 حفظ الصفحة</button>
        <a href="/admin/facebook/connections" class="btn btn-secondary">رجـع</a>
    </form>
</div>
<details style="margin-top:20px">
<summary style="cursor:pointer;color:#1a237e;font-weight:600">كيفية جلب التوكن من Business Manager</summary>
<div class="card" style="margin-top:10px">
<ol style="padding-right:20px;line-height:2">
<li>روح لـ <a href="https://business.facebook.com/settings/system-users" target="_blank">Business Settings → System Users</a></li>
<li>ضغط <strong>Add</strong> ← <strong>System User</strong></li>
<li>سميه (مثال: <code>Maria AI Bot</code>) واعطيه صلاحية <strong>Admin</strong></li>
<li>من نفس الصفحة، ضغط <strong>Assign Assets</strong> ← <strong>Pages</strong></li>
<li>اختار صفحتك واعطيه صلاحية <strong>Manage Page</strong> + <strong>Send Messages</strong></li>
<li>ضغط <strong>Generate Token</strong> واختار الصفحة</li>
<li>انسخ التوكن (يبدأ بـ <code>EAA...</code>) وحطه هنا</li>
</ol>
</div>
</details>"""
    return HTMLResponse(content=MANUAL_CONNECT_PAGE.format(title="ربط يدوي", content=content))


@router.post("/facebook/manual-connect", response_class=HTMLResponse)
async def facebook_manual_connect_submit(
    request: Request,
    page_id: str = Form(...),
    page_name: str = Form(...),
    page_access_token: str = Form(...),
    store_name: Optional[str] = Form(None),
):
    verify_admin_auth(request)
    from app.services.facebook_oauth import upsert_facebook_connection

    try:
        conn = await upsert_facebook_connection(
            page_id=page_id,
            page_name=page_name,
            page_access_token=page_access_token,
            store_name=store_name or page_name,
        )
        await send_telegram_notification(
            f"تم ربط الصفحة {page_name} يدويا!"
            f"ID: {page_id}"
        )
        content = f"""<div class="alert alert-success">
    <strong>تم ربط الصفحة بنجاح!</strong><br>
    <strong>{page_name}</strong> (ID: {page_id})<br>
    التوكن مشفر ومخزن في قاعدة البيانات.
</div>
<div style="text-align:center;margin-top:20px">
    <a href="/admin/facebook/connections" class="btn btn-primary">إدارة الصفحات المتصلة</a>
</div>"""
        return HTMLResponse(content=MANUAL_CONNECT_PAGE.format(title="تم الربط", content=content))

    except Exception as e:
        logger.error(f"Manual connect failed: {e}")
        content = f"""<div class="alert alert-error">
    <strong>فشل الربط</strong><br>
    {html.escape(str(e))}
</div>
<a href="/admin/facebook/manual-connect" class="btn btn-secondary">حاول مرة أخرى</a>"""
        return HTMLResponse(content=MANUAL_CONNECT_PAGE.format(title="فشل الربط", content=content))
