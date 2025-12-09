# Part 1: API Developments & Data Modeling

## Question 1.1: Database Design (Data Modeling)

### Machine Metadata (PostgreSQL)

```sql
CREATE TABLE IF NOT EXISTS machine_metadata (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    sensor_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Implementation Reference:** `app/database.py` - `init_postgres_schema()`

### Sensor Data (InfluxDB)

**Measurement:** `sensor_data`

**Tags (Indexed):**
- `machine_id` - Identifies which machine generated the data
- `sensor_type` - Type of sensor (temperature, pressure, speed, vibration)
- `unit` - Unit of measurement (celsius, psi, rpm, mm/s)

**Fields (Values):**
- `value` (float) - The actual sensor reading

**Timestamp:** Automatically indexed by InfluxDB

**Example Data Point:**
```python
Point("sensor_data")
    .tag("machine_id", "1")
    .tag("sensor_type", "temperature")
    .tag("unit", "celsius")
    .field("value", 75.5)
    .time(datetime.utcnow())
```

**Implementation Reference:** `app/repositories/machine_repository.py` - `SensorDataRepository.write_sensor_data()`

### Optimization Strategies

#### 1. InfluxDB Optimization

**Indexing:**
- Tags (`machine_id`, `sensor_type`, `unit`) are automatically indexed by InfluxDB
- Time-based indexing is built-in for fast range queries
- Tag cardinality is kept low (limited sensor types and machines)

**Data Retention Policies:**
```flux
// High-resolution data: Keep for 30 days
CREATE RETENTION POLICY "30_days" ON "sensors" DURATION 30d REPLICATION 1 DEFAULT

// Downsampled data: Keep aggregated data for 1 year
CREATE RETENTION POLICY "1_year" ON "sensors" DURATION 365d REPLICATION 1

// Continuous Query for downsampling
CREATE CONTINUOUS QUERY "cq_hourly_avg" ON "sensors"
BEGIN
  SELECT mean(value) AS value
  INTO "1_year"."sensor_data"
  FROM "30_days"."sensor_data"
  GROUP BY time(1h), machine_id, sensor_type, unit
END
```

**Query Optimization:**
- Use `aggregateWindow()` for time-based aggregation (implemented in query method)
- Filter by tags first, then by time range
- Limit result sets with appropriate time windows

#### 2. PostgreSQL Optimization

**Indexing:**
```sql
-- Index on frequently queried columns
CREATE INDEX idx_machine_status ON machine_metadata(status);
CREATE INDEX idx_machine_sensor_type ON machine_metadata(sensor_type);
CREATE INDEX idx_machine_location ON machine_metadata(location);

-- Composite index for common query patterns
CREATE INDEX idx_machine_status_type ON machine_metadata(status, sensor_type);
```

**Partitioning (for scale):**
```sql
-- If machine_metadata grows large, partition by status
CREATE TABLE machine_metadata_active PARTITION OF machine_metadata
    FOR VALUES IN ('active');

CREATE TABLE machine_metadata_inactive PARTITION OF machine_metadata
    FOR VALUES IN ('inactive', 'maintenance');
```

#### 3. Query Performance for Historical Analytics

**Weekly/Monthly Queries:**
- Use InfluxDB's `aggregateWindow()` with appropriate intervals (1h, 1d)
- Implement Redis caching for frequently accessed historical reports
- Pre-aggregate common time ranges using Continuous Queries
- Use connection pooling for PostgreSQL to reduce connection overhead

**Implementation in Code:**
```python
# app/repositories/machine_repository.py
query = f'''
    from(bucket: "{config.INFLUXDB_BUCKET}")
      |> range(start: {start_time}, stop: {end_time})
      |> filter(fn: (r) => r["_measurement"] == "sensor_data")
      |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
      |> filter(fn: (r) => r["_field"] == "value")
      |> aggregateWindow(every: {interval}, fn: mean, createEmpty: false)
      |> yield(name: "mean")
'''
```

---

## Question 1.2: RESTful API Design

### Ingestion Endpoint

**Endpoint:** `POST /api/v1/data/ingest`

**JSON Request Body Structure:**
```json
{
  "gateway_id": "gateway_001",
  "timestamp": "2024-12-08T10:30:00Z",
  "data": [
    {
      "machine_id": 1,
      "sensor_type": "temperature",
      "value": 75.5,
      "timestamp": "2024-12-08T10:30:00Z",
      "unit": "celsius"
    },
    {
      "machine_id": 1,
      "sensor_type": "pressure",
      "value": 101.3,
      "timestamp": "2024-12-08T10:30:00Z",
      "unit": "psi"
    },
    {
      "machine_id": 2,
      "sensor_type": "speed",
      "value": 1850.0,
      "timestamp": "2024-12-08T10:30:00Z",
      "unit": "rpm"
    }
  ]
}
```

**Design Rationale:**
- Batch ingestion reduces HTTP overhead
- `gateway_id` for traceability and debugging
- Each data point includes `machine_id`, `sensor_type`, `value`, `timestamp`, and `unit`
- ISO 8601 timestamp format for consistency

**Implementation Reference:** `app/api/routes.py` - `/data/ingest` endpoint

### Retrieval Endpoint

**Endpoint:** `GET /api/v1/data/machine/{machine_id}`

**Query Parameters:**
- `start_time` (required) - ISO 8601 format (e.g., `2024-12-01T00:00:00Z`)
- `end_time` (required) - ISO 8601 format (e.g., `2024-12-08T23:59:59Z`)
- `interval` (optional, default: `1h`) - Aggregation window (e.g., `5m`, `1h`, `1d`)

**Example Request:**
```
GET /api/v1/data/machine/1?start_time=2024-12-01T00:00:00Z&end_time=2024-12-08T23:59:59Z&interval=1h
```

**Response Structure:**
```json
{
  "status": "success",
  "machine_id": 1,
  "machine_name": "CNC Machine A",
  "start_time": "2024-12-01T00:00:00Z",
  "end_time": "2024-12-08T23:59:59Z",
  "interval": "1h",
  "data_points": 168,
  "data": [
    {
      "time": "2024-12-01T00:00:00Z",
      "machine_id": "1",
      "sensor_type": "temperature",
      "unit": "celsius",
      "value": 75.5,
      "field": "value"
    }
  ]
}
```

**Implementation Reference:** `app/api/routes.py` - `/data/machine/<int:machine_id>` endpoint

### Implementation: Input Data Validation

**Code Implementation:**

```python
# app/controllers/data_controller.py

from marshmallow import ValidationError
from app.models.schemas import SensorDataIngestSchema
from app.repositories.machine_repository import SensorDataRepository
from app.utils.logger import logger

class DataController:
    """Controller for data ingestion and retrieval"""

    @staticmethod
    def ingest_sensor_data(request_data):
        """
        Handle sensor data ingestion with validation
        Returns: (response_dict, status_code)
        """
        try:
            # Step 1: Schema validation
            schema = SensorDataIngestSchema()
            validated_data = schema.load(request_data)

            # Step 2: Log successful validation
            logger.info("Data ingestion request received", extra={
                'extra_data': {
                    'gateway_id': validated_data['gateway_id'],
                    'data_points': len(validated_data['data'])
                }
            })

            # Step 3: Write to InfluxDB
            SensorDataRepository.write_sensor_data(validated_data['data'])

            # Step 4: Return success response
            return {
                "status": "success",
                "message": f"Ingested {len(validated_data['data'])} data points",
                "gateway_id": validated_data['gateway_id']
            }, 201

        except ValidationError as e:
            # Handle validation errors
            logger.warning("Validation error in data ingestion", extra={
                'extra_data': {'errors': e.messages}
            })
            return {
                "status": "error",
                "errors": e.messages
            }, 400

        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Error ingesting data: {e}", extra={
                'extra_data': {'error_type': type(e).__name__}
            })
            return {
                "status": "error",
                "message": "Internal server error"
            }, 500
```

**Validation Schema:**

```python
# app/models/schemas.py

from marshmallow import Schema, fields, validate, ValidationError

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
    data = fields.List(
        fields.Nested(SensorDataPointSchema), 
        required=True, 
        validate=validate.Length(min=1)
    )
```

**Validation Process:**

1. **Type Validation:** Ensures `machine_id` is integer, `value` is float, etc.
2. **Required Fields:** All mandatory fields must be present
3. **Format Validation:** Timestamp must be valid ISO 8601 format
4. **Business Rules:** Data array must contain at least 1 data point
5. **Error Handling:** Returns 400 with detailed error messages if validation fails

**Example Validation Error Response:**
```json
{
  "status": "error",
  "errors": {
    "data": {
      "0": {
        "value": ["Not a valid number."],
        "timestamp": ["Not a valid datetime."]
      }
    },
    "gateway_id": ["Missing data for required field."]
  }
}
```

**Key Benefits:**
- Early validation prevents invalid data from reaching the database
- Detailed error messages help clients fix issues quickly
- Structured logging for debugging and monitoring
- Type safety ensures data consistency
