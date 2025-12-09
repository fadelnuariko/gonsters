from app.database import get_postgres_connection, get_influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from app.config import config
from app.utils.logger import logger
from app.services.cache_service import cache_service, cache_aside
from datetime import datetime


class MachineRepository:
    """Repository for machine metadata operations"""

    @staticmethod
    @cache_aside(key_prefix="machines:all", ttl=600)
    def get_all_machines():
        """Get all machines from PostgreSQL with caching"""
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM machine_metadata ORDER BY id")
        machines = cursor.fetchall()
        cursor.close()
        conn.close()
        return machines

    @staticmethod
    @cache_aside(key_prefix="machine", ttl=600)
    def get_machine_by_id(machine_id):
        """Get machine by ID with caching"""
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM machine_metadata WHERE id = %s", (machine_id,))
        machine = cursor.fetchone()
        cursor.close()
        conn.close()
        return machine

    @staticmethod
    def create_machine(machine_data):
        """Create new machine and invalidate cache"""
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO machine_metadata (name, location, sensor_type, status)
            VALUES (%(name)s, %(location)s, %(sensor_type)s, %(status)s)
            RETURNING *
        """,
            machine_data,
        )
        machine = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        cache_service.invalidate_pattern("machines:*")
        cache_service.invalidate_pattern("machine:*")

        return machine


class SensorDataRepository:
    """Repository for sensor data operations with InfluxDB"""

    @staticmethod
    def write_sensor_data(data_points):
        """Write sensor data to InfluxDB"""
        client = None
        try:
            client = get_influxdb_client()
            write_api = client.write_api(write_options=SYNCHRONOUS)

            points = []
            for data_point in data_points:
                timestamp = data_point["timestamp"]
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

                point = (
                    Point("sensor_data")
                    .tag("machine_id", str(data_point["machine_id"]))
                    .tag("sensor_type", data_point["sensor_type"])
                    .tag("unit", data_point["unit"])
                    .field("value", float(data_point["value"]))
                    .time(timestamp)
                )
                points.append(point)

            write_api.write(
                bucket=config.INFLUXDB_BUCKET, org=config.INFLUXDB_ORG, record=points
            )

            logger.info(f"Successfully wrote {len(points)} data points to InfluxDB")
            return True

        except Exception as e:
            logger.error(f"Error writing to InfluxDB: {e}", exc_info=True)
            raise
        finally:
            if client:
                client.close()

    @staticmethod
    def query_sensor_data(machine_id, start_time, end_time, interval="1h"):
        """Query sensor data from InfluxDB"""
        client = None
        try:
            client = get_influxdb_client()
            query_api = client.query_api()

            query = f"""
                from(bucket: "{config.INFLUXDB_BUCKET}")
                  |> range(start: {start_time}, stop: {end_time})
                  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
                  |> filter(fn: (r) => r["machine_id"] == "{machine_id}")
                  |> filter(fn: (r) => r["_field"] == "value")
                  |> aggregateWindow(every: {interval}, fn: mean, createEmpty: false)
                  |> yield(name: "mean")
            """

            logger.debug(f"Executing InfluxDB query: {query}")

            result = query_api.query(query, org=config.INFLUXDB_ORG)

            results = []
            for table in result:
                for record in table.records:
                    results.append(
                        {
                            "time": (
                                record.get_time().isoformat()
                                if record.get_time()
                                else None
                            ),
                            "machine_id": record.values.get("machine_id"),
                            "sensor_type": record.values.get("sensor_type"),
                            "unit": record.values.get("unit"),
                            "value": record.get_value(),
                            "field": record.get_field(),
                        }
                    )

            logger.info(f"Retrieved {len(results)} data points from InfluxDB")
            return results

        except Exception as e:
            logger.error(f"Error querying InfluxDB: {e}", exc_info=True)
            raise
        finally:
            if client:
                client.close()
