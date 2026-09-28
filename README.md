# Healthcare Backend

A REST API for managing patients, doctors and patient–doctor assignments. Built with Django, Django REST Framework and PostgreSQL.

## How to run

You'll need Python 3 and a running PostgreSQL server.

Before starting, create a `.env` file in the project root with the following:

- **PostgreSQL connection**: database name, username, password, host (e.g. `localhost`) and port (usually `5432`). The database and user must already exist.
- **Django**: a secret key (also used to sign access tokens), debug mode on or off, and the allowed hosts (e.g. `localhost,127.0.0.1`).
- **Access tokens**: how long an access token stays valid (in minutes) and how long a refresh token stays valid (in days).
- **Email (SMTP)**: server, port, whether to use TLS, username, password and the "from" address. This is used to send the verification OTP.
- **OTP**: how many minutes a verification OTP stays valid.

Then install dependencies, create the tables and start the server:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
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
