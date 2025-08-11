"""
Bulkhead pattern for isolating resource usage by limiting concurrent access.

Provides:
- Bulkhead: sync bulkhead using threading.Semaphore
- AsyncBulkhead: async bulkhead using asyncio.Semaphore
- bulkhead decorator for sync functions
- async_bulkhead decorator for async functions

If the bulkhead is full and cannot acquire within the configured timeout,
BulkheadRejectedError is raised.
"""

from __future__ import annotations

import asyncio
import threading
from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Optional, Any


class BulkheadRejectedError(Exception):
    """Raised when bulkhead cannot acquire a slot within timeout."""


@dataclass
class BulkheadConfig:
    enabled: bool = False
    max_concurrent: Optional[int] = None
    acquire_timeout: float = 0.0  # seconds, 0.0 = non-blocking


class Bulkhead:
    """Synchronous bulkhead using threading.Semaphore."""

    def __init__(self, config: BulkheadConfig) -> None:
        self.config = config
        self._semaphore = (
            threading.Semaphore(config.max_concurrent) if config.max_concurrent and config.max_concurrent > 0 else None
        )

    @contextmanager
    def slot(self):
        if not self.config.enabled or not self._semaphore:
            yield
            return
        acquired = self._semaphore.acquire(timeout=self.config.acquire_timeout)
        if not acquired:
            raise BulkheadRejectedError("Bulkhead capacity reached")
        try:
            yield
        finally:
            self._semaphore.release()


class AsyncBulkhead:
    """Asynchronous bulkhead using asyncio.Semaphore."""

    def __init__(self, config: BulkheadConfig) -> None:
        self.config = config
        self._semaphore = (
            asyncio.Semaphore(config.max_concurrent) if config.max_concurrent and config.max_concurrent > 0 else None
        )

    @asynccontextmanager
    async def slot(self):
        if not self.config.enabled or not self._semaphore:
            yield
            return
        # asyncio.Semaphore does not support timeout directly; emulate if needed
        if self.config.acquire_timeout and self.config.acquire_timeout > 0:
            try:
                await asyncio.wait_for(self._semaphore.acquire(), timeout=self.config.acquire_timeout)
            except asyncio.TimeoutError as e:
                raise BulkheadRejectedError("Bulkhead capacity reached (async)") from e
        else:
            await self._semaphore.acquire()

        try:
            yield
        finally:
            self._semaphore.release()


def bulkhead(max_concurrent: Optional[int], acquire_timeout: float = 0.0):
    """Decorator to limit concurrent sync function executions."""

    config = BulkheadConfig(enabled=True, max_concurrent=max_concurrent, acquire_timeout=acquire_timeout)
    bh = Bulkhead(config)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with bh.slot():
                return func(*args, **kwargs)

        return wrapper

    return decorator


def async_bulkhead(max_concurrent: Optional[int], acquire_timeout: float = 0.0):
    """Decorator to limit concurrent async function executions."""

    config = BulkheadConfig(enabled=True, max_concurrent=max_concurrent, acquire_timeout=acquire_timeout)
    bh = AsyncBulkhead(config)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with bh.slot():
                return await func(*args, **kwargs)

        return wrapper

    return decorator


