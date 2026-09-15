"""支付服务模块"""
import logging
from typing import Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    """支付状态"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentError(Exception):
    """支付异常"""
    pass


class PaymentGateway:
    """支付网关（外部接口）"""
    
    def charge(self, amount: float, card_number: str) -> Dict:
        """扣款（模拟外部调用）"""
        # 实际会调用银行接口
        raise NotImplementedError("需要实现")


class PaymentService:
    """支付服务"""
    
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
        self.payments: Dict[str, Dict] = {}
    
    def pay(self, order_id: str, amount: float, card_number: str) -> Dict:
        """支付"""
        if amount <= 0:
            raise PaymentError("金额必须大于0")
        
        if not card_number or len(card_number) < 16:
            raise PaymentError("卡号不合法")
        
        try:
            result = self.gateway.charge(amount, card_number)
        except Exception as e:
            logger.error(f"支付失败: {e}")
            raise PaymentError(f"支付失败: {e}")
        
        payment = {
            "order_id": order_id,
            "amount": amount,
            "status": PaymentStatus.SUCCESS.value,
            "transaction_id": result.get("transaction_id")
        }
        self.payments[order_id] = payment
        return payment
    
    def refund(self, order_id: str) -> Dict:
        """退款"""
        if order_id not in self.payments:
            raise PaymentError(f"支付记录不存在: {order_id}")
        
        payment = self.payments[order_id]
        if payment["status"] != PaymentStatus.SUCCESS.value:
            raise PaymentError("只有成功的支付才能退款")
        
        payment["status"] = PaymentStatus.REFUNDED.value
        return payment
    
    def get_payment(self, order_id: str) -> Optional[Dict]:
        """查询支付"""
        return self.payments.get(order_id)
