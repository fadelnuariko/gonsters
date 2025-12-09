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
            FROM machine_metadata
            WHERE status = 'active'
            ORDER BY id
        """
        )

        machines = cursor.fetchall()
        cursor.close()
        conn.close()

        print(f"\n📊 Loaded {len(machines)} active machines from database:")
        for machine in machines:
            # RealDictCursor returns dictionaries, not tuples
            print(
                f"   - ID {machine['id']}: {machine['name']} ({machine['sensor_type']}) at {machine['location']}"
            )

        return machines

    except Exception as e:
        print(f"❌ Error loading machines from database: {e}")
        print("💡 Make sure the database is running and machines table exists")
        return []


def main():
    """Main function to run multiple machine simulators with auto-detection"""
    print("=" * 60)
    print("🏭 Industrial IoT Device Simulator (Database-Integrated)")
    print("=" * 60)

    # Configuration from environment or defaults
    BROKER = os.getenv("MQTT_BROKER", config.MQTT_BROKER)
    PORT = int(os.getenv("MQTT_PORT", config.MQTT_PORT))
    INTERVAL = int(os.getenv("SIMULATOR_INTERVAL", "5"))
    RELOAD_INTERVAL = int(os.getenv("SIMULATOR_RELOAD_INTERVAL", "60"))
    FACTORY_ID = os.getenv("SIMULATOR_FACTORY_ID", "A")

    print(f"\n⚙️  Configuration:")
    print(f"   MQTT Broker: {BROKER}:{PORT}")
    print(f"   Data Interval: {INTERVAL} seconds")
    print(f"   Machine Reload: {RELOAD_INTERVAL} seconds")
    print(f"   Factory ID: {FACTORY_ID}")

    # Dictionary to track active simulators {machine_id: simulator}
    active_simulators = {}
    last_reload_time = 0

    print("\n🔄 Auto-detection enabled - will check for new machines every minute")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            current_time = time.time()

            # Reload machines from database periodically
            if current_time - last_reload_time >= RELOAD_INTERVAL:
                machines_data = load_machines_from_database()
                current_machine_ids = {m["id"] for m in machines_data}
                existing_machine_ids = set(active_simulators.keys())

                # Find new machines to add
                new_machine_ids = current_machine_ids - existing_machine_ids
                for machine in machines_data:
                    if machine["id"] in new_machine_ids:
                        sim = MachineSimulator(
                            machine_id=machine["id"],
                            machine_name=machine["name"],
                            sensor_type=machine["sensor_type"],
                            factory_id=FACTORY_ID,
                        )
                        try:
                            sim.connect(BROKER, PORT)
                            active_simulators[machine["id"]] = sim
                            print(f"➕ Added: {machine['name']} (ID:{machine['id']})")
                        except Exception as e:
                            print(f"⚠️  Failed to add Machine {machine['id']}: {e}")

                # Find deleted machines to remove
                deleted_machine_ids = existing_machine_ids - current_machine_ids
                for machine_id in deleted_machine_ids:
                    sim = active_simulators.pop(machine_id)
                    sim.client.disconnect()
                    print(f"➖ Removed: Machine ID {machine_id}")

                last_reload_time = current_time

                if not active_simulators:
                    print(
                        "\n⚠️  No active machines. Waiting for machines to be created..."
                    )

            # Publish data from all active simulators
            if active_simulators:
                for sim in active_simulators.values():
                    sim.publish_data()

            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down all simulators...")
        for sim in active_simulators.values():
            sim.client.disconnect()
        print("✅ All simulators stopped")


if __name__ == "__main__":
    main()
