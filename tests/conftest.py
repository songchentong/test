"""测试配置"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.calculator import Calculator, ScientificCalculator
from src.user_service import UserService
from src.order_service import OrderService
from src.cache_manager import CacheManager
from src.utils.validators import Validator
from src.utils.formatters import Formatter


@pytest.fixture
def calculator():
    """基础计算器"""
    return Calculator()


@pytest.fixture
def sci_calculator():
    """科学计算器"""
    return ScientificCalculator()


@pytest.fixture
def user_service():
    """用户服务"""
    return UserService()


@pytest.fixture(scope="class")
def order_service():
    """订单服务"""
    return OrderService()


@pytest.fixture(scope="session")
def cache_manager():
    """缓存管理器"""
    return CacheManager()


@pytest.fixture(scope="function")
def sample_user(user_service):
    """示例用户"""
    return user_service.create_user("Alice", 25, "alice@example.com")


@pytest.fixture
def sample_users(user_service):
    """多个示例用户"""
    return [
        user_service.create_user("Alice", 25),
        user_service.create_user("Bob", 30),
        user_service.create_user("Charlie", 35),
    ]


@pytest.fixture(autouse=True)
def setup():
    """测试设置"""
    print("开始测试------")
    yield
    print("结束测试------")