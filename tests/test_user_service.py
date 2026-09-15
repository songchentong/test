"""用户服务测试"""
import pytest
from src.user_service import UserService, UserNotFoundError, UserValidationError


class TestUserService:
    """用户服务测试"""
    
    def test_create_user(self, user_service):
        user = user_service.create_user("Alice", 25)
        assert user.name == "Alice"
        assert user.age == 25
        assert user.id == 1
    
    def test_create_user_empty_name(self, user_service):
        with pytest.raises(UserValidationError, match="用户名不能为空"):
            user_service.create_user("", 25)
    
    def test_create_user_invalid_age(self, user_service):
        with pytest.raises(UserValidationError, match="年龄不合法"):
            user_service.create_user("Alice", -1)
        
        with pytest.raises(UserValidationError, match="年龄不合法"):
            user_service.create_user("Alice", 200)
    
    def test_get_user(self, user_service, sample_user):
        user = user_service.get_user(sample_user.id)
        assert user.name == "Alice"
    
    def test_get_user_not_found(self, user_service):
        with pytest.raises(UserNotFoundError, match="用户不存在"):
            user_service.get_user(999)
    
    def test_get_all_users(self, user_service, sample_users):
        users = user_service.get_all_users()
        assert len(users) == 3
    
    def test_update_user(self, user_service, sample_user):
        user = user_service.update_user(sample_user.id, name="Alice2", age=26)
        assert user.name == "Alice2"
        assert user.age == 26
    
    def test_delete_user(self, user_service, sample_user):
        assert user_service.delete_user(sample_user.id) is True
        with pytest.raises(UserNotFoundError):
            user_service.get_user(sample_user.id)
    
    def test_search_by_name(self, user_service, sample_users):
        results = user_service.search_by_name("Alice")
        assert len(results) == 1
        assert results[0].name == "Alice"
    
    @pytest.mark.parametrize("name,age", [
        ("Alice", 25),
        ("Bob", 30),
        ("Charlie", 35),
    ])
    def test_create_multiple_users(self, user_service, name, age):
        user = user_service.create_user(name, age)
        assert user.name == name
        assert user.age == age
