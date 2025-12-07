import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password123')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'gonsters_metadata')

    INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
    INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'my-super-secret-token')
    INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'myorg')
    INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'sensors')

    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

    MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
    MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-this-secret-key')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_MINUTES = int(os.getenv('JWT_EXPIRATION_MINUTES', 30))

    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-this-secret-key')
    DEBUG = os.getenv('FLASK_ENV') == 'development'

config = Config()
