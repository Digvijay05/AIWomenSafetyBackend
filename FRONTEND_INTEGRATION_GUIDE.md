# Frontend Integration Guide

**Version:** 1.0  
**Target:** Flutter Developers  
**Backend:** AI-Powered Women Safety Platform

This guide explains how to integrate Flutter mobile applications with the backend API. All APIs are JSON-only and follow a consistent response format.

---

## 1. System Overview

### What This Backend Is

The backend is an **autonomous safety agent** that monitors user journeys in real-time, analyzes risks, and automatically decides when to escalate alerts. It shifts safety from reactive (manual SOS buttons) to **proactive** (automatic risk detection and escalation).

### What This Backend Is Not

- **Not a passive database**: The backend analyzes data and makes decisions
- **Not a simple CRUD API**: It includes intelligence and autonomous actions
- **Not frontend-controlled**: You don't decide risk levels or escalate manually

### Key Concepts

**Proactive Safety**
- Traditional systems: User presses SOS → Alert sent
- This system: Backend continuously analyzes telemetry → Automatically escalates when risk detected

**Autonomous Agent**
- The backend makes decisions based on risk analysis
- It creates alerts, notifies police, and suggests safe routes automatically
- Your Flutter app sends telemetry and receives decisions/actions

**JSON-Only Communication**
- All requests use `Content-Type: application/json`
- No form-data, no multipart, no file uploads
- All responses follow a consistent envelope format

---

## 2. High-Level Data Flow

```
User Opens App
  ↓
Register/Login → Get JWT Token
  ↓
Start Journey → Get journey_id
  ↓
Send Telemetry (every 5-30 seconds)
  ↓
Backend Analyzes → Returns Risk Assessment + Decision
  ↓
Frontend Reacts (show warning, update UI)
  ↓
Backend Executes Actions (auto-creates alerts if needed)
  ↓
End Journey → Cleanup
```

### Flow Breakdown

**Frontend Sends:**
- User credentials (login/register)
- Journey start/end information
- Telemetry data (location, speed, battery, etc.)

**Backend Decides:**
- Risk level based on telemetry
- Appropriate action (monitor, warn, escalate)
- When to create alerts

**Frontend Receives:**
- Risk assessments with confidence scores
- Decision actions (what the backend is doing)
- Alerts (if auto-created)
- Error messages (if something goes wrong)

---

## 3. Authentication Flow

### Registration

**Endpoint:** `POST /api/users/register`

**Purpose:** Create a new user account

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "Jane Doe",
  "phone_number": "+1234567890",
  "role": "user"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "507f1f77bcf86cd799439011",
      "email": "user@example.com",
      "full_name": "Jane Doe",
      "role": "user"
    },
    "message": "User registered successfully"
  },
  "error": null
}
```

**Note:** Role defaults to "user". Use "police" only for police dashboard apps.

---

### Login

**Endpoint:** `POST /api/users/login`

**Purpose:** Authenticate and receive JWT token

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Headers:** `Content-Type: application/json`

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "507f1f77bcf86cd799439011",
      "email": "user@example.com",
      "full_name": "Jane Doe",
      "role": "user"
    }
  },
  "error": null
}
```

**JWT Storage:**
- Store `access_token` securely (use `flutter_secure_storage` or similar)
- Token expires after 30 minutes (default)
- Include token in all authenticated requests

**Common Mistakes:**
- Using form-data instead of JSON
- Not storing token securely
- Forgetting to refresh token before expiration

---

### Using JWT Token

**Authorization Header:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**All subsequent requests require this header** (except register/login).

---

### Get Current User

**Endpoint:** `GET /api/users/me`

**Purpose:** Retrieve current authenticated user profile

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "role": "user",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "error": null
}
```

---

## 4. Journey Lifecycle APIs

### Start Journey

**Endpoint:** `POST /api/journeys/start`

**Purpose:** Begin tracking a new journey

**When to Call:** When user starts traveling (tap "Start Journey" button)

**Request:**
```json
{
  "start_location": {
    "lat": 23.0225,
    "lng": 72.5714
  },
  "start_time": "2024-01-15T10:30:00Z",
  "destination": {
    "lat": 23.0300,
    "lng": 72.5800
  },
  "expected_duration": 15
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "journey": {
      "id": "507f191e810c19729de860ea",
      "user_id": "507f1f77bcf86cd799439011",
      "start_time": "2024-01-15T10:30:00Z",
      "start_location": {"lat": 23.0225, "lng": 72.5714},
      "status": "active",
      "destination": {"lat": 23.0300, "lng": 72.5800},
      "expected_duration": 15
    },
    "message": "Journey started successfully"
  },
  "error": null
}
```

**Important:** Save `journey.id` immediately. You'll need it for all subsequent telemetry updates.

**Common Mistakes:**
- Not storing journey_id
- Using incorrect coordinate format
- Forgetting destination (optional but recommended)

---

### Send Telemetry

**Endpoint:** `POST /api/journeys/telemetry`

**Purpose:** Update journey with current location and sensor data

**When to Call:** Every 5-30 seconds while journey is active

**Request:**
```json
{
  "journey_id": "507f191e810c19729de860ea",
  "timestamp": "2024-01-15T10:30:15Z",
  "location": {
    "lat": 23.0230,
    "lng": 72.5720
  },
  "speed": 1.2,
  "movement_state": "walking",
  "battery_level": 78,
  "altitude": 45.5,
  "accuracy": 10.0
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "telemetry_added": true,
    "risk_assessment": {
      "risk_level": "MEDIUM",
      "confidence": 0.45,
      "factors": ["night_time"],
      "timestamp": "2024-01-15T10:30:15Z"
    },
    "decision": {
      "action": "warning_notification",
      "message": "Elevated risk (MEDIUM) detected with factors: night_time. User notified.",
      "timestamp": "2024-01-15T10:30:15Z"
    },
    "action_result": {
      "action": "alert_creation",
      "executed": true,
      "alert_id": "507f1f77bcf86cd799439012"
    }
  },
  "error": null
}
```

**Critical:** This endpoint triggers automatic risk analysis and decision-making. The backend may automatically create alerts without you asking.

**Update Frequency:**
- **Recommended:** Every 10-15 seconds during active journey
- **Minimum:** Every 30 seconds
- **Maximum:** Every 5 seconds (to avoid battery drain)

**Offline Behavior:**
- Store telemetry locally if offline
- Retry when connection restored (backend handles duplicates)

**Common Mistakes:**
- Sending telemetry too frequently (wastes battery)
- Not including required fields (journey_id, location, speed, movement_state, battery_level)
- Using wrong timestamp format (must be ISO 8601)

---

### Resume Journey

**Endpoint:** `POST /api/journeys/resume`

**Purpose:** Resume a paused journey (e.g., after app restart)

**When to Call:** When app restarts and an active journey exists

**Request:**
```json
{
  "journey_id": "507f191e810c19729de860ea",
  "resume_time": "2024-01-15T10:35:00Z",
  "current_location": {
    "lat": 23.0250,
    "lng": 72.5740
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "journey_id": "507f191e810c19729de860ea",
    "message": "Journey resumed successfully"
  },
  "error": null
}
```

**Common Mistakes:**
- Trying to resume a completed journey
- Using wrong journey_id

---

### End Journey

**Endpoint:** `POST /api/journeys/end`

**Purpose:** Complete journey and stop tracking

**When to Call:** When user reaches destination or cancels journey

**Request:**
```json
{
  "journey_id": "507f191e810c19729de860ea",
  "end_time": "2024-01-15T10:45:00Z",
  "end_location": {
    "lat": 23.0300,
    "lng": 72.5800
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "journey_id": "507f191e810c19729de860ea",
    "message": "Journey ended successfully"
  },
  "error": null
}
```

**Important:** After ending, stop sending telemetry for this journey_id.

---

## 5. Telemetry Contract

### Required Fields

All telemetry requests **must** include:

- `journey_id` (string): The journey ID from start journey response
- `timestamp` (ISO 8601 datetime): Current timestamp
- `location` (object): Current GPS coordinates
  - `lat` (float): Latitude (-90 to 90)
  - `lng` (float): Longitude (-180 to 180)
- `speed` (float): Speed in meters per second (>= 0)
- `movement_state` (enum): One of: `walking`, `running`, `driving`, `cycling`, `stationary`
- `battery_level` (integer): Battery percentage (0-100)

### Optional Fields

- `altitude` (float): Altitude in meters
- `accuracy` (float): GPS accuracy in meters

### Canonical Telemetry Payload

```json
{
  "journey_id": "507f191e810c19729de860ea",
  "timestamp": "2024-01-15T10:30:15.123Z",
  "location": {
    "lat": 23.0225,
    "lng": 72.5714
  },
  "speed": 1.2,
  "movement_state": "walking",
  "battery_level": 78,
  "altitude": 45.5,
  "accuracy": 10.0
}
```

### Update Frequency

- **Active journey:** Every 10-15 seconds
- **Low battery (< 20%):** Every 5 seconds (more frequent monitoring)
- **High risk detected:** Every 5 seconds (backend may request this)

### Idempotency

The backend handles duplicate telemetry requests. If you send the same telemetry twice, it will be accepted (helps with retry logic).

### Offline Behavior

1. **Store telemetry locally** if offline (use local database or shared preferences)
2. **Queue for retry** when connection restored
3. **Send queued telemetry** with original timestamps
4. Backend will accept even if timestamps are slightly old

**Important:** Don't skip telemetry points. Send all queued data when online.

---

## 6. Risk & Decision Feedback

### Risk Levels

The backend returns one of four risk levels:

- **LOW:** Normal monitoring, no action needed
- **MEDIUM:** Cautious monitoring, user may be notified
- **HIGH:** Elevated risk, user notified, closer monitoring
- **CRITICAL:** Immediate action, alerts escalated automatically

### Risk Assessment Response

```json
{
  "risk_assessment": {
    "risk_level": "HIGH",
    "confidence": 0.75,
    "factors": ["night_time", "isolated_area"],
    "timestamp": "2024-01-15T10:30:15Z"
  }
}
```

**Risk Factors:**
- `isolated_area`: User in isolated/unsafe location
- `night_time`: Journey during high-risk hours (9 PM - 6 AM)
- `route_deviation`: Significant deviation from planned route
- `speed_anomaly`: Unusual speed patterns
- `low_battery`: Battery below 10%

**Confidence Score:**
- Range: 0.0 to 1.0
- Higher confidence = more reliable risk assessment
- Use confidence to decide how prominently to display warnings

### Decision Actions

The backend automatically decides what to do:

- **`silent_monitoring`:** Continue normal monitoring (no UI change needed)
- **`warning_notification`:** Show warning to user (update UI, play sound)
- **`safe_route_suggestion`:** Suggest safer route (show on map)
- **`alert_escalation`:** Alert already created automatically (show alert confirmation)
- **`police_dashboard_event`:** Event sent to police dashboard (show confirmation)

### Frontend Response to Decisions

**For `warning_notification`:**
- Display warning message
- Change UI color (yellow/red)
- Play notification sound
- Show risk factors to user

**For `safe_route_suggestion`:**
- Show alternative route on map
- Allow user to accept/reject
- Update navigation if accepted

**For `alert_escalation`:**
- Show alert confirmation
- Display message: "Alert sent to emergency contacts"
- Do NOT create another alert (backend already did it)

**For `silent_monitoring`:**
- No UI change needed
- Continue normal monitoring display

### Important: Don't Override Backend Decisions

The backend decides when to escalate. Your app should:
- Display warnings when backend says `warning_notification`
- Show alerts when backend creates them (`alert_escalation`)
- Follow safe route suggestions (`safe_route_suggestion`)

**Do NOT:**
- Create your own alerts based on risk_level alone
- Override backend's decision to escalate
- Ignore backend's decision actions

---

## 7. Alerts & Escalation

### Automatic Alerts

The backend automatically creates alerts when:
- Risk level is CRITICAL with high confidence
- Risk level is HIGH for extended period
- Multiple risk factors detected simultaneously

**You don't need to create these alerts.** The backend handles it.

### Manual Alerts (SOS Button)

**Endpoint:** `POST /api/alerts`

**Purpose:** Allow user to manually trigger alert (SOS button)

**Request:**
```json
{
  "journey_id": "507f191e810c19729de860ea",
  "alert_type": "sos",
  "message": "Emergency! Need help immediately",
  "location": {
    "lat": 23.0225,
    "lng": 72.5714
  },
  "priority": "critical"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "alert": {
      "id": "507f1f77bcf86cd799439012",
      "journey_id": "507f191e810c19729de860ea",
      "alert_type": "sos",
      "message": "Emergency! Need help immediately",
      "location": {"lat": 23.0225, "lng": 72.5714},
      "priority": "critical",
      "status": "active",
      "created_at": "2024-01-15T10:30:20Z"
    },
    "message": "Alert created successfully"
  },
  "error": null
}
```

### Get Alerts

**Endpoint:** `GET /api/alerts`

**Purpose:** Retrieve alerts for current user

**Query Parameters:**
- `limit` (optional, default: 50): Maximum number of alerts

**Response:**
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "id": "507f1f77bcf86cd799439012",
        "journey_id": "507f191e810c19729de860ea",
        "alert_type": "automated_alert",
        "message": "Critical risk detected",
        "location": {"lat": 23.0225, "lng": 72.5714},
        "priority": "high",
        "status": "active",
        "created_at": "2024-01-15T10:30:20Z"
      }
    ]
  },
  "error": null
}
```

### Police Dashboard

For police dashboard apps (role: "police" or "admin"):

**Endpoint:** `GET /api/dashboard/alerts`

**Purpose:** Get high-priority alerts for police response

**Response:** Same format as GET /api/alerts, but filtered for high/critical priority unresolved alerts.

---

## 8. Error Handling & Status Codes

### Response Envelope Format

All responses follow this structure:

**Success:**
```json
{
  "success": true,
  "data": { /* response data */ },
  "error": null
}
```

**Error:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Could not validate credentials"
  }
}
```

### Common Error Codes

- **`UNAUTHORIZED`** (401): Invalid or missing JWT token
  - Solution: Re-login to get new token

- **`FORBIDDEN`** (403): Not authorized for this resource
  - Solution: Check user role or resource ownership

- **`NOT_FOUND`** (404): Resource doesn't exist
  - Solution: Check journey_id, alert_id, etc.

- **`VALIDATION_ERROR`** (422): Invalid request format
  - Solution: Check JSON schema, required fields

- **`BAD_REQUEST`** (400): Invalid request data
  - Solution: Check request payload

- **`INTERNAL_ERROR`** (500): Backend error
  - Solution: Retry request, contact support if persists

- **`SERVICE_UNAVAILABLE`** (503): Backend temporarily unavailable
  - Solution: Retry with exponential backoff

### Retry Strategy

**For 5xx errors (500, 503):**
- Retry immediately (may be transient)
- If fails again, wait 1 second, retry
- If fails again, wait 2 seconds, retry
- If fails again, wait 4 seconds, retry
- Maximum 3 retries

**For 4xx errors (400, 401, 403, 404, 422):**
- Do NOT retry (client error)
- Show error message to user
- For 401: Re-login user

**For network errors:**
- Queue request for retry when online
- Store telemetry locally
- Resume when connection restored

---

## 9. Environment & URLs

### Base URLs

**Local Development:**
```
http://localhost:8000
```

**Docker (local):**
```
http://localhost:8000
```

**Ngrok (demo/testing):**
```
https://abc123.ngrok-free.app
```

### API Endpoints

All endpoints are prefixed with `/api`:

- Authentication: `/api/users/*`
- Journeys: `/api/journeys/*`
- Alerts: `/api/alerts/*`
- Dashboard: `/api/dashboard/*`

### Environment Configuration in Flutter

Create a config file:

```dart
// lib/config/api_config.dart

class ApiConfig {
  // Development
  static const String localBaseUrl = 'http://localhost:8000';
  
  // Ngrok (for demo/testing)
  static const String ngrokBaseUrl = 'https://your-ngrok-url.ngrok-free.app';
  
  // Production (if deployed)
  static const String productionBaseUrl = 'https://api.yourdomain.com';
  
  // Select active URL
  static const String baseUrl = kDebugMode 
    ? ngrokBaseUrl  // Use ngrok for Flutter testing
    : productionBaseUrl;
  
  // Full API URL
  static String get apiUrl => '$baseUrl/api';
}
```

### Switching Environments

1. **Local Testing:** Use `localhost` (requires emulator/device on same network)
2. **Ngrok Testing:** Use ngrok URL (works from any network)
3. **Production:** Update to production URL when deployed

**Note:** Ngrok URLs change on restart. Update `ngrokBaseUrl` when ngrok restarts.

### Health Check

**Endpoint:** `GET /health`

**Purpose:** Verify backend is running

**No authentication required.**

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected"
  },
  "error": null
}
```

Use this on app startup to verify connectivity.

---

## 10. Best Practices for Flutter Developers

### Do's

**Authentication:**
- Store JWT token securely (`flutter_secure_storage`)
- Refresh token before expiration (check expiry time)
- Include token in all authenticated requests
- Handle 401 errors by redirecting to login

**Telemetry:**
- Send telemetry every 10-15 seconds (not more frequent)
- Store telemetry locally if offline
- Retry failed telemetry when online
- Include all required fields (journey_id, location, speed, movement_state, battery_level)

**Error Handling:**
- Always check `success` field in response
- Handle network errors gracefully
- Show user-friendly error messages
- Retry 5xx errors with exponential backoff
- Don't retry 4xx errors

**Battery Optimization:**
- Reduce telemetry frequency if battery < 20%
- Stop GPS when journey ended
- Batch telemetry updates if possible (though backend prefers regular intervals)

**Network:**
- Check network connectivity before sending requests
- Queue requests when offline
- Resume sending when connection restored
- Show offline indicator in UI

**UI/UX:**
- Display risk levels with appropriate colors (green/yellow/red)
- Show warning messages when backend returns `warning_notification`
- Display alert confirmations when backend creates alerts
- Update UI based on decision actions, not just risk levels

### Don'ts

**Authentication:**
- Don't store passwords or tokens in plain text
- Don't send token in URL parameters (use headers)
- Don't hardcode tokens in source code

**Telemetry:**
- Don't send telemetry more frequently than every 5 seconds
- Don't skip required fields
- Don't use wrong timestamp format (must be ISO 8601)
- Don't create your own alerts based on risk_level alone

**Decision Making:**
- Don't override backend decisions
- Don't create alerts when backend already created them
- Don't ignore backend's decision actions
- Don't try to calculate risk levels in Flutter (backend does this)

**Network:**
- Don't retry 4xx errors automatically
- Don't send requests if network unavailable (queue them)
- Don't block UI thread on network calls

**Security:**
- Don't log JWT tokens to console
- Don't expose API keys or secrets
- Don't use HTTP in production (use HTTPS)

### Common Pitfalls

**1. Forgetting journey_id**
- Save journey_id immediately after starting journey
- Use it in all telemetry requests

**2. Wrong timestamp format**
- Use ISO 8601: `2024-01-15T10:30:15.123Z`
- Include timezone (Z for UTC)

**3. Sending telemetry too frequently**
- Backend accepts frequent requests but wastes battery
- Stick to 10-15 second intervals

**4. Not handling offline scenarios**
- Always queue telemetry when offline
- Retry when connection restored

**5. Ignoring decision actions**
- Backend tells you what it's doing via `decision.action`
- Update UI based on actions, not just risk levels

**6. Creating duplicate alerts**
- Backend creates alerts automatically
- Check `action_result.alert_id` to see if alert was created
- Don't create another alert if one already exists

### Security Notes

**JWT Token Handling:**
- Store in secure storage (`flutter_secure_storage`)
- Don't log tokens to console
- Refresh before expiration
- Clear token on logout

**API Communication:**
- Always use HTTPS (never HTTP)
- Validate SSL certificates
- Don't skip certificate validation

**Sensitive Data:**
- Don't log user passwords
- Don't store passwords in plain text
- Don't expose API endpoints in logs

---

## Quick Reference

### Endpoint Summary

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/api/users/register` | Register user | No |
| POST | `/api/users/login` | Login | No |
| GET | `/api/users/me` | Get current user | Yes |
| POST | `/api/journeys/start` | Start journey | Yes |
| POST | `/api/journeys/telemetry` | Send telemetry | Yes |
| POST | `/api/journeys/resume` | Resume journey | Yes |
| POST | `/api/journeys/end` | End journey | Yes |
| GET | `/api/journeys` | List journeys | Yes |
| POST | `/api/alerts` | Create alert | Yes |
| GET | `/api/alerts` | List alerts | Yes |
| GET | `/api/dashboard/alerts` | Police alerts | Yes (police/admin) |
| GET | `/health` | Health check | No |

### Response Format

All responses:
```json
{
  "success": boolean,
  "data": object | null,
  "error": {
    "code": string,
    "message": string
  } | null
}
```

### Request Headers

**All authenticated requests:**
```
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

**Unauthenticated requests (register/login):**
```
Content-Type: application/json
```

---

## Support

For backend-specific questions or issues, contact the backend team. This guide covers the API contract from a frontend perspective.

**Remember:** The backend is an autonomous agent. Send telemetry, receive decisions, and react accordingly. Don't try to outsmart the backend's risk analysis and decision-making.
