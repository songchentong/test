"""支付服务测试"""
import pytest
from unittest.mock import Mock
from src.payment_service import PaymentService, PaymentGateway, PaymentError, PaymentStatus


@pytest.fixture
def mock_gateway():
    """Mock 支付网关"""
    gateway = Mock(spec=PaymentGateway)
    gateway.charge.return_value = {"transaction_id": "TXN123"}
    return gateway


@pytest.fixture
def payment_service(mock_gateway):
    """支付服务"""
    return PaymentService(mock_gateway)


class TestPaymentService:
    """支付服务测试"""
    
    def test_pay_success(self, payment_service, mock_gateway):
        result = payment_service.pay("ORDER001", 100, "1234567890123456")
        assert result["status"] == PaymentStatus.SUCCESS.value
        assert result["transaction_id"] == "TXN123"
        mock_gateway.charge.assert_called_once_with(100, "1234567890123456")
    
    def test_pay_invalid_amount(self, payment_service):
        with pytest.raises(PaymentError, match="金额必须大于0"):
            payment_service.pay("ORDER001", 0, "1234567890123456")
    
    def test_pay_invalid_card(self, payment_service):
        with pytest.raises(PaymentError, match="卡号不合法"):
            payment_service.pay("ORDER001", 100, "123")
    
    def test_pay_gateway_error(self, payment_service, mock_gateway):
        mock_gateway.charge.side_effect = Exception("网关超时")
        with pytest.raises(PaymentError, match="支付失败"):
            payment_service.pay("ORDER001", 100, "1234567890123456")
    
    def test_refund(self, payment_service):
        payment_service.pay("ORDER001", 100, "1234567890123456")
        result = payment_service.refund("ORDER001")
        assert result["status"] == PaymentStatus.REFUNDED.value
    
    def test_refund_not_found(self, payment_service):
        with pytest.raises(PaymentError, match="支付记录不存在"):
            payment_service.refund("ORDER999")
    
    def test_get_payment(self, payment_service):
        payment_service.pay("ORDER001", 100, "1234567890123456")
        payment = payment_service.get_payment("ORDER001")
        assert payment["amount"] == 100
