import pytest
from app.services.auth_service import AuthService


def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = AuthService.hash_password(password)

    assert hashed != password
    assert AuthService.verify_password(password, hashed) == True
    assert AuthService.verify_password("wrongpassword", hashed) == False


def test_jwt_token_creation():
    """Test JWT token creation and decoding"""
    data = {"user_id": 1, "username": "testuser", "role": "Operator"}

    token = AuthService.create_access_token(data)
    assert token is not None
    assert isinstance(token, str)

    decoded = AuthService.decode_token(token)
    assert decoded["user_id"] == 1
    assert decoded["username"] == "testuser"
    assert decoded["role"] == "Operator"


def test_role_permissions():
    """Test RBAC role hierarchy"""
    # Management can access everything
    assert AuthService.check_permission("Management", "Operator") == True
    assert AuthService.check_permission("Management", "Supervisor") == True
    assert AuthService.check_permission("Management", "Management") == True

    # Supervisor can access Operator and Supervisor
    assert AuthService.check_permission("Supervisor", "Operator") == True
    assert AuthService.check_permission("Supervisor", "Supervisor") == True
    assert AuthService.check_permission("Supervisor", "Management") == False

    # Operator can only access Operator
    assert AuthService.check_permission("Operator", "Operator") == True
    assert AuthService.check_permission("Operator", "Supervisor") == False
    assert AuthService.check_permission("Operator", "Management") == False
