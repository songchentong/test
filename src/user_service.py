"""用户服务模块"""
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class UserNotFoundError(Exception):
    """用户不存在异常"""
    pass


class UserValidationError(Exception):
    """用户验证异常"""
    pass


class User:
    """用户类"""
    
    def __init__(self, user_id: int, name: str, age: int, email: str = ""):
        self.id = user_id
        self.name = name
        self.age = age
        self.email = email
        self.active = True
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "active": self.active
        }
    
    def __repr__(self):
        return f"User(id={self.id}, name={self.name})"


class UserService:
    """用户服务"""
    
    def __init__(self, db=None):
        self.db = db
        self.users: Dict[int, User] = {}
        self._next_id = 1
    
    def create_user(self, name: str, age: int, email: str = "") -> User:
        """创建用户"""
        if not name:
            raise UserValidationError("用户名不能为空")
        if age < 0 or age > 150:
            raise UserValidationError("年龄不合法")
        
        user = User(self._next_id, name, age, email)
        self.users[user.id] = user
        self._next_id += 1
        logger.info(f"创建用户: {user}")
        return user
    
    def get_user(self, user_id: int) -> User:
        """获取用户"""
        if user_id not in self.users:
            raise UserNotFoundError(f"用户不存在: {user_id}")
        return self.users[user_id]
    
    def get_all_users(self) -> List[User]:
        """获取所有用户"""
        return list(self.users.values())
    
    def update_user(self, user_id: int, **kwargs) -> User:
        """更新用户"""
        user = self.get_user(user_id)
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        if user_id not in self.users:
            raise UserNotFoundError(f"用户不存在: {user_id}")
        del self.users[user_id]
        return True
    
    def search_by_name(self, keyword: str) -> List[User]:
        """按名字搜索"""
        return [u for u in self.users.values() if keyword in u.name]
