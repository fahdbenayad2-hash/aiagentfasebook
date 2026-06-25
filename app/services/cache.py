import time
from typing import Any, Optional, Callable
from threading import Lock


class TTLCache:
    """Thread-safe TTL cache. Stores a single value with expiry."""

    def __init__(self, ttl: float = 60.0):
        self._data: Any = None
        self._timestamp: float = 0.0
        self._ttl = ttl
        self._lock = Lock()

    def get(self) -> Any:
        with self._lock:
            if self._data is not None and (time.time() - self._timestamp) < self._ttl:
                return self._data
            return None

    def set(self, data: Any):
        with self._lock:
            self._data = data
            self._timestamp = time.time()

    def invalidate(self):
        with self._lock:
            self._data = None
            self._timestamp = 0.0

    def get_or_set(self, factory: Callable[[], Any]) -> Any:
        cached = self.get()
        if cached is not None:
            return cached
        data = factory()
        self.set(data)
        return data
