# IoT Device Simulator

## Overview

This simulator reads active machines from the PostgreSQL database and simulates them sending sensor data via MQTT, just like real IoT devices would.

## Features

- ✅ **Database Integration**: Automatically loads machines from PostgreSQL
- ✅ **Dynamic**: Picks up new machines without code changes
- ✅ **Realistic Data**: Generates sensor readings based on machine type
- ✅ **MQTT Publishing**: Sends data to the same broker as real devices
- ✅ **Configurable**: Environment variables for all settings

## How It Works

1. Connects to PostgreSQL database
2. Queries all machines with `status = 'active'`
3. Creates a simulator for each machine
4. Publishes sensor data every 5 seconds (configurable)
5. Data flows through MQTT → Backend → InfluxDB
6. Visible in web dashboard monitoring page

## Prerequisites

- PostgreSQL database running with machines
- MQTT broker (Mosquitto) running
- Python dependencies installed

## Usage

### Local Development

```bash
# Make sure database and MQTT are running
docker-compose up -d postgres mosquitto

# Run simulator
python simulator.py
```

### With Docker Compose

```bash
# Start all services including simulator
docker-compose up -d

# View simulator logs
docker-compose logs -f simulator
```

### Create Test Machines First

If you don't have machines in the database:

```bash
# Option 1: Use web dashboard
# Go to http://localhost:5000
# Login and create machines via UI

# Option 2: Use API
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"supervisor_user","password":"password123"}'

# Use the token to create a machine
curl -X POST http://localhost:5000/api/v1/machines \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "CNC Machine A",
    "location": "Factory Floor 1",
    "sensor_type": "temperature",
    "status": "active"
  }'
```

## Configuration

### Environment Variables

```bash
# MQTT Settings
MQTT_BROKER=localhost        # MQTT broker hostname
MQTT_PORT=1883              # MQTT broker port

# Simulator Settings
SIMULATOR_INTERVAL=5         # Seconds between data publishes
SIMULATOR_FACTORY_ID=A      # Factory identifier

# Database (uses same config as main app)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=gonsters_metadata
POSTGRES_USER=admin
POSTGRES_PASSWORD=password123
```

## Output Example

```
============================================================
🏭 Industrial IoT Device Simulator (Database-Integrated)
============================================================

⚙️  Configuration:
   MQTT Broker: localhost:1883
   Interval: 5 seconds
   Factory ID: A

📊 Loaded 3 active machines from database:
   - ID 1: CNC Machine A (temperature) at Factory Floor 1
   - ID 2: Hydraulic Press B (pressure) at Factory Floor 2
   - ID 3: Conveyor Belt C (speed) at Warehouse

✅ Machine 1 (CNC Machine A) connected to MQTT broker
✅ Machine 2 (Hydraulic Press B) connected to MQTT broker
✅ Machine 3 (Conveyor Belt C) connected to MQTT broker

✅ 3 machines connected. Publishing data every 5 seconds...
Press Ctrl+C to stop

📤 CNC Machine A (ID:1) | temperature: 72.45 celsius
📤 Hydraulic Press B (ID:2) | pressure: 98.32 psi
📤 Conveyor Belt C (ID:3) | speed: 2156.78 rpm
```

## Monitoring Simulated Data

### 1. MQTT Subscriber

```bash
# Subscribe to all factory topics
mosquitto_sub -h localhost -t "factory/#" -v

# Subscribe to specific machine
mosquitto_sub -h localhost -t "factory/A/machine/1/telemetry" -v
```

### 2. Web Dashboard

1. Go to `http://localhost:5000`
2. Login
3. Navigate to **Machines**
4. Click **Monitor** on any machine
5. Watch real-time charts update with simulated data

### 3. InfluxDB Query

```bash
# Access InfluxDB container
docker exec -it gonsters-influxdb influx

# Query sensor data
> use sensor_data
> SELECT * FROM sensor_readings WHERE machine_id='1' ORDER BY time DESC LIMIT 10
```

## Sensor Data Ranges

The simulator generates realistic data for each sensor type:

| Sensor Type | Min | Max | Unit |
|------------|-----|-----|------|
| temperature | 65.0 | 85.0 | celsius |
| pressure | 95.0 | 105.0 | psi |
| speed | 1000.0 | 3000.0 | rpm |
| vibration | 0.1 | 2.5 | mm/s |

## Troubleshooting

### No machines found

```
⚠️  No active machines found in database!
💡 Create machines using the web dashboard or API first
```

**Solution**: Create machines with `status = 'active'` in the database

### MQTT connection failed

```
❌ Failed to connect Machine 1: [Errno 111] Connection refused
```

**Solution**: Make sure Mosquitto is running:
```bash
docker-compose up -d mosquitto
# OR
sudo systemctl start mosquitto
```

### Database connection error

```
❌ Error loading machines from database: could not connect to server
```

**Solution**: Make sure PostgreSQL is running:
```bash
docker-compose up -d postgres
```

## Integration with Main App

The simulator integrates seamlessly:

1. **Same Database**: Reads from `machines` table
2. **Same MQTT Broker**: Publishes to same topics
3. **Same Data Format**: Compatible with backend ingestion
4. **Same InfluxDB**: Data stored in same database

```
┌─────────────┐
│  Simulator  │ ──MQTT──┐
└─────────────┘         │
                        ↓
┌─────────────┐    ┌─────────┐    ┌──────────┐
│  PostgreSQL │───→│ Backend │───→│ InfluxDB │
│  (machines) │    │  (MQTT) │    │  (data)  │
└─────────────┘    └─────────┘    └──────────┘
                        ↑
                        │
                   ┌────────────┐
                   │ Web        │
                   │ Dashboard  │
                   └────────────┘
```

## Tips

- **Start with 1-2 machines** for testing
- **Use different sensor types** to see variety in dashboard
- **Set machines to 'active'** status to include in simulation
- **Monitor logs** to verify data publishing
- **Check web dashboard** to see real-time updates
