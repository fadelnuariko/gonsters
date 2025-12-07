from marshmallow import Schema, fields, validate, ValidationError

class MachineMetadataSchema(Schema):
    """Schema for machine metadata"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    location = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    sensor_type = fields.Str(required=True, validate=validate.OneOf(['temperature', 'pressure', 'speed', 'vibration']))
    status = fields.Str(validate=validate.OneOf(['active', 'inactive', 'maintenance']))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class SensorDataPointSchema(Schema):
    """Schema for a single sensor data point"""
    machine_id = fields.Int(required=True)
    sensor_type = fields.Str(required=True)
    value = fields.Float(required=True)
    timestamp = fields.DateTime(required=True)
    unit = fields.Str(required=True)

class SensorDataIngestSchema(Schema):
    """Schema for batch sensor data ingestion"""
    gateway_id = fields.Str(required=True)
    timestamp = fields.DateTime(required=True)
    data = fields.List(fields.Nested(SensorDataPointSchema), required=True, validate=validate.Length(min=1))

class UserLoginSchema(Schema):
    """Schema for user login"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    password = fields.Str(required=True, validate=validate.Length(min=6))

class UserSchema(Schema):
    """Schema for user data"""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    role = fields.Str(required=True, validate=validate.OneOf(['Operator', 'Supervisor', 'Management']))
    created_at = fields.DateTime(dump_only=True)
