"""
进程内内存限流器（固定窗口计数）。

仅适用于单进程部署（本项目默认 uvicorn 单进程）；多 worker 部署时各进程独立计数，
实际放行量会放大 worker 倍数。不引入 Redis 等外部依赖。
"""
import time
import threading
from typing import Dict, Tuple

# 清理周期与过期阈值：所有窗口均不超过 1 小时，2 小时前的记录必然过期
_CLEANUP_INTERVAL_SECONDS = 300
_STALE_AFTER_SECONDS = 7200


class RateLimiter:
    def __init__(self):
        # key -> (window_start, count, window_seconds)
        self._buckets: Dict[str, Tuple[float, int, int]] = {}
        self._lock = threading.Lock()
        self._last_cleanup = time.monotonic()

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        """记录一次请求并判断是否放行（用于统计所有请求的公开接口）。"""
        now = time.monotonic()
        with self._lock:
            self._maybe_cleanup(now)
            start, count, _ = self._buckets.get(key, (now, 0, window_seconds))
            if now - start >= window_seconds:
                start, count = now, 0
            count += 1
            self._buckets[key] = (start, count, window_seconds)
            return count <= limit

    def is_blocked(self, key: str, limit: int, window_seconds: int) -> bool:
        """只读判断是否已超限（用于登录：只统计失败次数）。"""
        now = time.monotonic()
        with self._lock:
            self._maybe_cleanup(now)
            entry = self._buckets.get(key)
            if entry is None:
                return False
            start, count, _ = entry
            if now - start >= window_seconds:
                return False
            return count >= limit

    def record_failure(self, key: str, window_seconds: int) -> None:
        now = time.monotonic()
        with self._lock:
            start, count, _ = self._buckets.get(key, (now, 0, window_seconds))
            if now - start >= window_seconds:
                start, count = now, 0
            self._buckets[key] = (start, count + 1, window_seconds)

    def reset(self, key: str) -> None:
        with self._lock:
            self._buckets.pop(key, None)

    def _maybe_cleanup(self, now: float) -> None:
        if now - self._last_cleanup < _CLEANUP_INTERVAL_SECONDS:
            return
        self._last_cleanup = now
        stale = [k for k, (start, _, _) in self._buckets.items() if now - start > _STALE_AFTER_SECONDS]
        for k in stale:
            self._buckets.pop(k, None)


rate_limiter = RateLimiter()
