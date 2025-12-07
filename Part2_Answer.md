# Part 2: Industrial Protocols & Security

## Question 2.1: MQTT Protocol Implementation

### 1. Code Flow: Connecting to Broker and Subscribing to Topic

**Pseudocode:**

```
FUNCTION connect_to_mqtt_broker():
    1. Initialize MQTT client instance
    2. Register callback handlers:
       - on_connect: Triggered when connection established
       - on_message: Triggered when message received
       - on_disconnect: Triggered when connection lost
    3. Connect to broker at MQTT_BROKER:MQTT_PORT with keepalive=60
    4. Start background network loop (non-blocking)
    5. Return control to main application

FUNCTION on_connect(client, userdata, flags, return_code):
    1. IF return_code == 0 (success):
       a. Set connection status to True
       b. Subscribe to topic: "factory/+/machine/+/telemetry"
          - '+' is single-level wildcard
          - Matches: factory/A/machine/1/telemetry, factory/B/machine/5/telemetry
       c. Log successful connection and subscription
    2. ELSE:
       a. Log connection failure with return code

FUNCTION on_message(client, userdata, message):
    1. Parse topic to extract metadata:
       - Split topic by '/' delimiter
       - Extract factory_id from position [1]
       - Extract machine_id from position [3]
    
    2. Decode message payload:
       - Convert bytes to UTF-8 string
       - Parse JSON string to dictionary
    
    3. Validate payload structure:
       - Check required fields: sensor_type, value, timestamp, unit
       - IF validation fails:
         * Log warning
         * Discard message and return
    
    4. Transform data for storage:
       - Create data_point dictionary with:
         * machine_id (integer)
         * sensor_type (string)
         * value (float)
         * timestamp (ISO 8601)
         * unit (string)
    
    5. Persist to database:
       - Call SensorDataRepository.write_sensor_data([data_point])
       - Write to InfluxDB time-series database
    
    6. Log success or handle exceptions:
       - JSONDecodeError: Invalid JSON format
       - ValueError: Invalid data types
       - DatabaseError: Failed to write to InfluxDB

FUNCTION on_disconnect(client, userdata, return_code):
    1. Set connection status to False
    2. IF return_code != 0 (unexpected disconnect):
       - Log warning with return code
       - Client will automatically attempt reconnection
```

**Implementation Reference:** `app/services/mqtt_service.py`

**Key Implementation Details:**

```python
# Connection
self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, keepalive=60)
self.client.loop_start()  # Non-blocking background thread

# Subscription with wildcard
topic = "factory/+/machine/+/telemetry"
client.subscribe(topic)

# Message handling
payload = json.loads(msg.payload.decode('utf-8'))
data_point = {
    'machine_id': int(payload.get('machine_id')),
    'sensor_type': payload['sensor_type'],
    'value': float(payload['value']),
    'timestamp': payload['timestamp'],
    'unit': payload['unit']
}
SensorDataRepository.write_sensor_data([data_point])
```

---

### 2. Comparison: WebSocket vs MQTT

#### Fundamental Difference in Connection Handling

**MQTT:**
- **Connection Model:** Client connects to a central broker (pub/sub architecture)
- **Communication Pattern:** Decoupled - publishers and subscribers don't know about each other
- **Message Flow:** Client → Broker → Subscriber(s)
- **State Management:** Broker maintains session state and message queues
- **Quality of Service:** Built-in QoS levels (0, 1, 2) guarantee message delivery
- **Reconnection:** Automatic with session persistence and queued messages

**WebSocket:**
- **Connection Model:** Direct peer-to-peer connection between client and server
- **Communication Pattern:** Coupled - client and server communicate directly
- **Message Flow:** Client ↔ Server (bidirectional)
- **State Management:** Application must implement state management
- **Quality of Service:** No built-in guarantees - application layer responsibility
- **Reconnection:** Manual implementation required

#### When to Choose MQTT as Data Source for Real-Time Dashboard

**Scenario 1: Unreliable Network Conditions**
```
Factory Environment:
- Industrial WiFi with intermittent connectivity
- Mobile devices moving between access points
- Occasional network congestion

Why MQTT:
✅ QoS 1/2 ensures no data loss during brief disconnections
✅ Broker queues messages while client reconnects
✅ Automatic reconnection with session resumption

Why NOT WebSocket:
❌ Messages lost during disconnection
❌ Must implement custom queuing and retry logic
❌ No guaranteed delivery mechanism
```

**Scenario 2: Multiple Concurrent Subscribers**
```
Dashboard Requirements:
- Web dashboard for operators
- Mobile app for supervisors
- Analytics service for data processing
- All need same real-time sensor data

Why MQTT:
✅ Broker handles fan-out to N subscribers efficiently
✅ Single publish reaches all subscribers
✅ New subscribers get retained messages (last known state)

Why NOT WebSocket:
❌ Server must maintain N separate WebSocket connections
❌ Must implement custom message routing/broadcasting
❌ Higher server resource consumption
```

**Scenario 3: Bandwidth-Constrained Environments**
```
IoT Deployment:
- 100+ machines sending data every 5 seconds
- Cellular/satellite connectivity
- Limited bandwidth budget

Why MQTT:
✅ Minimal protocol overhead (2-byte header)
✅ Binary protocol optimized for IoT
✅ ~93% less bandwidth than WebSocket for small messages

Why NOT WebSocket:
❌ HTTP-based framing adds overhead
❌ Text-based protocol (unless using binary frames)
❌ Higher bandwidth consumption at scale
```

**Scenario 4: Hierarchical Data Organization**
```
Data Structure:
- Multiple factories, each with multiple machines
- Each machine has multiple sensors
- Dashboard needs flexible subscription patterns

Why MQTT:
✅ Topic hierarchy: factory/A/machine/1/temperature
✅ Wildcard subscriptions: factory/+/machine/+/# (all data)
✅ Selective subscriptions: factory/A/machine/1/# (one machine)

Why NOT WebSocket:
❌ No built-in topic/routing system
❌ Must implement custom filtering logic
❌ Client receives all data and filters locally
```

**Practical Decision Matrix:**

| Requirement | Choose MQTT | Choose WebSocket |
|-------------|-------------|------------------|
| IoT device-to-server communication | ✅ Yes | ❌ No |
| Unreliable network | ✅ Yes | ❌ No |
| Multiple subscribers to same data | ✅ Yes | ⚠️ Complex |
| Guaranteed message delivery | ✅ Yes | ❌ No |
| Low bandwidth | ✅ Yes | ❌ No |
| Browser-based real-time updates | ⚠️ MQTT over WS | ✅ Yes |
| Direct client-server RPC | ❌ No | ✅ Yes |
| Simple request-response | ❌ No | ✅ Yes |

**Our Implementation Choice:**

```python
# run.py - MQTT for device ingestion
mqtt_service.connect()  # Handles all 100+ machines with single connection

# Benefits in our system:
# 1. QoS 1 ensures no sensor data loss
# 2. Broker handles multiple backend services subscribing
# 3. Minimal bandwidth for high-frequency sensor updates
# 4. Automatic reconnection for industrial environment
```

**Conclusion:**

For **real-time dashboard data source**, choose MQTT when:
- Data originates from IoT devices/sensors
- Network reliability is a concern
- Multiple services need the same data
- Bandwidth efficiency is critical
- Guaranteed delivery is required

Use WebSocket when:
- Direct browser-to-server communication
- Simple request-response patterns
- No need for pub/sub architecture
- Reliable network environment

---

## Question 2.2: Security and Authentication (RBAC)

### JWT Design

**JWT Payload Structure:**

```json
{
  "user_id": 1,
  "username": "john_manager",
  "role": "Management",
  "exp": 1702045200,
  "iat": 1702043400,
  "type": "access"
}
```

**Required Fields for RBAC:**

| Field | Purpose | Why Required |
|-------|---------|--------------|
| `user_id` | Unique user identifier | Audit logging, user-specific operations, token revocation |
| `username` | Human-readable identifier | Logging, display, audit trails |
| `role` | User's role (Operator/Supervisor/Management) | **CRITICAL** - Core of RBAC authorization |
| `exp` | Expiration timestamp | Security - prevents token reuse, forces re-authentication |
| `iat` | Issued at timestamp | Security - token lifecycle tracking, replay attack detection |
| `type` | Token type (access/refresh) | Distinguishes between token types in multi-token systems |

**Implementation:**

```python
# app/services/auth_service.py

@staticmethod
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config.JWT_EXPIRATION_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        config.JWT_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM  # HS256
    )
    
    return encoded_jwt
```

**Configuration:**

```python
# app/config.py
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-this-secret-key')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_MINUTES = 30
```

---

### Authorization Flow: Management Role Accessing Sensitive Endpoint

**Scenario:** User with Management role accesses `POST /api/v1/config/update`

#### Step 1: User Login

**Request:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "john_manager",
  "password": "SecurePass123!"
}
```

**Process:**
```python
# app/controllers/auth_controller.py

1. Validate input schema (username, password)
2. Fetch user from database by username
3. Verify password hash using bcrypt
4. Create JWT token with user data:
   {
     "user_id": 1,
     "username": "john_manager",
     "role": "Management"
   }
5. Return token to client
```

**Response:**
```json
{
  "status": "success",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "user": {
    "username": "john_manager",
    "role": "Management"
  }
}
```

#### Step 2: Client Stores Token

```javascript
localStorage.setItem('access_token', response.access_token);
```

#### Step 3: Request to Protected Endpoint

**Request:**
```http
POST /api/v1/config/update
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "setting": "data_retention_days",
  "value": 90
}
```

#### Step 4: Token Validation (@token_required)

```python
# app/api/auth.py

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 1. Extract token from Authorization header
        token = request.headers.get('Authorization', '').split(" ")[1]
        
        # 2. Check if token exists
        if not token:
            return {"status": "error", "message": "Token is missing"}, 401
        
        # 3. Decode and verify token
        try:
            payload = AuthService.decode_token(token)
            # Verifies: signature, expiration, algorithm
        except JWTError:
            return {"status": "error", "message": "Token is invalid or expired"}, 401
        
        # 4. Attach user info to request context
        request.current_user = payload
        # {
        #   "user_id": 1,
        #   "username": "john_manager",
        #   "role": "Management",
        #   "exp": 1702045200,
        #   "iat": 1702043400
        # }
        
        return f(*args, **kwargs)
    
    return decorated
```

#### Step 5: Role Authorization (@role_required)

```python
# app/api/auth.py

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # 1. Get user's role from JWT payload
            user_role = request.current_user.get('role')  # "Management"
            
            # 2. Check permission using role hierarchy
            if not AuthService.check_permission(user_role, required_role):
                return {
                    "status": "error",
                    "message": f"Access denied. Required role: {required_role} or higher",
                    "your_role": user_role
                }, 403
            
            # 3. Permission granted
            return f(*args, **kwargs)
        
        return decorated
    return decorator
```

#### Step 6: Permission Check (Role Hierarchy)

```python
# app/services/auth_service.py

@staticmethod
def check_permission(user_role: str, required_role: str) -> bool:
    role_hierarchy = {
        'Operator': 1,
        'Supervisor': 2,
        'Management': 3
    }
    
    user_level = role_hierarchy.get(user_role, 0)      # 3
    required_level = role_hierarchy.get(required_role, 0)  # 3
    
    return user_level >= required_level  # 3 >= 3 = True ✅
```

**Permission Matrix:**

| User Role | Operator Endpoints | Supervisor Endpoints | Management Endpoints |
|-----------|-------------------|---------------------|---------------------|
| Operator | ✅ (1 >= 1) | ❌ (1 < 2) | ❌ (1 < 3) |
| Supervisor | ✅ (2 >= 1) | ✅ (2 >= 2) | ❌ (2 < 3) |
| Management | ✅ (3 >= 1) | ✅ (3 >= 2) | ✅ (3 >= 3) |

#### Step 7: Execute Endpoint Logic

```python
# app/api/routes.py

@api_bp.route('/config/update', methods=['POST'])
@token_required
@role_required('Management')
def update_config():
    # User is authenticated and authorized
    return {
        "status": "success",
        "message": "Configuration updated successfully",
        "updated_by": request.current_user.get('username'),
        "role": request.current_user.get('role')
    }, 200
```

**Success Response:**
```json
{
  "status": "success",
  "message": "Configuration updated successfully",
  "updated_by": "john_manager",
  "role": "Management"
}
```

---

### Complete Authorization Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│ 1. LOGIN                                                 │
│    POST /api/v1/auth/login                               │
│    Verify credentials → Generate JWT → Return token      │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 2. CLIENT STORES TOKEN                                   │
│    localStorage.setItem('access_token', token)           │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 3. REQUEST TO PROTECTED ENDPOINT                         │
│    POST /api/v1/config/update                            │
│    Authorization: Bearer <token>                         │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 4. @token_required DECORATOR                             │
│    ✓ Extract token from header                           │
│    ✓ Decode JWT (verify signature & expiration)         │
│    ✓ Attach payload to request.current_user             │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 5. @role_required('Management') DECORATOR                │
│    ✓ Get user_role from request.current_user            │
│    ✓ Check role hierarchy (Management >= Management)    │
│    ✓ Grant access if permission check passes            │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 6. EXECUTE ENDPOINT LOGIC                                │
│    ✓ Update configuration                                │
│    ✓ Log action with user info                          │
│    ✓ Return success response                             │
└──────────────────────────────────────────────────────────┘
```

---

### Error Scenarios

**Scenario A: Operator tries to access Management endpoint**

```python
User: operator_user (Role: Operator)
Endpoint: POST /api/v1/config/update (Requires: Management)

Permission Check:
user_level = 1 (Operator)
required_level = 3 (Management)
1 >= 3 = False ❌

Response:
{
  "status": "error",
  "message": "Access denied. Required role: Management or higher",
  "your_role": "Operator"
}
HTTP Status: 403 Forbidden
```

**Scenario B: Expired Token**

```python
Token expired (exp < current_time)

Response:
{
  "status": "error",
  "message": "Token is invalid or expired"
}
HTTP Status: 401 Unauthorized
```

**Scenario C: Missing Token**

```python
No Authorization header

Response:
{
  "status": "error",
  "message": "Token is missing"
}
HTTP Status: 401 Unauthorized
```

---

### Security Best Practices Implemented

1. ✅ Password Hashing - bcrypt with 12 rounds
2. ✅ JWT Expiration - 30-minute token lifetime
3. ✅ Role Hierarchy - Prevents privilege escalation
4. ✅ Audit Logging - All access attempts logged
5. ✅ Secure Headers - Bearer token in Authorization header
6. ✅ Input Validation - Marshmallow schemas
7. ✅ Generic Error Messages - No information leakage
8. ✅ HTTPS Ready - Token transmission over secure channel (production)
