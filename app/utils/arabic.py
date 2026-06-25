from __future__ import annotations
import re
import unicodedata
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Product


def normalize_arabic(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
    text = re.sub(r"[إأآٱ]", "ا", text)
    text = text.replace("ة", "ه").replace("ى", "ي")
    text = re.sub(r"[ۿﱞ]", "", text)
    text = text.strip().lower()
    return text


def normalize_list(items: list[str]) -> list[str]:
    return [normalize_arabic(item) for item in items]


def find_product(query: str, products: list) -> object | None:
    query_norm = normalize_arabic(query.strip())
    for product in products:
        name_norm = normalize_arabic(product.name)
        if query_norm == name_norm:
            return product
        if query_norm in name_norm or name_norm in query_norm:
            return product
    query_words = set(query_norm.split())
    for product in products:
        name_words = set(normalize_arabic(product.name).split())
        if query_words & name_words:
            return product
    return None
