from app import create_app
from app.database import init_postgres_schema
from app.utils.logger import logger

app = create_app()

try:
    with app.app_context():
        init_postgres_schema()
        logger.info("Application initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize application: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
