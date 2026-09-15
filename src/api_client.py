"""API 客户端模块"""
import logging
import requests
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class APIError(Exception):
    """API 异常"""
    pass


class APIClient:
    """API 客户端"""
    
    def __init__(self, base_url: str, api_key: str = "", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """GET 请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"GET 请求失败: {e}")
    
    def post(self, endpoint: str, data: Dict) -> Dict:
        """POST 请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"POST 请求失败: {e}")
    
    def put(self, endpoint: str, data: Dict) -> Dict:
        """PUT 请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.put(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"PUT 请求失败: {e}")
    
    def delete(self, endpoint: str) -> Dict:
        """DELETE 请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.delete(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"DELETE 请求失败: {e}")
    
    def close(self):
        """关闭会话"""
        self.session.close()
