from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import config
from app.utils.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class AuthService:
    """Service for authentication and authorization"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password is too long (max 72 bytes)")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    @staticmethod
    def create_access_token(data: dict) -> str:
        """
        Create JWT access token

        Args:
            data: Dictionary containing user information (user_id, username, role)

        Returns:
            JWT token string
        """
        to_encode = data.copy()

        expire = datetime.utcnow() + timedelta(minutes=config.JWT_EXPIRATION_MINUTES)
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})

        encoded_jwt = jwt.encode(
            to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM
        )

        logger.info(f"JWT token created for user: {data.get('username')}")

        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode and verify JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.warning(f"JWT decode error: {e}")
            raise

    @staticmethod
    def check_permission(user_role: str, required_role: str) -> bool:
        """
        Check if user role has permission for required role

        Role hierarchy: Operator < Supervisor < Management
        """
        role_hierarchy = {"Operator": 1, "Supervisor": 2, "Management": 3}

        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level
