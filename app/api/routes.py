from flask import Blueprint, request, jsonify
from app.controllers.data_controller import DataController, MachineController

api_bp = Blueprint('api', __name__)

# ============ Health Check ============
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "gonsters-backend"
    }), 200

# ============ Data Ingestion & Retrieval ============
@api_bp.route('/data/ingest', methods=['POST'])
def ingest_data():
    """Endpoint for ingesting sensor data"""
    response, status_code = DataController.ingest_sensor_data(request.json)
    return jsonify(response), status_code

@api_bp.route('/data/machine/<int:machine_id>', methods=['GET'])
def get_machine_data(machine_id):
    """Endpoint for retrieving machine historical data"""
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    interval = request.args.get('interval', '1h')

    response, status_code = DataController.get_machine_data(
        machine_id, start_time, end_time, interval
    )
    return jsonify(response), status_code

# ============ Machine Metadata Management ============
@api_bp.route('/machines', methods=['GET'])
def get_machines():
    """Get all machines"""
    response, status_code = MachineController.get_all_machines()
    return jsonify(response), status_code

@api_bp.route('/machines/<int:machine_id>', methods=['GET'])
def get_machine(machine_id):
    """Get machine by ID"""
    response, status_code = MachineController.get_machine(machine_id)
    return jsonify(response), status_code

@api_bp.route('/machines', methods=['POST'])
def create_machine():
    """Create new machine"""
    response, status_code = MachineController.create_machine(request.json)
    return jsonify(response), status_code
