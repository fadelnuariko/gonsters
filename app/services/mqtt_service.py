import paho.mqtt.client as mqtt
import json
import threading
from app.config import config
from app.utils.logger import logger
from app.repositories.machine_repository import SensorDataRepository


class MQTTService:
    """MQTT Service for subscribing to sensor data topics"""

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.is_connected = False

    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.is_connected = True
            logger.info(
                "Connected to MQTT broker successfully",
                extra={
                    "extra_data": {
                        "broker": config.MQTT_BROKER,
                        "port": config.MQTT_PORT,
                    }
                },
            )

            topic = "factory/+/machine/+/telemetry"
            client.subscribe(topic)
            logger.info(f"Subscribed to topic: {topic}")

        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.is_connected = False
        if rc != 0:
            logger.warning(
                "Unexpected MQTT disconnection. Attempting to reconnect...",
                extra={"extra_data": {"return_code": rc}},
            )

    def on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            topic_parts = msg.topic.split("/")
            factory_id = topic_parts[1] if len(topic_parts) > 1 else "unknown"
            machine_id = topic_parts[3] if len(topic_parts) > 3 else "unknown"

            payload = json.loads(msg.payload.decode("utf-8"))

            logger.info(
                f"MQTT message received from {msg.topic}",
                extra={
                    "extra_data": {
                        "topic": msg.topic,
                        "factory": factory_id,
                        "machine_id": machine_id,
                        "payload": payload,
                    }
                },
            )

            if not self._validate_payload(payload):
                logger.warning(
                    "Invalid payload structure",
                    extra={"extra_data": {"payload": payload}},
                )
                return

            data_point = {
                "machine_id": int(payload.get("machine_id", machine_id)),
                "sensor_type": payload["sensor_type"],
                "value": float(payload["value"]),
                "timestamp": payload["timestamp"],
                "unit": payload["unit"],
            }

            SensorDataRepository.write_sensor_data([data_point])

            logger.info(
                f"Successfully ingested data from MQTT for machine {data_point['machine_id']}"
            )

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to decode MQTT message: {e}",
                extra={"extra_data": {"payload": msg.payload}},
            )
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}", exc_info=True)

    def _validate_payload(self, payload):
        """Validate MQTT payload structure"""
        required_fields = ["sensor_type", "value", "timestamp", "unit"]
        return all(field in payload for field in required_fields)

    def connect(self):
        """Connect to MQTT broker"""
        try:
            logger.info(
                f"Connecting to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}"
            )
            self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, keepalive=60)

            self.client.loop_start()

            logger.info("MQTT client loop started")

        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}", exc_info=True)
            raise

    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Disconnected from MQTT broker")


mqtt_service = MQTTService()
