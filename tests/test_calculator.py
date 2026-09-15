"""计算器测试"""
import pytest
from src.calculator import Calculator, ScientificCalculator, CalculatorFactory


class TestCalculator:
    """基础计算器测试"""
    
    def test_add(self, calculator):
        assert calculator.add(1, 2) == 3
        assert calculator.add(-1, 1) == 0
        assert calculator.add(1.5, 2.5) == 4.0
    
    def test_subtract(self, calculator):
        assert calculator.subtract(5, 3) == 2
        assert calculator.subtract(1, 1) == 0
    
    def test_multiply(self, calculator):
        assert calculator.multiply(2, 3) == 6
        assert calculator.multiply(-2, 3) == -6
        assert calculator.multiply(0, 5) == 0
    
    def test_divide(self, calculator):
        assert calculator.divide(6, 2) == 3
        assert calculator.divide(5, 2) == 2.5
    
    def test_divide_by_zero(self, calculator):
        with pytest.raises(ValueError, match="除数不能为0"):
            calculator.divide(1, 0)
    
    def test_power(self, calculator):
        assert calculator.power(2, 3) == 8
        assert calculator.power(5, 0) == 1
    
    def test_history(self, calculator):
        calculator.add(1, 2)
        calculator.subtract(5, 3)
        history = calculator.get_history()
        assert len(history) == 2
        assert "1 + 2 = 3" in history
    
    def test_clear_history(self, calculator):
        calculator.add(1, 2)
        calculator.clear_history()
        assert len(calculator.get_history()) == 0


class TestScientificCalculator:
    """科学计算器测试"""
    
    def test_sqrt(self, sci_calculator):
        assert sci_calculator.sqrt(4) == 2
        assert sci_calculator.sqrt(9) == 3
    
    def test_sqrt_negative(self, sci_calculator):
        with pytest.raises(ValueError, match="不能对负数开平方"):
            sci_calculator.sqrt(-1)
    
    def test_factorial(self, sci_calculator):
        assert sci_calculator.factorial(0) == 1
        assert sci_calculator.factorial(5) == 120
    
    def test_factorial_negative(self, sci_calculator):
        with pytest.raises(ValueError, match="阶乘不能为负数"):
            sci_calculator.factorial(-1)
    
    def test_inheritance(self, sci_calculator):
        """测试继承：科学计算器也能用基础方法"""
        assert sci_calculator.add(1, 2) == 3


class TestCalculatorFactory:
    """计算器工厂测试"""
    
    def test_create_basic(self):
        calc = CalculatorFactory.create("basic")
        assert isinstance(calc, Calculator)
    
    def test_create_scientific(self):
        calc = CalculatorFactory.create("scientific")
        assert isinstance(calc, ScientificCalculator)
    
    def test_create_unknown(self):
        with pytest.raises(ValueError, match="未知的计算器类型"):
            CalculatorFactory.create("unknown")
