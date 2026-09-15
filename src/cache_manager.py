"""缓存管理模块"""
import logging
from typing import Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, default_ttl: int = 300):
        self.cache: dict = {}
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        if ttl is None:
            ttl = self.default_ttl
        
        expire_at = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = {
            "value": value,
            "expire_at": expire_at
        }
        return True
    
    def get(self, key: str) -> Any:
        """获取缓存"""
        if key not in self.cache:
            self.misses += 1
            return None
        
        item = self.cache[key]
        if datetime.now() > item["expire_at"]:
            # 已过期
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return item["value"]
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
    
    def get_stats(self) -> dict:
        """获取统计"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "size": len(self.cache)
        }
