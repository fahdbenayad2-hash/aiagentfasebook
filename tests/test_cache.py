import time
import pytest
from app.services.cache import TTLCache


def test_cache_get_set():
    c = TTLCache(ttl=60)
    assert c.get() is None
    c.set("hello")
    assert c.get() == "hello"


def test_cache_get_or_set():
    c = TTLCache(ttl=60)
    called = 0

    def factory():
        nonlocal called
        called += 1
        return "computed"

    assert c.get_or_set(factory) == "computed"
    assert called == 1
    assert c.get_or_set(factory) == "computed"
    assert called == 1  # should not re-call factory


def test_cache_invalidate():
    c = TTLCache(ttl=60)
    c.set("data")
    assert c.get() == "data"
    c.invalidate()
    assert c.get() is None


def test_cache_expiry():
    c = TTLCache(ttl=0.1)  # 100ms TTL
    c.set("data")
    assert c.get() == "data"
    time.sleep(0.15)
    assert c.get() is None


def test_cache_ttl_zero():
    c = TTLCache(ttl=0)
    c.set("data")
    assert c.get() is None  # Expired immediately
