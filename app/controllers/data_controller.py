from marshmallow import ValidationError
from app.models.schemas import SensorDataIngestSchema, MachineMetadataSchema
from app.repositories.machine_repository import MachineRepository, SensorDataRepository
from app.utils.logger import logger


class DataController:
    """Controller for data ingestion and retrieval"""

    @staticmethod
    def ingest_sensor_data(request_data):
        """
        Handle sensor data ingestion
        Returns: (response_dict, status_code)
        """
        try:

            schema = SensorDataIngestSchema()
            validated_data = schema.load(request_data)

            logger.info(
                "Data ingestion request received",
                extra={
                    "extra_data": {
                        "gateway_id": validated_data["gateway_id"],
                        "data_points": len(validated_data["data"]),
                    }
                },
            )

            SensorDataRepository.write_sensor_data(validated_data["data"])

            return {
                "status": "success",
                "message": f"Ingested {len(validated_data['data'])} data points",
                "gateway_id": validated_data["gateway_id"],
            }, 201

        except ValidationError as e:
            logger.warning(
                "Validation error in data ingestion",
                extra={"extra_data": {"errors": e.messages}},
            )
            return {"status": "error", "errors": e.messages}, 400

        except Exception as e:
            logger.error(
                f"Error ingesting data: {e}",
                extra={"extra_data": {"error_type": type(e).__name__}},
            )
            return {"status": "error", "message": "Internal server error"}, 500

    @staticmethod
    def get_machine_data(machine_id, start_time, end_time, interval="1h"):
        """
        Retrieve historical machine data
        Returns: (response_dict, status_code)
        """
        try:

            if not start_time or not end_time:
                return {
                    "status": "error",
                    "message": "start_time and end_time are required",
                }, 400

            machine = MachineRepository.get_machine_by_id(machine_id)
            if not machine:
                return {
                    "status": "error",
                    "message": f"Machine with ID {machine_id} not found",
                }, 404

            logger.info(
                f"Data retrieval request for machine {machine_id}",
                extra={
                    "extra_data": {
                        "start_time": start_time,
                        "end_time": end_time,
                        "interval": interval,
                    }
                },
            )

            data = SensorDataRepository.query_sensor_data(
                machine_id, start_time, end_time, interval
            )

            return {
                "status": "success",
                "machine_id": machine_id,
                "machine_name": machine["name"],
                "start_time": start_time,
                "end_time": end_time,
                "interval": interval,
                "data_points": len(data),
                "data": data,
            }, 200

        except Exception as e:
            logger.error(
                f"Error retrieving machine data: {e}",
                extra={"extra_data": {"error_type": type(e).__name__}},
            )
            return {"status": "error", "message": "Internal server error"}, 500


class MachineController:
    """Controller for machine metadata operations"""

    @staticmethod
    def get_all_machines():
        """Get all machines"""
        try:
            machines = MachineRepository.get_all_machines()
            schema = MachineMetadataSchema(many=True)
            return {
                "status": "success",
                "count": len(machines),
                "machines": schema.dump(machines),
            }, 200
        except Exception as e:
            logger.error(f"Error retrieving machines: {e}")
            return {"status": "error", "message": "Internal server error"}, 500

    @staticmethod
    def get_machine(machine_id):
        """Get machine by ID"""
        try:
            machine = MachineRepository.get_machine_by_id(machine_id)
            if not machine:
                return {
                    "status": "error",
                    "message": f"Machine with ID {machine_id} not found",
                }, 404

            schema = MachineMetadataSchema()
            return {"status": "success", "machine": schema.dump(machine)}, 200
        except Exception as e:
            logger.error(f"Error retrieving machine: {e}")
            return {"status": "error", "message": "Internal server error"}, 500

    @staticmethod
    def create_machine(request_data):
        """Create new machine"""
        try:
            schema = MachineMetadataSchema()
            validated_data = schema.load(request_data)

            machine = MachineRepository.create_machine(validated_data)

            logger.info(f"Machine created: {machine['id']}")

            return {
                "status": "success",
                "message": "Machine created successfully",
                "machine": schema.dump(machine),
            }, 201

        except ValidationError as e:
            return {"status": "error", "errors": e.messages}, 400
        except Exception as e:
            logger.error(f"Error creating machine: {e}")
            return {"status": "error", "message": "Internal server error"}, 500

    @staticmethod
    def update_machine(machine_id, request_data):
        """Update existing machine"""
        try:
            schema = MachineMetadataSchema()
            validated_data = schema.load(request_data, partial=True)

            machine = MachineRepository.update_machine(machine_id, validated_data)

            if not machine:
                return {"status": "error", "message": "Machine not found"}, 404

            logger.info(f"Machine updated: {machine_id}")

            return {
                "status": "success",
                "message": "Machine updated successfully",
                "machine": schema.dump(machine),
            }, 200

        except ValidationError as e:
            return {"status": "error", "errors": e.messages}, 400
        except Exception as e:
            logger.error(f"Error updating machine: {e}")
            return {"status": "error", "message": "Internal server error"}, 500

    @staticmethod
    def delete_machine(machine_id):
        """Delete machine"""
        try:
            deleted = MachineRepository.delete_machine(machine_id)

            if not deleted:
                return {"status": "error", "message": "Machine not found"}, 404

            logger.info(f"Machine deleted: {machine_id}")

            return {
                "status": "success",
                "message": "Machine deleted successfully",
            }, 200

        except Exception as e:
            logger.error(f"Error deleting machine: {e}")
            return {"status": "error", "message": "Internal server error"}, 500
