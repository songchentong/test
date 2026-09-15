"""订单服务测试"""
import pytest
from src.order_service import OrderService, OrderStatus


class TestOrderService:
    """订单服务测试"""
    
    def test_create_order(self, order_service):
        order = order_service.create_order(user_id=1, amount=100)
        assert order.user_id == 1
        assert order.amount == 100
        assert order.status == OrderStatus.PENDING
    
    def test_get_order(self, order_service):
        order = order_service.create_order(1, 100)
        result = order_service.get_order(order.id)
        assert result.id == order.id
    
    def test_get_order_not_found(self, order_service):
        with pytest.raises(ValueError, match="订单不存在"):
            order_service.get_order(999)
    
    def test_pay_order(self, order_service):
        order = order_service.create_order(1, 100)
        paid = order_service.pay_order(order.id)
        assert paid.status == OrderStatus.PAID
    
    def test_pay_order_wrong_status(self, order_service):
        order = order_service.create_order(1, 100)
        order_service.pay_order(order.id)
        with pytest.raises(ValueError, match="订单状态错误"):
            order_service.pay_order(order.id)
    
    def test_cancel_order(self, order_service):
        order = order_service.create_order(1, 100)
        cancelled = order_service.cancel_order(order.id)
        assert cancelled.status == OrderStatus.CANCELLED
    
    def test_add_item(self, order_service):
        order = order_service.create_order(1)
        order.add_item("商品A", 10, 2)
        order.add_item("商品B", 20, 1)
        assert order.amount == 40
        assert len(order.items) == 2
    
    def test_get_user_orders(self, order_service):
        order_service.create_order(1, 100)
        order_service.create_order(1, 200)
        order_service.create_order(2, 300)
        orders = order_service.get_user_orders(1)
        assert len(orders) == 2
    
    def test_calculate_total(self, order_service):
        order_service.create_order(1, 100)
        order_service.create_order(1, 200)
        total = order_service.calculate_total(1)
        assert total == 300
    
    def test_calculate_total_excludes_cancelled(self, order_service):
        order1 = order_service.create_order(1, 100)
        order2 = order_service.create_order(1, 200)
        order_service.cancel_order(order2.id)
        total = order_service.calculate_total(1)
        assert total == 100
