from flask import Blueprint, request, jsonify
from app.controllers.data_controller import DataController, MachineController
from app.controllers.auth_controller import AuthController
from app.api.auth import token_required, role_required

api_bp = Blueprint("api", __name__)


# ============ Health Check ============
@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "gonsters-backend"}), 200


# ============ Authentication ============
@api_bp.route("/auth/register", methods=["POST"])
def register():
    """User registration endpoint"""
    response, status_code = AuthController.register(request.json)
    return jsonify(response), status_code


@api_bp.route("/auth/login", methods=["POST"])
def login():
    """User login endpoint"""
    response, status_code = AuthController.login(request.json)
    return jsonify(response), status_code


@api_bp.route("/auth/me", methods=["GET"])
@token_required
def get_current_user():
    """Get current authenticated user info"""
    return jsonify({"status": "success", "user": request.current_user}), 200


# ============ Data Ingestion & Retrieval ============
@api_bp.route("/data/ingest", methods=["POST"])
@token_required
@role_required("Operator")
def ingest_data():
    """Endpoint for ingesting sensor data (Operator+)"""
    response, status_code = DataController.ingest_sensor_data(request.json)
    return jsonify(response), status_code


@api_bp.route("/data/machine/<int:machine_id>", methods=["GET"])
@token_required
@role_required("Operator")
def get_machine_data(machine_id):
    """Endpoint for retrieving machine historical data (Operator+)"""
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    interval = request.args.get("interval", "1h")

    response, status_code = DataController.get_machine_data(
        machine_id, start_time, end_time, interval
    )
    return jsonify(response), status_code


# ============ Machine Metadata Management ============
@api_bp.route("/machines", methods=["GET"])
@token_required
@role_required("Operator")
def get_machines():
    """Get all machines (Operator+)"""
    response, status_code = MachineController.get_all_machines()
    return jsonify(response), status_code


@api_bp.route("/machines/<int:machine_id>", methods=["GET"])
@token_required
@role_required("Operator")
def get_machine(machine_id):
    """Get machine by ID (Operator+)"""
    response, status_code = MachineController.get_machine(machine_id)
    return jsonify(response), status_code


@api_bp.route("/machines", methods=["POST"])
@token_required
@role_required("Supervisor")
def create_machine():
    """Create new machine (Supervisor+)"""
    response, status_code = MachineController.create_machine(request.json)
    return jsonify(response), status_code


# ============ Configuration (Management Only) ============
@api_bp.route("/config/update", methods=["POST"])
@token_required
@role_required("Management")
def update_config():
    """Update system configuration (Management only)"""
    # This is a demo endpoint to show Management-only access
    return (
        jsonify(
            {
                "status": "success",
                "message": "Configuration updated successfully",
                "updated_by": request.current_user.get("username"),
                "role": request.current_user.get("role"),
            }
        ),
        200,
    )
