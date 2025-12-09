"""
Web authentication decorators for session-based authentication
"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """Decorator to require login for web routes"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("web.login"))
        return f(*args, **kwargs)

    return decorated_function


def role_required(required_role):
    """Decorator to require specific role for web routes"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user" not in session:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("web.login"))

            user_role = session.get("user", {}).get("role")

            # Role hierarchy: Management > Supervisor > Operator
            role_hierarchy = {"Operator": 1, "Supervisor": 2, "Management": 3}

            user_level = role_hierarchy.get(user_role, 0)
            required_level = role_hierarchy.get(required_role, 999)

            if user_level < required_level:
                flash("You don't have permission to access this page.", "danger")
                return redirect(url_for("web.dashboard"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator
