import time
import asyncio
import threading

import pytest

from http_service import bulkhead, async_bulkhead, Bulkhead, AsyncBulkhead, BulkheadConfig, BulkheadRejectedError


def test_bulkhead_decorator_limits_concurrency():
    max_concurrent = 2
    active = 0
    peak = 0
    lock = threading.Lock()

    @bulkhead(max_concurrent=max_concurrent, acquire_timeout=0.01)
    def work(delay):
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        try:
            time.sleep(delay)
        finally:
            with lock:
                active -= 1

    # Launch 2 calls; with max 2 allowed concurrently
    threads = [threading.Thread(target=work, args=(0.2,)) for _ in range(2)]
    for t in threads:
        t.start()

    # Give threads time to acquire the semaphore
    time.sleep(0.02)

    # This third attempt should be rejected since capacity is full and timeout is tiny
    with pytest.raises(BulkheadRejectedError):
        work(0.01)

    for t in threads:
        t.join()

    assert peak <= max_concurrent


@pytest.mark.asyncio
async def test_async_bulkhead_decorator_limits_concurrency():
    max_concurrent = 2
    active = 0
    peak = 0
    lock = asyncio.Lock()

    @async_bulkhead(max_concurrent=max_concurrent, acquire_timeout=0.01)
    async def awork(delay):
        nonlocal active, peak
        async with lock:
            active += 1
            peak = max(peak, active)
        try:
            await asyncio.sleep(delay)
        finally:
            async with lock:
                active -= 1

    tasks = [asyncio.create_task(awork(0.2)) for _ in range(2)]
    # Let tasks start and acquire
    await asyncio.sleep(0.02)

    with pytest.raises(BulkheadRejectedError):
        await awork(0.01)

    await asyncio.gather(*tasks)

    assert peak <= max_concurrent


def test_bulkhead_context_manager():
    cfg = BulkheadConfig(enabled=True, max_concurrent=1, acquire_timeout=0.0)
    bh = Bulkhead(cfg)
    with bh.slot():
        with pytest.raises(BulkheadRejectedError):
            with bh.slot():
                pass


@pytest.mark.asyncio
async def test_async_bulkhead_context_manager():
    cfg = BulkheadConfig(enabled=True, max_concurrent=1, acquire_timeout=0.01)
    bh = AsyncBulkhead(cfg)
    async with bh.slot():
        with pytest.raises(BulkheadRejectedError):
            await bh.slot().__aenter__()

