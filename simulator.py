"""
IoT Device Simulator - Simulates multiple machines sending sensor data via MQTT
"""
import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

class MachineSimulator:
    """Simulates an industrial machine sending sensor data"""

    def __init__(self, machine_id, factory_id, sensor_types):
        self.machine_id = machine_id
        self.factory_id = factory_id
        self.sensor_types = sensor_types
        self.client = mqtt.Client(client_id=f"machine_{machine_id}_simulator")

    def connect(self, broker="localhost", port=1883):
        """Connect to MQTT broker"""
        try:
            self.client.connect(broker, port, keepalive=60)
            print(f"✅ Machine {self.machine_id} connected to MQTT broker")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            raise

    def generate_sensor_data(self, sensor_type):
        """Generate realistic sensor data based on type"""
        data_ranges = {
            'temperature': (65.0, 85.0, 'celsius'),
            'pressure': (95.0, 105.0, 'psi'),
            'speed': (1000.0, 3000.0, 'rpm'),
            'vibration': (0.1, 2.5, 'mm/s')
        }

        if sensor_type in data_ranges:
            min_val, max_val, unit = data_ranges[sensor_type]
            value = round(random.uniform(min_val, max_val), 2)
        else:
            value = round(random.uniform(0, 100), 2)
            unit = 'unknown'

        return {
            'machine_id': self.machine_id,
            'sensor_type': sensor_type,
            'value': value,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'unit': unit
        }

    def publish_data(self):
        """Publish sensor data to MQTT topic"""
        for sensor_type in self.sensor_types:
            data = self.generate_sensor_data(sensor_type)
            topic = f"factory/{self.factory_id}/machine/{self.machine_id}/telemetry"

            payload = json.dumps(data)
            self.client.publish(topic, payload)

            print(f"📤 Machine {self.machine_id} | {sensor_type}: {data['value']} {data['unit']}")

    def run(self, interval=5):
        """Run simulator continuously"""
        print(f"🚀 Starting simulator for Machine {self.machine_id}")
        try:
            while True:
                self.publish_data()
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n⏹️  Stopping simulator for Machine {self.machine_id}")
            self.client.disconnect()

def main():
    """Main function to run multiple machine simulators"""
    print("=" * 60)
    print("🏭 Industrial IoT Device Simulator")
    print("=" * 60)

    BROKER = "localhost"
    PORT = 1883
    INTERVAL = 5

    machines = [
        {
            'machine_id': 1,
            'factory_id': 'A',
            'sensors': ['temperature', 'pressure']
        },
        {
            'machine_id': 2,
            'factory_id': 'A',
            'sensors': ['temperature', 'speed']
        },
        {
            'machine_id': 3,
            'factory_id': 'B',
            'sensors': ['vibration', 'temperature']
        }
    ]

    simulators = []
    for config in machines:
        sim = MachineSimulator(
            machine_id=config['machine_id'],
            factory_id=config['factory_id'],
            sensor_types=config['sensors']
        )
        sim.connect(BROKER, PORT)
        simulators.append(sim)

    print(f"\n✅ All machines connected. Publishing data every {INTERVAL} seconds...")
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

if __name__ == '__main__':
    main()
