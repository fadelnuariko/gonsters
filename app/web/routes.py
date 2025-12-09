"""
Web routes for the dashboard interface
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.controllers.auth_controller import AuthController
from app.controllers.data_controller import MachineController
from app.repositories.user_repository import UserRepository
from app.repositories.machine_repository import MachineRepository
from app.web.auth import login_required, role_required

web_bp = Blueprint("web", __name__)


# ============ Authentication Routes ============
@web_bp.route("/")
def index():
    """Redirect to dashboard or login"""
    if "user" in session:
        return redirect(url_for("web.dashboard"))
    return redirect(url_for("web.login"))


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Call auth controller
        response, status_code = AuthController.login(
            {"username": username, "password": password}
        )

        if status_code == 200:
            # Store user info and token in session
            session["user"] = response["user"]
            session["token"] = response["access_token"]
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("web.dashboard"))
        else:
            flash(response.get("message", "Invalid credentials"), "danger")

    return render_template("login.html")


@web_bp.route("/logout")
def logout():
    """Logout and clear session"""
    username = session.get("user", {}).get("username", "User")
    session.clear()
    flash(f"Goodbye, {username}! You have been logged out.", "info")
    return redirect(url_for("web.login"))


# ============ Dashboard ============
@web_bp.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard"""
    # Get all machines
    machines_response, _ = MachineController.get_all_machines()
    machines = machines_response.get("machines", [])

    # Calculate statistics
    stats = {
        "total_machines": len(machines),
        "active_machines": sum(1 for m in machines if m.get("status") == "active"),
        "maintenance_machines": sum(
            1 for m in machines if m.get("status") == "maintenance"
        ),
        "total_sensors": len(machines),  # Simplified: 1 sensor per machine
    }

    return render_template("dashboard.html", machines=machines, stats=stats)


# ============ Machine Management ============
@web_bp.route("/machines")
@login_required
def machines_list():
    """List all machines"""
    response, _ = MachineController.get_all_machines()
    machines = response.get("machines", [])
    return render_template("machines/list.html", machines=machines)


@web_bp.route("/machines/create", methods=["GET", "POST"])
@login_required
@role_required("Supervisor")
def machine_create():
    """Create new machine"""
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "location": request.form.get("location"),
            "sensor_type": request.form.get("sensor_type"),
            "status": request.form.get("status", "active"),
        }

        try:
            response, status_code = MachineController.create_machine(data)

            if status_code == 201:
                flash(f"Machine '{data['name']}' created successfully!", "success")
                return redirect(url_for("web.machines_list"))
            else:
                # Show detailed error
                error_msg = response.get("message", "Failed to create machine")
                errors = response.get("errors", {})
                if errors:
                    error_details = ", ".join([f"{k}: {v}" for k, v in errors.items()])
                    flash(f"{error_msg}: {error_details}", "danger")
                else:
                    flash(error_msg, "danger")
        except Exception as e:
            flash(f"Error creating machine: {str(e)}", "danger")

    return render_template("machines/form.html", machine=None)


@web_bp.route("/machines/<int:machine_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Supervisor")
def machine_edit(machine_id):
    """Edit machine"""
    # Get machine details
    response, status_code = MachineController.get_machine(machine_id)

    if status_code != 200:
        flash("Machine not found", "danger")
        return redirect(url_for("web.machines_list"))

    machine = response.get("machine")

    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "location": request.form.get("location"),
            "sensor_type": request.form.get("sensor_type"),
            "status": request.form.get("status"),
        }

        try:
            response, status_code = MachineController.update_machine(machine_id, data)

            if status_code == 200:
                flash(f"Machine '{data['name']}' updated successfully!", "success")
                return redirect(url_for("web.machines_list"))
            else:
                error_msg = response.get("message", "Failed to update machine")
                flash(error_msg, "danger")
        except Exception as e:
            flash(f"Error updating machine: {str(e)}", "danger")

    return render_template("machines/form.html", machine=machine)


@web_bp.route("/machines/<int:machine_id>/delete", methods=["POST"])
@login_required
@role_required("Supervisor")
def machine_delete(machine_id):
    """Delete machine"""
    try:
        response, status_code = MachineController.delete_machine(machine_id)

        if status_code == 200:
            flash("Machine deleted successfully!", "success")
        else:
            flash(response.get("message", "Failed to delete machine"), "danger")
    except Exception as e:
        flash(f"Error deleting machine: {str(e)}", "danger")

    return redirect(url_for("web.machines_list"))


@web_bp.route("/machines/<int:machine_id>/monitor")
@login_required
def machine_monitor(machine_id):
    """Monitor machine in real-time"""
    response, status_code = MachineController.get_machine(machine_id)

    if status_code != 200:
        flash("Machine not found", "danger")
        return redirect(url_for("web.machines_list"))

    machine = response.get("machine")
    return render_template("machines/monitor.html", machine=machine)


# ============ User Management ============
@web_bp.route("/users")
@login_required
@role_required("Management")
def users_list():
    """List all users (Management only)"""
    users = UserRepository.get_all_users()
    return render_template("users/list.html", users=users)


@web_bp.route("/users/create", methods=["GET", "POST"])
@login_required
@role_required("Management")
def user_create():
    """Create new user (Management only)"""
    if request.method == "POST":
        data = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "role": request.form.get("role"),
        }

        response, status_code = AuthController.register(data)

        if status_code == 201:
            flash(f"User '{data['username']}' created successfully!", "success")
            return redirect(url_for("web.users_list"))
        else:
            flash(response.get("message", "Failed to create user"), "danger")

    return render_template("users/create.html")
