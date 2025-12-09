import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import init_postgres_schema
from app.utils.logger import logger
from app.services.mqtt_service import mqtt_service

app = create_app()

def init_app():
    """Initialize application on startup"""
    try:
        with app.app_context():
            init_postgres_schema()
            logger.info("Application initialized successfully")

            mqtt_service.connect()
            logger.info("MQTT service started")

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise


init_app()

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("Shutting down application...")
        mqtt_service.disconnect()
        logger.info("Application stopped")
