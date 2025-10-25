# store.py
import os
import threading
import config

class BaseStore:
    def seen(self, key: str) -> bool: ...
    def mark(self, key: str) -> None: ...

class FileStore(BaseStore):
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        self._set = set()
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    raw = f.read().strip().strip(",")
                    if raw:
                        self._set = set([s for s in raw.split(",") if s])
            except Exception:
                self._set = set()
        else:
            open(path, "a").close()

    def seen(self, key: str) -> bool:
        return key in self._set

    def mark(self, key: str) -> None:
        with self._lock:
            if key not in self._set:
                with open(self.path, "a") as f:
                    f.write(key + ",")
                self._set.add(key)

class RedisStore(BaseStore):
    def __init__(self, url: str, key: str = "processed_urls"):
        import redis
        self.r = redis.from_url(url, decode_responses=True)
        self.key = key

    def seen(self, key: str) -> bool:
        return bool(self.r.sismember(self.key, key))

    def mark(self, key: str) -> None:
        self.r.sadd(self.key, key)

def get_store() -> BaseStore:
    if config.REDIS_URL:
        return RedisStore(config.REDIS_URL)
    return FileStore(config.DATABASE_FILE)
