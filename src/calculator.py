"""计算器模块"""
from typing import Union, List
import logging

logger = logging.getLogger(__name__)


class Calculator:
    """基础计算器"""
    
    def __init__(self):
        self.history: List[str] = []
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """加法"""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        """减法"""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """乘法"""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a, b):
        """除法"""
        if b == 0:
            raise ValueError("除数不能为0")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def power(self, base, exponent):
        """幂运算"""
        result = base ** exponent
        self.history.append(f"{base} ** {exponent} = {result}")
        return result
    
    def get_history(self) -> List[str]:
        """获取历史"""
        return self.history.copy()
    
    def clear_history(self):
        """清空历史"""
        self.history.clear()


class ScientificCalculator(Calculator):
    """科学计算器（继承基础计算器）"""
    
    def sqrt(self, x):
        """平方根"""
        if x < 0:
            raise ValueError("不能对负数开平方")
        result = x ** 0.5
        self.history.append(f"sqrt({x}) = {result}")
        return result
    
    def factorial(self, n):
        """阶乘"""
        if n < 0:
            raise ValueError("阶乘不能为负数")
        if n > 100:
            raise ValueError("数字太大")
        result = 1
        for i in range(1, n + 1):
            result *= i
        self.history.append(f"{n}! = {result}")
        return result


class CalculatorFactory:
    """计算器工厂"""
    
    @staticmethod
    def create(calc_type="basic"):
        """创建计算器"""
        if calc_type == "basic":
            return Calculator()
        elif calc_type == "scientific":
            return ScientificCalculator()
        else:
            raise ValueError(f"未知的计算器类型: {calc_type}")
