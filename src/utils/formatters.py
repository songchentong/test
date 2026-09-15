"""格式化工具"""
from datetime import datetime
from typing import Dict, List


class Formatter:
    """格式化器"""
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """格式化金额"""
        return f"¥{amount:.2f}"
    
    @staticmethod
    def format_date(dt: datetime, fmt: str = "%Y-%m-%d") -> str:
        """格式化日期"""
        return dt.strftime(fmt)
    
    @staticmethod
    def format_user(user_dict: Dict) -> str:
        """格式化用户信息"""
        return f"{user_dict.get('name', '未知')} ({user_dict.get('age', '?')}岁)"
    
    @staticmethod
    def format_list(items: List, separator: str = ", ") -> str:
        """格式化列表"""
        return separator.join(str(item) for item in items)
    
    @staticmethod
    def truncate(text: str, max_length: int = 50, suffix: str = "...") -> str:
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
