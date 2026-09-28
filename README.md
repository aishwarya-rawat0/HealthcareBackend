# Healthcare Backend

A REST API for managing patients, doctors and patient–doctor assignments. Built with Django, Django REST Framework and PostgreSQL.

## Setup

Requires Python 3 and PostgreSQL.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in the values
python manage.py migrate
python manage.py runserver
```

The API runs at http://localhost:8000/api/.

## Authentication

Register, verify your email, then log in to get an access token. Send it on every other request:

```
Authorization: Bearer <access_token>
```

## Endpoints

**Auth**

| Method | URL                        | Body                        |
| ------ | -------------------------- | --------------------------- |
| POST   | `/api/auth/register/`      | `name`, `email`, `password` |
| POST   | `/api/auth/verify-otp/`    | `email`, `otp`              |
| POST   | `/api/auth/resend-otp/`    | `email`                     |
| POST   | `/api/auth/login/`         | `email`, `password`         |
| POST   | `/api/auth/token/refresh/` | `refresh`                   |

**Patients**: `/api/patients/` and `/api/patients/<id>/` (GET, POST, PUT, PATCH, DELETE). You only see patients you created.

**Doctors**: `/api/doctors/` and `/api/doctors/<id>/` (GET, POST, PUT, PATCH, DELETE). Anyone logged in can view doctors; only the creator can edit or delete.

**Mappings**

| Method | URL                           | Description                      |
| ------ | ----------------------------- | -------------------------------- |
| GET    | `/api/mappings/`              | All mappings for your patients   |
| POST   | `/api/mappings/`              | Assign a doctor to a patient     |
| GET    | `/api/mappings/<patient_id>/` | Doctors assigned to that patient |
| DELETE | `/api/mappings/<id>/`         | Remove a mapping                 |

Note: GET and DELETE share the same URL, but the ID means a patient ID for GET and a mapping ID for DELETE. A standard ViewSet can't handle that, so both are handled by one `APIView`.

## Errors

All errors use the same format:

```json
{
  "success": false,
  "status_code": 400,
  "errors": { "email": ["A user with this email already exists."] }
}
```
