import time
import pytest
from app.core.cache import HighThroughputCache, cache_manager


def test_high_throughput_cache_set_and_get():
    cache = HighThroughputCache(default_ttl_sec=5, max_l1_entries=100)
    data = {"company": "Google", "role": "Senior Staff Engineer"}
    
    etag = cache.set_l1("test_key_1", data, ttl_sec=5)
    assert etag.startswith('"') and etag.endswith('"')

    cached = cache.get_l1("test_key_1")
    assert cached is not None
    cached_data, cached_etag = cached
    assert cached_data == data
    assert cached_etag == etag


def test_high_throughput_cache_ttl_expiration():
    cache = HighThroughputCache(default_ttl_sec=1, max_l1_entries=100)
    cache.set_l1("expiring_key", {"status": "ok"}, ttl_sec=0.1)
    
    time.sleep(0.15)
    result = cache.get_l1("expiring_key")
    assert result is None


def test_high_throughput_cache_lru_capacity_eviction():
    cache = HighThroughputCache(default_ttl_sec=10, max_l1_entries=2)
    cache.set_l1("k1", {"val": 1})
    cache.set_l1("k2", {"val": 2})
    cache.set_l1("k3", {"val": 3})  # Should evict k1

    assert cache.get_l1("k1") is None
    assert cache.get_l1("k2") is not None
    assert cache.get_l1("k3") is not None


def test_high_throughput_cache_invalidation():
    cache = HighThroughputCache(default_ttl_sec=10, max_l1_entries=100)
    cache.set_l1("prefix_1", {"v": 1})
    cache.set_l1("prefix_2", {"v": 2})
    cache.set_l1("other_1", {"v": 3})

    # Invalidate matching prefix
    cache.invalidate(prefix="prefix_")
    assert cache.get_l1("prefix_1") is None
    assert cache.get_l1("prefix_2") is None
    assert cache.get_l1("other_1") is not None

    # Invalidate all
    cache.invalidate()
    assert cache.get_l1("other_1") is None
