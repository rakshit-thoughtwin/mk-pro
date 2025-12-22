# Slot Booking System API

A backend-only slot booking system built with Python, Django, and Django REST Framework (DRF). This system manages slot bookings per date with time segments, requiring admin approval before confirmation.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [API Response Format](#api-response-format)
- [API Endpoints](#api-endpoints)
- [Booking Flow](#booking-flow)
- [Admin Panel](#admin-panel)
- [Examples](#examples)

## Features

- **Date-based slot management**: Bookings are managed per date
- **Time segments**: Each date has 4 time segments (Morning, Noon, Evening, Night)
- **Slot capacity**: 10 slots per time segment
- **Admin approval workflow**: Bookings require admin approval before confirmation
- **Aadhaar integration**: Support for person details with Aadhaar information
- **SMS notifications**: Automated SMS notifications for booking status changes

## Setup

### Prerequisites

- Python 3.12+
- Django 6.0+
- Django REST Framework

### Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd /home/lenovo/Projects/MK_pro
   ```

2. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies** (if not already installed):
   ```bash
   pip install django djangorestframework
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

## API Response Format

**All API responses follow this strict format:**

```json
{
    "data": <object | list | null>,
    "status": <http_status_code>,
    "message": <string>,
    "error": <boolean>
}
```

- `data`: The actual response payload or empty object `{}` when not applicable
- `status`: HTTP status code (same as DRF response status)
- `message`: Human-readable message
- `error`: `true` for failures, `false` for success

## API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### 1. Get Available Slots

Get slot availability for a specific date.

**Endpoint:** `GET /api/slots/`

**Query Parameters:**
- `date` (required): Date in `YYYY-MM-DD` format

**Response Example (Success):**
```json
{
    "data": {
        "MORNING": 8,
        "NOON": 10,
        "EVENING": 5,
        "NIGHT": 10
    },
    "status": 200,
    "message": "Slot availability retrieved",
    "error": false
}
```

**Response Example (Error):**
```json
{
    "data": {},
    "status": 400,
    "message": "Date parameter is required",
    "error": true
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/slots/?date=2024-01-15"
```

**Python Example:**
```python
import requests

response = requests.get('http://localhost:8000/api/slots/', params={'date': '2024-01-15'})
print(response.json())
```

---

### 2. Create Booking (Checkout)

Create a new booking with PENDING status.

**Endpoint:** `POST /api/bookings/`

**Request Body:**
```json
{
    "booking_date": "2024-01-15",
    "time_segment": "MORNING",
    "primary_person_name": "John Doe",
    "primary_contact": "+919876543210",
    "persons": [
        {
            "name": "John Doe",
            "aadhaar": "123456789012",
            "aadhaar_file": null,
            "identity_details": "Additional identity information"
        },
        {
            "name": "Jane Doe",
            "aadhaar": "987654321098",
            "aadhaar_file": null,
            "identity_details": ""
        }
    ]
}
```

**Field Descriptions:**
- `booking_date`: Date in `YYYY-MM-DD` format
- `time_segment`: One of `MORNING`, `NOON`, `EVENING`, `NIGHT`
- `primary_person_name`: Name of the primary booking person
- `primary_contact`: Contact number for SMS notifications (format: +919876543210)
- `persons`: Array of person objects (at least one required)
  - `name`: Person's full name
  - `aadhaar`: Aadhaar number (12 digits)
  - `aadhaar_file`: Optional file upload for Aadhaar document
  - `identity_details`: Optional additional identity information

**Response Example (Success):**
```json
{
    "data": {},
    "status": 201,
    "message": "Your request has been submitted",
    "error": false
}
```

**Response Example (Validation Error):**
```json
{
    "data": {
        "booking_date": ["This field is required."],
        "persons": ["At least one person is required."]
    },
    "status": 400,
    "message": "This field is required.",
    "error": true
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_date": "2024-01-15",
    "time_segment": "MORNING",
    "primary_person_name": "John Doe",
    "primary_contact": "+919876543210",
    "persons": [
        {
            "name": "John Doe",
            "aadhaar": "123456789012",
            "identity_details": "Passport: AB123456"
        }
    ]
  }'
```

**Python Example:**
```python
import requests

url = 'http://localhost:8000/api/bookings/'
data = {
    "booking_date": "2024-01-15",
    "time_segment": "MORNING",
    "primary_person_name": "John Doe",
    "primary_contact": "+919876543210",
    "persons": [
        {
            "name": "John Doe",
            "aadhaar": "123456789012",
            "identity_details": "Passport: AB123456"
        }
    ]
}

response = requests.post(url, json=data)
print(response.json())
```

**File Upload Example (with aadhaar_file):**
```python
import requests

url = 'http://localhost:8000/api/bookings/'
files = {
    'persons[0][aadhaar_file]': open('aadhaar.pdf', 'rb')
}
data = {
    "booking_date": "2024-01-15",
    "time_segment": "MORNING",
    "primary_person_name": "John Doe",
    "primary_contact": "+919876543210",
    "persons[0][name]": "John Doe",
    "persons[0][aadhaar]": "123456789012",
    "persons[0][identity_details]": "Passport: AB123456"
}

response = requests.post(url, data=data, files=files)
print(response.json())
```

---

### 3. List Bookings

Get a list of all bookings (optional endpoint).

**Endpoint:** `GET /api/bookings/`

**Response Example:**
```json
{
    "data": [
        {
            "id": 1,
            "booking_date": "2024-01-15",
            "time_segment": "MORNING",
            "status": "PENDING",
            "primary_person_name": "John Doe",
            "primary_contact": "+919876543210",
            "persons": [
                {
                    "name": "John Doe",
                    "aadhaar": "123456789012",
                    "aadhaar_file": null,
                    "identity_details": "Passport: AB123456"
                }
            ],
            "created_at": "2024-01-10T10:30:00Z"
        }
    ],
    "status": 200,
    "message": "Success",
    "error": false
}
```

---

### 4. Get Booking Details

Get details of a specific booking.

**Endpoint:** `GET /api/bookings/{id}/`

**Response Example:**
```json
{
    "data": {
        "id": 1,
        "booking_date": "2024-01-15",
        "time_segment": "MORNING",
        "status": "PENDING",
        "primary_person_name": "John Doe",
        "primary_contact": "+919876543210",
        "persons": [
            {
                "name": "John Doe",
                "aadhaar": "123456789012",
                "aadhaar_file": null,
                "identity_details": "Passport: AB123456"
            }
        ],
        "created_at": "2024-01-10T10:30:00Z"
    },
    "status": 200,
    "message": "Success",
    "error": false
}
```

---

## Booking Flow

### 1. Checkout Process

1. User calls the **Create Booking** endpoint with booking details
2. Booking is created with **PENDING** status
3. API responds with: `"Your request has been submitted"`
4. **Slots are NOT confirmed at this stage**

### 2. Admin Approval Process

1. Admin logs into Django Admin panel
2. Views booking list showing: `"Primary Person Name → qty(n)"`
3. Admin selects bookings and uses **Approve** or **Reject** action

### 3. Approval Logic

**When Admin Approves:**
- System checks slot availability atomically (with database locking)
- **If slots available:**
  - Booking status → `APPROVED`
  - Slot count reduced
  - SMS sent: *"Your booking is confirmed"*
- **If slots NOT available:**
  - Booking status → `REJECTED` (automatically)
  - SMS sent: *"Slots not available, booking rejected"*

**When Admin Rejects:**
- Booking status → `REJECTED`
- SMS sent: *"Your booking has been rejected"*

## Admin Panel

### Access

Navigate to: `http://localhost:8000/admin/`

Login with superuser credentials created during setup.

### Features

1. **Booking List View**
   - Displays: `"Primary Person Name → qty(n)"`
   - Shows: Booking date, time segment, status, created date
   - Filterable by: Status, booking date, time segment

2. **Admin Actions**
   - **Approve selected bookings**: Approves bookings (with slot availability check)
   - **Reject selected bookings**: Rejects bookings

3. **Inline Person Editing**
   - View and edit persons associated with each booking

### Usage

1. Go to **Bookings** section
2. Select one or more bookings
3. Choose action from dropdown: **Approve selected bookings** or **Reject selected bookings**
4. Click **Go**
5. System processes the action and sends SMS notifications

## Time Segments

The system supports 4 time segments per date:

- `MORNING`: Morning time slot
- `NOON`: Noon time slot
- `EVENING`: Evening time slot
- `NIGHT`: Night time slot

Each segment has a capacity of **10 slots**.

## Slot Availability

- Only **APPROVED** bookings count toward slot availability
- **PENDING** and **REJECTED** bookings do not reduce available slots
- Availability is calculated per date and time segment

## Error Handling

All errors follow the standard API response format:

```json
{
    "data": {
        "field_name": ["Error message"],
        "non_field_errors": ["General error message"]
    },
    "status": 400,
    "message": "Error message",
    "error": true
}
```

### Common Error Codes

- `400`: Bad Request (validation errors, missing parameters)
- `404`: Not Found (booking ID doesn't exist)
- `500`: Internal Server Error

## SMS Notifications

SMS notifications are sent via the Notification Service layer:

- **Booking Confirmed**: "Your booking is confirmed"
- **Booking Rejected (by admin)**: "Your booking has been rejected"
- **Booking Rejected (slots unavailable)**: "Slots not available, booking rejected"

*Note: SMS sending is currently mocked/abstracted. In production, integrate with an actual SMS provider.*

## Examples

### Complete Booking Flow Example

```python
import requests

BASE_URL = "http://localhost:8000/api/"

# 1. Check available slots
response = requests.get(f"{BASE_URL}slots/", params={"date": "2024-01-15"})
print("Available slots:", response.json())

# 2. Create booking
booking_data = {
    "booking_date": "2024-01-15",
    "time_segment": "MORNING",
    "primary_person_name": "John Doe",
    "primary_contact": "+919876543210",
    "persons": [
        {
            "name": "John Doe",
            "aadhaar": "123456789012",
            "identity_details": "Passport: AB123456"
        },
        {
            "name": "Jane Doe",
            "aadhaar": "987654321098",
            "identity_details": ""
        }
    ]
}

response = requests.post(f"{BASE_URL}bookings/", json=booking_data)
result = response.json()
print("Booking created:", result)

# 3. Check booking status (if you have the booking ID)
booking_id = 1  # Replace with actual ID
response = requests.get(f"{BASE_URL}bookings/{booking_id}/")
print("Booking details:", response.json())
```

## Technical Notes

- **Atomic Operations**: Slot availability checks use `transaction.atomic()` and `select_for_update()` for thread-safe operations
- **Business Logic**: All business logic is in the service layer, not in views or admin classes
- **Validation**: Comprehensive validation for all input fields
- **File Uploads**: Aadhaar documents can be uploaded as files (stored in `media/aadhaar_docs/`)

## Support

For issues or questions, please refer to the codebase documentation or contact the development team.



