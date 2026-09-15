"""订单服务模块"""
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OrderStatus:
    """订单状态"""
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order:
    """订单类"""
    
    def __init__(self, order_id: int, user_id: int, amount: float):
        self.id = order_id
        self.user_id = user_id
        self.amount = amount
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()
        self.items: List[Dict] = []
    
    def add_item(self, name: str, price: float, quantity: int = 1):
        """添加商品"""
        self.items.append({
            "name": name,
            "price": price,
            "quantity": quantity
        })
        self.amount += price * quantity
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "items": self.items
        }


class OrderService:
    """订单服务"""
    
    def __init__(self):
        self.orders: Dict[int, Order] = {}
        self._next_id = 1
    
    def create_order(self, user_id: int, amount: float = 0) -> Order:
        """创建订单"""
        order = Order(self._next_id, user_id, amount)
        self.orders[order.id] = order
        self._next_id += 1
        return order
    
    def get_order(self, order_id: int) -> Order:
        """获取订单"""
        if order_id not in self.orders:
            raise ValueError(f"订单不存在: {order_id}")
        return self.orders[order_id]
    
    def pay_order(self, order_id: int) -> Order:
        """支付订单"""
        order = self.get_order(order_id)
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"订单状态错误: {order.status}")
        order.status = OrderStatus.PAID
        return order
    
    def cancel_order(self, order_id: int) -> Order:
        """取消订单"""
        order = self.get_order(order_id)
        if order.status in [OrderStatus.SHIPPED, OrderStatus.COMPLETED]:
            raise ValueError("已发货订单不能取消")
        order.status = OrderStatus.CANCELLED
        return order
    
    def get_user_orders(self, user_id: int) -> List[Order]:
        """获取用户订单"""
        return [o for o in self.orders.values() if o.user_id == user_id]
    
    def calculate_total(self, user_id: int) -> float:
        """计算用户订单总额"""
        orders = self.get_user_orders(user_id)
        return sum(o.amount for o in orders if o.status != OrderStatus.CANCELLED)
