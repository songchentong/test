"""订单服务测试"""
import uuid

import pytest
from src.order_service import OrderStatus


def _unique_user_id():
    return uuid.uuid4().int


class TestOrderService:
    """订单服务测试"""
    
    def test_create_order(self, order_service):
        user_id = _unique_user_id()
        order = order_service.create_order(user_id=user_id, amount=100)
        assert order.user_id == user_id
        assert order.amount == 100
        assert order.status == OrderStatus.PENDING
    
    def test_get_order(self, order_service):
        user_id = _unique_user_id()
        order = order_service.create_order(user_id, 100)
        result = order_service.get_order(order.id)
        assert result.id == order.id
    
    def test_get_order_not_found(self, order_service):
        with pytest.raises(ValueError, match="订单不存在"):
            order_service.get_order(999)
    
    def test_pay_order(self, order_service):
        user_id = _unique_user_id()
        order = order_service.create_order(user_id, 100)
        paid = order_service.pay_order(order.id)
        assert paid.status == OrderStatus.PAID
    
    def test_pay_order_wrong_status(self, order_service):
        user_id = _unique_user_id()
        order = order_service.create_order(user_id, 100)
        order_service.pay_order(order.id)
        with pytest.raises(ValueError, match="订单状态错误"):
            order_service.pay_order(order.id)
    
    def test_cancel_order(self, order_service):
        user_id = _unique_user_id()
        order = order_service.create_order(user_id, 100)
        cancelled = order_service.cancel_order(order.id)
        assert cancelled.status == OrderStatus.CANCELLED
    
    def test_add_item(self, order_service):
        user_id = _unique_user_id()
        order = order_service.create_order(user_id)
        order.add_item("商品A", 10, 2)
        order.add_item("商品B", 20, 1)
        assert order.amount == 40
        assert len(order.items) == 2
    
    def test_get_user_orders(self, order_service):
        user_id = _unique_user_id()
        other_user_id = _unique_user_id()
        order_service.create_order(user_id, 100)
        order_service.create_order(user_id, 200)
        order_service.create_order(other_user_id, 300)
        orders = order_service.get_user_orders(user_id)
        assert len(orders) == 2
        assert all(order.user_id == user_id for order in orders)
    
    def test_calculate_total(self, order_service):
        user_id = _unique_user_id()
        order_service.create_order(user_id, 100)
        order_service.create_order(user_id, 200)
        total = order_service.calculate_total(user_id)
        assert total == 300
    
    def test_calculate_total_excludes_cancelled(self, order_service):
        user_id = _unique_user_id()
        order_service.create_order(user_id, 100)
        order2 = order_service.create_order(user_id, 200)
        order_service.cancel_order(order2.id)
        total = order_service.calculate_total(user_id)
        assert total == 100
