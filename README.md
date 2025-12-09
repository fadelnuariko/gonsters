# GONSTERS Backend - Industrial IoT Platform

![CI/CD Pipeline](https://github.com/YOUR_USERNAME/gonsters/actions/workflows/ci-cd.yml/badge.svg)

## Overview
Backend service for real-time industrial machine monitoring with sensor data ingestion, MQTT integration, and role-based access control.

## Features
- ✅ RESTful API for sensor data ingestion and retrieval
- ✅ PostgreSQL for machine metadata
- ✅ InfluxDB for time-series sensor data
- ✅ MQTT protocol support for real-time data
- ✅ JWT authentication with RBAC (Operator, Supervisor, Management)
- ✅ Redis caching with Cache-Aside pattern
- ✅ Structured JSON logging
- ✅ Docker containerization
- ✅ CI/CD with GitHub Actions

## Tech Stack
- **Backend**: Python, Flask
- **Databases**: PostgreSQL, InfluxDB
- **Cache**: Redis
- **Message Broker**: MQTT (Mosquitto)
- **Authentication**: JWT
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Clone repository
git clone <your-repo>
cd gonsters

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Local Development
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python run.py
```

## API Documentation

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Machines
- `GET /api/v1/machines` - Get all machines (Operator+)
- `POST /api/v1/machines` - Create machine (Supervisor+)
- `GET /api/v1/machines/{id}` - Get machine by ID (Operator+)

### Data
- `POST /api/v1/data/ingest` - Ingest sensor data (Operator+)
- `GET /api/v1/data/machine/{id}` - Query historical data (Operator+)

## Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest app/tests/test_auth.py
```

## CI/CD Pipeline
The GitHub Actions workflow includes:
1. **Code Quality**: Flake8, Black, Pylint
2. **Testing**: Unit tests with pytest
3. **Build**: Docker image build
4. **Security**: Trivy vulnerability scanning
5. **Deploy**: Automated deployment (on main branch)

## License
MIT
