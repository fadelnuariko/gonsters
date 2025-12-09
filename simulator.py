"""
IoT Device Simulator - Simulates multiple machines sending sensor data via MQTT
Reads machine configurations from PostgreSQL database
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import os
import sys
from datetime import datetime

# Add app directory to path to import database utilities
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_postgres_connection
from app.config import config


class MachineSimulator:
    """Simulates an industrial machine sending sensor data"""

    def __init__(self, machine_id, machine_name, sensor_type, factory_id="A"):
        self.machine_id = machine_id
        self.machine_name = machine_name
        self.sensor_type = sensor_type
        self.factory_id = factory_id
        self.client = mqtt.Client(client_id=f"machine_{machine_id}_simulator")

    def connect(self, broker="localhost", port=1883):
        """Connect to MQTT broker"""
        try:
            self.client.connect(broker, port, keepalive=60)
            print(
                f"✅ Machine {self.machine_id} ({self.machine_name}) connected to MQTT broker"
            )
        except Exception as e:
            print(f"❌ Failed to connect Machine {self.machine_id}: {e}")
            raise

    def generate_sensor_data(self):
        """Generate realistic sensor data based on type"""
        data_ranges = {
            "temperature": (65.0, 85.0, "celsius"),
            "pressure": (95.0, 105.0, "psi"),
            "speed": (1000.0, 3000.0, "rpm"),
            "vibration": (0.1, 2.5, "mm/s"),
        }

        if self.sensor_type in data_ranges:
            min_val, max_val, unit = data_ranges[self.sensor_type]
            value = round(random.uniform(min_val, max_val), 2)
        else:
            value = round(random.uniform(0, 100), 2)
            unit = "unknown"

        return {
            "machine_id": self.machine_id,
            "sensor_type": self.sensor_type,
            "value": value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "unit": unit,
        }

    def publish_data(self):
        """Publish sensor data to MQTT topic"""
        data = self.generate_sensor_data()
        topic = f"factory/{self.factory_id}/machine/{self.machine_id}/telemetry"

        payload = json.dumps(data)
        self.client.publish(topic, payload)

        print(
            f"📤 {self.machine_name} (ID:{self.machine_id}) | {self.sensor_type}: {data['value']} {data['unit']}"
        )


def load_machines_from_database():
    """Load active machines from PostgreSQL database"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()

        # Query active machines
        cursor.execute(
            """
            SELECT id, name, sensor_type, status, location
            FROM machines
            WHERE status = 'active'
            ORDER BY id
        """
        )

        machines = cursor.fetchall()
        cursor.close()
        conn.close()

        print(f"\n📊 Loaded {len(machines)} active machines from database:")
        for machine in machines:
            print(f"   - ID {machine[0]}: {machine[1]} ({machine[2]}) at {machine[4]}")

        return machines

    except Exception as e:
        print(f"❌ Error loading machines from database: {e}")
        print("💡 Make sure the database is running and machines table exists")
        return []


def main():
    """Main function to run multiple machine simulators"""
    print("=" * 60)
    print("🏭 Industrial IoT Device Simulator (Database-Integrated)")
    print("=" * 60)

    # Configuration from environment or defaults
    BROKER = os.getenv("MQTT_BROKER", config.MQTT_BROKER)
    PORT = int(os.getenv("MQTT_PORT", config.MQTT_PORT))
    INTERVAL = int(os.getenv("SIMULATOR_INTERVAL", "5"))
    FACTORY_ID = os.getenv("SIMULATOR_FACTORY_ID", "A")

    print(f"\n⚙️  Configuration:")
    print(f"   MQTT Broker: {BROKER}:{PORT}")
    print(f"   Interval: {INTERVAL} seconds")
    print(f"   Factory ID: {FACTORY_ID}")

    # Load machines from database
    machines_data = load_machines_from_database()

    if not machines_data:
        print("\n⚠️  No active machines found in database!")
        print("💡 Create machines using the web dashboard or API first")
        return

    # Create simulators for each machine
    simulators = []
    for machine in machines_data:
        machine_id, name, sensor_type, status, location = machine
        sim = MachineSimulator(
            machine_id=machine_id,
            machine_name=name,
            sensor_type=sensor_type,
            factory_id=FACTORY_ID,
        )
        try:
            sim.connect(BROKER, PORT)
            simulators.append(sim)
        except Exception as e:
            print(f"⚠️  Skipping Machine {machine_id} due to connection error")

    if not simulators:
        print("\n❌ No simulators could connect to MQTT broker")
        print("💡 Make sure MQTT broker is running (mosquitto)")
        return

    print(
        f"\n✅ {len(simulators)} machines connected. Publishing data every {INTERVAL} seconds..."
    )
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            for sim in simulators:
                sim.publish_data()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down all simulators...")
        for sim in simulators:
            sim.client.disconnect()
        print("✅ All simulators stopped")


if __name__ == "__main__":
    main()
