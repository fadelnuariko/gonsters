# Back End Developer

------------------------------------------------------------------------

# GONSTERS Technical Skill Assessment

**Position:** Back End Developer

## Assessment Goal

This test is designed to evaluate the candidate's technical proficiency
in developing scalable and secure backend services, focusing on data
modeling, API implementation, industrial protocol integration, and the
application of DevOps best practices, directly addressing the core tasks
of the role.

------------------------------------------------------------------------

## General Instructions

-   **Time Allotment:** 3 days.\
-   **Answer Format:** Submit your answers in a clearly structured
    document (PDF) including relevant pseudocode or code snippets.\
-   **Code Quality:** We value conceptual clarity, efficient design, and
    the application of best practices (modularity, error handling,
    logging) over perfectly functioning code. Use your preferred
    framework (FastAPI/Flask).

------------------------------------------------------------------------

# Part 1: API Development & Data Modeling (Weight: 40%)

## Scenario: Real-Time Machine Data Ingestion

You are tasked with building a microservice responsible for receiving,
storing, and serving real-time sensor data from hundreds of industrial
machines.

------------------------------------------------------------------------

## Question 1.1: Database Design (Data Modeling)

### Machine Metadata (PostgreSQL)

Provide the basic SQL syntax (**CREATE TABLE**) for the
`machine_metadata` table. Include essential columns:\
- ID\
- Name\
- Location\
- Sensor Type\
- Status

### Sensor Data (InfluxDB)

Describe the InfluxDB schema (Tags, Fields, Measurement) you would use
to store sensor data:\
- Temperature\
- Pressure\
- Speed

### Optimization

Explain the strategies you would implement (Partitioning, Indexing, or
Data Retention) to ensure rapid query execution for weekly/monthly
historical analytics.

------------------------------------------------------------------------

## Question 1.2: RESTful API Design

Design the RESTful API endpoints for the data ingestion and retrieval
microservice.

### Ingestion Endpoint

Design the ideal JSON request body structure for the endpoint:\
`POST /api/v1/data/ingest`\
This receives a batch of sensor data from an industrial gateway.

### Retrieval Endpoint

Design the endpoint:\
`GET /api/v1/data/machine/{machine_id}`\
Specify the necessary query parameters:\
- start_time\
- end_time\
- interval

### Brief Implementation

Write a short pseudocode or code snippet for the
`POST /api/v1/data/ingest` endpoint, focusing specifically on **input
data validation before processing**.

------------------------------------------------------------------------

# Part 2: Industrial Protocols & Security (Weight: 35%)

## Scenario: Connectivity and Access Authentication

Your service must integrate with industrial protocols and ensure that
only authorized users can access the management dashboards.

------------------------------------------------------------------------

## Question 2.1: MQTT Protocol Implementation

1.  **Code Flow:**\
    Write pseudocode outlining the steps for:
    -   Connecting to the broker\
    -   Subscribing to topic: `factory/A/machine/+/telemetry`\
    -   Logic within the received message handler
2.  **Comparison:**\
    Explain the fundamental difference in connection handling between
    WebSocket and MQTT.\
    In the context of a real-time dashboard, when would you choose MQTT
    as the data source over WebSocket?

------------------------------------------------------------------------

## Question 2.2: Security and Authentication (RBAC)

Describe the authentication and authorization process you would
implement using **JWT** and **Role-Based Access Control (RBAC)**.

### JWT Design

Explain the JWT payload you would use. Which pieces of information (User
ID, Role, etc.) must be included to effectively support RBAC?

### Authorization Flow

Given the roles:\
- Operator\
- Supervisor\
- Management

Describe the step-by-step workflow (from login to request) when a user
with the **Management** role attempts to access a sensitive endpoint
such as:\
`POST /api/v1/config/update`

------------------------------------------------------------------------

# Part 3: Best Practices & Scalability (Weight: 25%)

## Scenario: 24/7 Deployment and Maintenance

The service must be maintainable, testable, and reliably deployed in a
continuous production environment.

------------------------------------------------------------------------

## Question 3.1: Logging and Caching

### Logging Structure

Provide an example of an effective logging structure (JSON or text
format) for the following event levels:\
- **DEBUG:** Successful incoming payload validation\
- **WARNING:** Temporary Redis connection loss, self-healing retry is
initiated\
- **ERROR:** Failed to persist data to PostgreSQL after 3 retry attempts

### Caching with Redis

Explain how you would use Redis for caching (e.g., machine metadata) to
reduce the load from repetitive queries to PostgreSQL/InfluxDB.\
Briefly describe the implementation of the **Cache-Aside Pattern** in
this context.

------------------------------------------------------------------------

## Question 3.2: Containerization & CI/CD

### Dockerfile

Write a brief Dockerfile draft for your Python FastAPI application.
Ensure the resulting image is small and secure (use multi-stage builds
if necessary).

### GitHub Actions

Describe **3 critical steps** (stages or jobs) that must be included in
your GitHub Actions workflow to ensure high-quality code is deployed to
production.

------------------------------------------------------------------------

# Table of Contents

-   GONSTERS Technical Skill Assessment\
-   Position: Back End Developer\
-   Assessment Goal\
-   General Instructions\
-   Part 1: API Development & Data Modeling (Weight: 40%)\
-   Part 2: Industrial Protocols & Security (Weight: 35%)\
-   Part 3: Best Practices & Scalability (Weight: 25%)
