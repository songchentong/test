"""API 客户端测试"""
import pytest
from unittest.mock import Mock, patch
from src.api_client import APIClient, APIError


class TestAPIClient:
    """API 客户端测试"""
    
    @patch("src.api_client.requests.Session")
    def test_get_success(self, mock_session):
        # 模拟响应
        mock_response = Mock()
        mock_response.json.return_value = {"id": 1, "name": "Alice"}
        mock_response.raise_for_status.return_value = None
        
        mock_session.return_value.get.return_value = mock_response
        
        client = APIClient("http://api.example.com")
        result = client.get("/users/1")
        
        assert result == {"id": 1, "name": "Alice"}
    
    @patch("src.api_client.requests.Session")
    def test_post_success(self, mock_session):
        mock_response = Mock()
        mock_response.json.return_value = {"id": 1}
        mock_response.raise_for_status.return_value = None
        
        mock_session.return_value.post.return_value = mock_response
        
        client = APIClient("http://api.example.com")
        result = client.post("/users", {"name": "Alice"})
        
        assert result == {"id": 1}
    
    @patch("src.api_client.requests.Session")
    def test_get_error(self, mock_session):
        import requests
        mock_session.return_value.get.side_effect = requests.RequestException("连接失败")
        
        client = APIClient("http://api.example.com")
        with pytest.raises(APIError, match="GET 请求失败"):
            client.get("/users/1")
