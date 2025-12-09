from app.database import get_postgres_connection, get_influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from app.config import config
from app.utils.logger import logger
from app.services.cache_service import cache_service
from datetime import datetime


class MachineRepository:
    """Repository for machine metadata operations with caching"""

    @staticmethod
    def get_all_machines():
        """Get all machines from PostgreSQL with caching"""
        cache_key = "machines:all"

        cached_machines = cache_service.get(cache_key)
        if cached_machines is not None:
            logger.info("Retrieved machines from cache")
            return cached_machines

        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM machine_metadata ORDER BY id")
        machines = cursor.fetchall()
        cursor.close()
        conn.close()

        cache_service.set(cache_key, machines, ttl=300)
        logger.info("Retrieved machines from database and cached")

        return machines

    @staticmethod
    def get_machine_by_id(machine_id):
        """Get machine by ID with caching"""
        cache_key = f"machine:{machine_id}"

        cached_machine = cache_service.get(cache_key)
        if cached_machine is not None:
            logger.info(f"Retrieved machine {machine_id} from cache")
            return cached_machine

        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM machine_metadata WHERE id = %s", (machine_id,))
        machine = cursor.fetchone()
        cursor.close()
        conn.close()

        if machine:
            cache_service.set(cache_key, machine, ttl=300)
            logger.info(f"Retrieved machine {machine_id} from database and cached")

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

        cache_service.invalidate_machine_cache()
        logger.info(f"Created machine {machine['id']} and invalidated cache")

        return machine

    @staticmethod
    def update_machine(machine_id, machine_data):
        """Update machine and invalidate cache"""
        conn = get_postgres_connection()
        cursor = conn.cursor()

        update_fields = []
        values = []
        for key, value in machine_data.items():
            update_fields.append(f"{key} = %s")
            values.append(value)

        values.append(machine_id)

        query = f"""
            UPDATE machine_metadata
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """

        cursor.execute(query, values)
        machine = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        cache_service.invalidate_machine_cache(machine_id)
        logger.info(f"Updated machine {machine_id} and invalidated cache")

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
