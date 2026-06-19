import secrets
import csv
import io
import base64
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Product, Order, Customer, Conversation
from app.config import get_settings
from app.services.conversation_manager import invalidate_products_cache

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
<title>{title} - متجر فهد</title>
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
<div class="sidebar"><h1>🛒 متجر فهد</h1>
<a href="/admin/" class="{s_dash}">الرئيسية</a>
<a href="/admin/products" class="{s_prod}">المنتجات</a>
<a href="/admin/orders" class="{s_ord}">الطلبات</a>
<a href="/admin/customers" class="{s_cust}">العملاء</a>
<a href="/admin/conversations" class="{s_conv}">المحادثات</a>
<a href="/admin/accounts" class="{s_acct}">الحسابات المتصلة</a>
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
    )


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    verify_admin_auth(request)

    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    total_customers = db.query(Customer).count()
    total_products = db.query(Product).filter(Product.active == True).count()

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders = db.query(Order).filter(Order.created_at >= today_start).count()

    revenue = db.query(func.coalesce(func.sum(Order.total_price), 0)).filter(
        Order.status.in_(["delivered", "shipped"])
    ).scalar()

    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
    rows = ""
    for o in recent_orders:
        cname = o.customer.name if o.customer else 'غير معروف'
        rows += f"<tr><td>#{o.id}</td><td>{cname}</td><td><span class='badge badge-{o.status}'>{o.status}</span></td><td>{o.total_price} دج</td><td>{o.created_at.strftime('%Y-%m-%d %H:%M')}</td><td><a href='/admin/orders/{o.id}' class='btn btn-sm'>عرض</a></td></tr>"

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

    content = f"""<h2 class="mb-20">لوحة التحكم</h2>
<div class="stats">
<div class="stat-card"><h3>إجمالي الطلبات</h3><div class="number">{total_orders}</div><div class="small">منذ البدء</div></div>
<div class="stat-card"><h3>طلبات معلقة</h3><div class="number">{pending_orders}</div><div class="small">بحاجة للمراجعة</div></div>
<div class="stat-card"><h3>العملاء</h3><div class="number">{total_customers}</div><div class="small">مسجلين</div></div>
<div class="stat-card"><h3>المنتجات النشطة</h3><div class="number">{total_products}</div><div class="small">متاحة للبيع</div></div>
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
        rows += f"<tr><td>{p.id}</td><td>{p.name}</td><td>{p.price} دج</td><td>{p.stock}</td>"
        rows += f"<td><span class='badge badge-{badge}'>{status}</span></td>"
        rows += f"<td class='flex'><a href='/admin/products/{p.id}' class='btn btn-sm'>تعديل</a>"
        rows += f"<form method='post' action='/admin/products/{p.id}/delete' style='display:inline'>"
        rows += f"<button type='submit' class='btn btn-sm btn-danger' onclick=\"return confirm('تأكيد الحذف؟')\">حذف</button></form></td></tr>"

    content = f"""<h2 class="mb-20">إدارة المنتجات</h2>
<div class="card"><h3 class="mb-20">إضافة منتج جديد</h3>
<form method="post" action="/admin/products">
<div class="grid-2">
<div class="form-group"><label>اسم المنتج</label><input name="name" class="form-control" required></div>
<div class="form-group"><label>السعر (دج)</label><input name="price" type="number" class="form-control" required></div>
<div class="form-group"><label>الوصف</label><input name="description" class="form-control"></div>
<div class="form-group"><label>المخزون</label><input name="stock" type="number" class="form-control" value="0"></div>
</div>
<button type="submit" class="btn mt-20">➕ إضافة منتج</button>
</form></div>
<table><thead><tr><th>ID</th><th>الاسم</th><th>السعر</th><th>المخزون</th><th>الحالة</th><th>إجراءات</th></tr></thead><tbody>{rows}</tbody></table>"""
    return HTMLResponse(content=render_page("المنتجات", content, "products"))


@router.post("/products")
async def create_product(
    request: Request, name: str = Form(...), price: int = Form(...),
    description: str = Form(""), stock: int = Form(0), db: Session = Depends(get_db)
):
    verify_admin_auth(request)
    product = Product(name=name.strip(), price=price, description=description.strip(), stock=stock)
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

    content = f"""<h2 class="mb-20">تعديل المنتج: {p.name}</h2>
<div class="card"><form method="post" action="/admin/products/{p.id}/edit">
<div class="grid-2">
<div class="form-group"><label>اسم المنتج</label><input name="name" class="form-control" value="{p.name}" required></div>
<div class="form-group"><label>السعر (دج)</label><input name="price" type="number" class="form-control" value="{p.price}" required></div>
<div class="form-group"><label>الوصف</label><textarea name="description" class="form-control">{p.description or ''}</textarea></div>
<div class="form-group"><label>المخزون</label><input name="stock" type="number" class="form-control" value="{p.stock}"></div>
<div class="form-group"><label>حالة المنتج</label>
<select name="active" class="form-control"><option value="1"{' selected' if p.active else ''}>نشط</option><option value="0"{' selected' if not p.active else ''}>معطل</option></select></div>
</div>
<button type="submit" class="btn mt-20">💾 حفظ التغييرات</button>
</form></div>"""
    return HTMLResponse(content=render_page("تعديل منتج", content, "products"))


@router.post("/products/{product_id}/edit")
async def edit_product(
    request: Request, product_id: int, name: str = Form(...),
    price: int = Form(...), description: str = Form(""),
    stock: int = Form(0), active: int = Form(1), db: Session = Depends(get_db)
):
    verify_admin_auth(request)
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    p.name = name.strip()
    p.price = price
    p.description = description.strip()
    p.stock = stock
    p.active = bool(active)
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
        cname = o.customer.name if o.customer else 'غير معروف'
        rows += f"<tr><td>#{o.id}</td><td>{cname}</td><td><span class='badge badge-{o.status}'>{o.status}</span></td>"
        rows += f"<td>{o.total_price} دج</td><td>{o.created_at.strftime('%Y-%m-%d %H:%M')}</td>"
        rows += f"<td><a href='/admin/orders/{o.id}' class='btn btn-sm'>تفاصيل</a></td></tr>"

    content = f"""<h2 class="mb-20">الطلبات</h2>
<table><thead><tr><th>رقم الطلب</th><th>العميل</th><th>الحالة</th><th>المبلغ</th><th>التاريخ</th><th></th></tr></thead><tbody>{rows}</tbody></table>"""
    return HTMLResponse(content=render_page("الطلبات", content, "orders"))


@router.get("/orders/{order_id}", response_class=HTMLResponse)
async def order_detail(request: Request, order_id: int, db: Session = Depends(get_db)):
    verify_admin_auth(request)
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")

    items_rows = ""
    for item in o.items:
        pname = item.product.name if item.product else 'غير معروف'
        items_rows += f"<tr><td>{pname}</td><td>{item.quantity}</td><td>{item.price_at_time} دج</td>"
        items_rows += f"<td>{item.price_at_time * item.quantity} دج</td></tr>"

    statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    status_opts = "".join(f"<option value='{s}'{' selected' if s == o.status else ''}>{s}</option>" for s in statuses)

    c = o.customer
    content = f"""<h2 class="mb-20">تفاصيل الطلب #{o.id}</h2>
<div class="grid-2">
<div class="card"><h3 class="mb-20">معلومات العميل</h3>
<p><strong>الاسم:</strong> {c.name if c else 'غير معروف'}</p>
<p><strong>الهاتف:</strong> {c.phone if c and c.phone else 'غير متوفر'}</p>
<p><strong>الولاية:</strong> {c.state if c and c.state else 'غير متوفر'}</p>
<p><strong>العنوان:</strong> {c.address if c and c.address else 'غير متوفر'}</p>
<p><strong>المنصة:</strong> {c.platform if c else 'غير معروف'}</p></div>
<div class="card"><h3 class="mb-20">معلومات الطلب</h3>
<p><strong>الحالة:</strong> <span class='badge badge-{o.status}'>{o.status}</span></p>
<p><strong>الإجمالي:</strong> {o.total_price} دج</p>
<p><strong>تاريخ الإنشاء:</strong> {o.created_at.strftime('%Y-%m-%d %H:%M')}</p>
<p><strong>آخر تحديث:</strong> {o.updated_at.strftime('%Y-%m-%d %H:%M')}</p>
<p><strong>ملاحظات:</strong> {o.notes or 'لا توجد'}</p></div></div>
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
        rows += f"<tr><td>{c.id}</td><td>{c.name or 'غير معروف'}</td><td>{c.phone or 'غير متوفر'}</td>"
        rows += f"<td>{c.state or 'غير متوفر'}</td><td>{c.platform}</td><td>{order_count}</td>"
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
    content = f"""<h2 class="mb-20">العميل: {c.name or 'غير معروف'}</h2>
<div class="grid-2">
<div class="card"><h3 class="mb-20">معلومات العميل</h3>
<p><strong>الاسم:</strong> {c.name or 'غير معروف'}</p>
<p><strong>الهاتف:</strong> {c.phone or 'غير متوفر'}</p>
<p><strong>الولاية:</strong> {c.state or 'غير متوفر'}</p>
<p><strong>العنوان:</strong> {c.address or 'غير متوفر'}</p>
<p><strong>المنصة:</strong> {c.platform}</p>
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
        cname = conv.customer.name if conv.customer else 'غير معروف'
        msg_count = len(conv.messages) if conv.messages else 0
        last_msg = ""
        if conv.messages and len(conv.messages) > 0:
            last_msg = conv.messages[-1].get("content", "")[:50]
        platform_icon = "📘" if conv.platform == "facebook" else "📸"
        state_class = conv.current_state.lower().replace("_", "-")
        rows += f"<tr><td>{conv.id}</td><td>{cname}</td><td>{platform_icon} {conv.platform}</td>"
        rows += f"<td><span class='badge badge-{state_class}'>{conv.current_state}</span></td>"
        rows += f"<td>{msg_count}</td><td>{last_msg}</td>"
        rows += f"<td>{conv.last_message_at.strftime('%Y-%m-%d %H:%M')}</td></tr>"

    content = f"""<h2 class="mb-20">المحادثات</h2>
<table><thead><tr><th>ID</th><th>العميل</th><th>المنصة</th><th>الحالة</th><th>الرسائل</th><th>آخر رسالة</th><th>آخر نشاط</th></tr></thead><tbody>{rows}</tbody></table>"""
    return HTMLResponse(content=render_page("المحادثات", content, "conversations"))


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


@router.get("/accounts")
async def admin_accounts(request: Request, db: Session = Depends(get_db)):
    verify_admin_auth(request)
    from app.models import PlatformAccount
    accounts = db.query(PlatformAccount).filter(PlatformAccount.active == True).all()

    rows = ""
    for acc in accounts:
        platform_icon = "📘" if acc.platform == "facebook" else "📸"
        ig_info = f"<br><small>📸 IG: {acc.ig_id}</small>" if acc.ig_id else ""
        rows += f"""<tr>
            <td>{platform_icon} {acc.page_name or acc.page_id}</td>
            <td>{acc.page_id}</td>
            <td>{acc.platform}{ig_info}</td>
            <td><span class="badge badge-{acc.active and 'confirmed' or 'cancelled'}">{acc.active and "نشط" or "غير نشط"}</span></td>
            <td>{acc.connected_at.strftime('%Y-%m-%d')}</td>
        </tr>"""

    ngrok_url = "https://vigorous-frequency-entryway.ngrok-free.dev"
    content = f"""<h2 class="mb-20">🔗 الحسابات المتصلة</h2>
<div class="card">
    <p>اربط حساب فيسبوك أو إنستغرام عبر Meta OAuth. التوكن يخزن تلقائياً ويستعمل للرد.</p>
    <a href="/auth/login" class="btn btn-success" style="margin-top:15px">🔗 ربط حساب فيسبوك/إنستغرام</a>
</div>
<h3 class="mb-20">الحسابات الحالية</h3>
<table><thead><tr><th>الصفحة</th><th>Page ID</th><th>المنصة</th><th>الحالة</th><th>تاريخ الربط</th></tr></thead><tbody>{rows or '<tr><td colspan="5" style="text-align:center;color:#999">لا توجد حسابات مرتبطة بعد</td></tr>'}</tbody></table>"""
    return HTMLResponse(content=render_page("الحسابات المتصلة", content, "accounts"))
