import pytest
from marshmallow import ValidationError
from app.models.schemas import MachineMetadataSchema, SensorDataIngestSchema

def test_machine_metadata_schema_valid():
    """Test valid machine metadata"""
    schema = MachineMetadataSchema()
    data = {
        "name": "Test Machine",
        "location": "Factory A",
        "sensor_type": "temperature",
        "status": "active"
    }

    result = schema.load(data)
    assert result["name"] == "Test Machine"
    assert result["sensor_type"] == "temperature"

def test_machine_metadata_schema_invalid():
    """Test invalid machine metadata"""
    schema = MachineMetadataSchema()
    data = {
        "name": "Test Machine",
        "location": "Factory A",
        "sensor_type": "invalid_type",
        "status": "active"
    }

    with pytest.raises(ValidationError):
        schema.load(data)

def test_sensor_data_ingest_schema():
    """Test sensor data ingestion schema"""
    schema = SensorDataIngestSchema()
    data = {
        "gateway_id": "gw-001",
        "timestamp": "2024-12-09T10:00:00Z",
        "data": [
            {
                "machine_id": 1,
                "sensor_type": "temperature",
                "value": 75.5,
                "timestamp": "2024-12-09T10:00:00Z",
                "unit": "celsius"
            }
        ]
    }

    result = schema.load(data)
    assert result["gateway_id"] == "gw-001"
    assert len(result["data"]) == 1
