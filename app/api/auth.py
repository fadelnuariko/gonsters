from functools import wraps
from flask import request, jsonify
from jose import JWTError
from app.services.auth_service import AuthService
from app.utils.logger import logger

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({
                    "status": "error",
                    "message": "Invalid token format. Use: Bearer <token>"
                }), 401

        if not token:
            return jsonify({
                "status": "error",
                "message": "Token is missing"
            }), 401

        try:
            payload = AuthService.decode_token(token)
            request.current_user = payload

        except JWTError:
            return jsonify({
                "status": "error",
                "message": "Token is invalid or expired"
            }), 401

        return f(*args, **kwargs)

    return decorated

def role_required(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({
                    "status": "error",
                    "message": "Authentication required"
                }), 401

            user_role = request.current_user.get('role')

            if not AuthService.check_permission(user_role, required_role):
                logger.warning(
                    f"Access denied for user {request.current_user.get('username')} "
                    f"(Role: {user_role}) to {required_role} endpoint"
                )
                return jsonify({
                    "status": "error",
                    "message": f"Access denied. Required role: {required_role} or higher",
                    "your_role": user_role
                }), 403

            return f(*args, **kwargs)

        return decorated

    return decorator
