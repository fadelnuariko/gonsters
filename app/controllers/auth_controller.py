from marshmallow import ValidationError
from app.models.schemas import UserLoginSchema, UserSchema
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.utils.logger import logger


class AuthController:
    """Controller for authentication operations"""

    @staticmethod
    def login(request_data):
        """
        Handle user login
        Returns: (response_dict, status_code)
        """
        try:
            schema = UserLoginSchema()
            validated_data = schema.load(request_data)

            username = validated_data["username"]
            password = validated_data["password"]

            user = UserRepository.authenticate_user(username, password)

            if not user:
                return {
                    "status": "error",
                    "message": "Invalid username or password",
                }, 401

            # Create JWT token
            token_data = {
                "user_id": user["id"],
                "username": user["username"],
                "role": user["role"],
            }

            access_token = AuthService.create_access_token(token_data)

            logger.info(f"User logged in: {username} (Role: {user['role']})")

            return {
                "status": "success",
                "message": "Login successful",
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "role": user["role"],
                },
            }, 200

        except ValidationError as e:
            return {"status": "error", "errors": e.messages}, 400
        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            return {"status": "error", "message": "Internal server error"}, 500

    @staticmethod
    def register(request_data):
        """
        Handle user registration
        Returns: (response_dict, status_code)
        """
        try:
            username = request_data.get("username")
            password = request_data.get("password")
            role = request_data.get("role", "Operator")

            if not username or not password:
                return {
                    "status": "error",
                    "message": "Username and password are required",
                }, 400

            existing_user = UserRepository.get_user_by_username(username)
            if existing_user:
                return {"status": "error", "message": "Username already exists"}, 409

            user = UserRepository.create_user(username, password, role)

            schema = UserSchema()
            return {
                "status": "success",
                "message": "User registered successfully",
                "user": schema.dump(user),
            }, 201

        except Exception as e:
            logger.error(f"Registration error: {e}", exc_info=True)
            return {"status": "error", "message": "Internal server error"}, 500
