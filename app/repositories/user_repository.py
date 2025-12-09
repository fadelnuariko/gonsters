from app.database import get_postgres_connection
from app.services.auth_service import AuthService
from app.utils.logger import logger


class UserRepository:
    """Repository for user operations"""

    @staticmethod
    def create_user(username: str, password: str, role: str):
        """Create a new user"""
        conn = get_postgres_connection()
        cursor = conn.cursor()

        try:
            password_hash = AuthService.hash_password(password)

            cursor.execute(
                """
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
                RETURNING id, username, role, created_at
            """,
                (username, password_hash, role),
            )

            user = cursor.fetchone()
            conn.commit()

            logger.info(f"User created: {username} with role {role}")
            return user

        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating user: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_user_by_username(username: str):
        """Get user by username"""
        conn = get_postgres_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT id, username, password_hash, role, created_at
                FROM users
                WHERE username = %s
            """,
                (username,),
            )

            user = cursor.fetchone()
            return user

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_user_by_id(user_id: int):
        """Get user by ID"""
        conn = get_postgres_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT id, username, role, created_at
                FROM users
                WHERE id = %s
            """,
                (user_id,),
            )

            user = cursor.fetchone()
            return user

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def authenticate_user(username: str, password: str):
        """Authenticate user credentials"""
        user = UserRepository.get_user_by_username(username)

        if not user:
            logger.warning(f"Authentication failed: User not found - {username}")
            return None

        if not AuthService.verify_password(password, user["password_hash"]):
            logger.warning(f"Authentication failed: Invalid password - {username}")
            return None

        logger.info(f"User authenticated successfully: {username}")
        return user
