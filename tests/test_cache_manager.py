"""缓存管理测试"""
import time

from src.cache_manager import CacheManager


class TestCacheManager:
    """缓存管理测试"""

    def test_set_and_get(self, cache_manager):
        cache_manager.set("key1", "value1")
        assert cache_manager.get("key1") == "value1"

    def test_get_missing(self, cache_manager):
        assert cache_manager.get("nonexistent") is None

    def test_delete(self, cache_manager):
        cache_manager.set("key1", "value1")
        assert cache_manager.delete("key1") is True
        assert cache_manager.get("key1") is None

    def test_delete_missing(self, cache_manager):
        assert cache_manager.delete("nonexistent") is False

    def test_clear(self, cache_manager):
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")
        cache_manager.clear()
        assert cache_manager.get("key1") is None
        assert cache_manager.get("key2") is None

    def test_expire(self, cache_manager):
        cache_manager.set("key1", "value1", ttl=1)
        assert cache_manager.get("key1") == "value1"
        time.sleep(1.1)
        assert cache_manager.get("key1") is None

    def test_stats(self, cache_manager):
        cache_manager.clear()
        baseline = cache_manager.get_stats()

        cache_manager.set("key1", "value1")
        cache_manager.get("key1")  # hit
        cache_manager.get("key2")  # miss

        stats = cache_manager.get_stats()
        assert stats["hits"] == baseline["hits"] + 1
        assert stats["misses"] == baseline["misses"] + 1
        assert stats["size"] == 1
