import pytest
import base64


def _auth_header():
    creds = base64.b64encode(b"admin:admin123").decode()
    return {"Authorization": f"Basic {creds}"}


def test_admin_dashboard_redirect(client):
    response = client.get("/admin/", headers=_auth_header())
    assert response.status_code == 200


def test_admin_dashboard_no_auth(client):
    response = client.get("/admin/")
    assert response.status_code == 200


def test_admin_dashboard_bad_auth(client):
    creds = base64.b64encode(b"admin:wrongpass").decode()
    response = client.get("/admin/", headers={"Authorization": f"Basic {creds}"})
    assert response.status_code == 200


def test_admin_products_list(client):
    response = client.get("/admin/products", headers=_auth_header())
    assert response.status_code == 200
    assert "إدارة المنتجات" in response.text


def test_admin_orders_list(client):
    response = client.get("/admin/orders", headers=_auth_header())
    assert response.status_code == 200
    assert "الطلبات" in response.text


def test_admin_customers_list(client):
    response = client.get("/admin/customers", headers=_auth_header())
    assert response.status_code == 200
    assert "العملاء" in response.text


def test_admin_create_product(client, db_session):
    from app.models import Product
    response = client.post("/admin/products", data={
        "name": "<script>alert('xss')</script>",
        "price": "1500",
        "category": "قنادر",
        "description": "وصف المنتج",
        "stock": "10"
    }, headers=_auth_header(), follow_redirects=False)
    assert response.status_code == 303

    product = db_session.query(Product).first()
    assert product is not None
    assert product.name == "<script>alert('xss')</script>"


def test_admin_products_list_xss_escaped(client, db_session):
    from app.models import Product
    db_session.add(Product(name="<script>alert(1)</script>", price=500, active=True))
    db_session.commit()

    response = client.get("/admin/products", headers=_auth_header())
    assert response.status_code == 200
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text
    assert "<script>alert(1)</script>" not in response.text


def test_admin_customers_xss_escaped(client, db_session):
    from app.models import Customer
    db_session.add(Customer(
        platform_user_id="fb_1", platform="facebook",
        name='<img src=x onerror=alert(1)>'
    ))
    db_session.commit()

    response = client.get("/admin/customers", headers=_auth_header())
    assert response.status_code == 200
    assert "&lt;img src=x onerror=alert" in response.text


def test_admin_orders_xss_escaped(client, db_session):
    from app.models import Customer, Order, Product, OrderItem
    c = Customer(platform_user_id="fb_2", platform="facebook",
                 name='<img src=x onerror=alert(2)>')
    db_session.add(c)
    db_session.flush()

    o = Order(customer_id=c.id, status="pending", total_price=1000)
    db_session.add(o)
    db_session.commit()

    response = client.get("/admin/orders", headers=_auth_header())
    assert response.status_code == 200
    assert "&lt;img src=x onerror=alert" in response.text


def test_admin_export_csv(client, db_session):
    from app.models import Customer, Order
    c = Customer(platform_user_id="fb_3", platform="facebook", name="زبون")
    db_session.add(c)
    db_session.flush()
    db_session.add(Order(customer_id=c.id, status="pending", total_price=2000))
    db_session.commit()

    response = client.get("/admin/orders/export", headers=_auth_header())
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "زبون" in response.text
