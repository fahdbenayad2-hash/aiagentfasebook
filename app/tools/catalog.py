from typing import List, Optional
from app.database import SessionLocal
from app.models import Product


class ProductResult:
    def __init__(self, name: str, price: int, stock_status: str, description: str = ""):
        self.name = name
        self.price = price
        self.stock_status = stock_status
        self.description = description

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "price": self.price,
            "stock_status": self.stock_status,
            "description": self.description
        }


NOT_FOUND = ProductResult("NOT_FOUND", 0, "unavailable", "")


async def search_catalog(query: str, wilaya: Optional[str] = None) -> List[ProductResult]:
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.active == True).all()
        results = []
        query_lower = query.lower()
        for p in products:
            if (query_lower in p.name.lower() or
                query_lower in (p.description or "").lower() or
                query_lower in (p.category or "").lower()):
                stock = "in_stock" if p.stock > 0 else "out_of_stock" if p.stock == 0 else "low_stock"
                results.append(ProductResult(
                    name=p.name,
                    price=p.price,
                    stock_status=stock,
                    description=p.description or ""
                ))
            if len(results) >= 3:
                break
        if not results:
            return [NOT_FOUND]
        return results
    finally:
        db.close()
