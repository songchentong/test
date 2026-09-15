"""验证工具"""
import re
from typing import Any


class Validator:
    """验证器"""
    
    @staticmethod
    def is_email(email: str) -> bool:
        """验证邮箱"""
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_phone(phone: str) -> bool:
        """验证手机号"""
        pattern = r"^1[3-9]\d{9}$"
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def is_positive(value: Any) -> bool:
        """验证正数"""
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_in_range(value: float, min_val: float, max_val: float) -> bool:
        """验证范围"""
        return min_val <= value <= max_val
    
    @staticmethod
    def is_valid_age(age: int) -> bool:
        """验证年龄"""
        return isinstance(age, int) and 0 <= age <= 150
