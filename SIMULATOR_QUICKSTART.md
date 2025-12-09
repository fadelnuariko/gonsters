# Quick Start: IoT Simulator

## What It Does

The simulator reads machines from your PostgreSQL database and simulates them sending sensor data via MQTT - just like real IoT devices!

## Quick Test (Local)

```bash
# 1. Make sure services are running
docker-compose up -d postgres mosquitto

# 2. Create a test machine (via web dashboard or API)
# Go to http://localhost:5000, login, and create a machine
# OR use the API (see SIMULATOR_README.md)

# 3. Run the simulator
python simulator.py
```

You should see:
```
🏭 Industrial IoT Device Simulator (Database-Integrated)
📊 Loaded 1 active machines from database:
   - ID 1: CNC Machine A (temperature) at Factory Floor 1
✅ Machine 1 (CNC Machine A) connected to MQTT broker
📤 CNC Machine A (ID:1) | temperature: 72.45 celsius
```

## With Docker

```bash
# Start with simulator
docker-compose --profile simulator up -d

# View logs
docker-compose logs -f simulator

# Stop simulator
docker-compose --profile simulator down
```

## Monitor the Data

1. **Web Dashboard**: Go to http://localhost:5000 → Machines → Monitor
2. **MQTT**: `mosquitto_sub -h localhost -t "factory/#" -v`

## Troubleshooting

**No machines found?**
- Create machines with `status = 'active'` in the web dashboard

**MQTT connection failed?**
- Make sure mosquitto is running: `docker-compose up -d mosquitto`

**Database connection error?**
- Make sure postgres is running: `docker-compose up -d postgres`

See `SIMULATOR_README.md` for full documentation.
