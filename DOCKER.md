# Docker Setup Guide

This guide explains how to run the Slot Booking System API using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)

## Quick Start

1. **Build and start the containers:**
   ```bash
   docker-compose up --build
   ```

2. **The API will be available at:**
   - `http://localhost:8000/api/`
   - Admin panel: `http://localhost:8000/admin/`

3. **Create a superuser (in another terminal):**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## Common Commands

### Start containers in background:
```bash
docker-compose up -d
```

### Stop containers:
```bash
docker-compose down
```

### View logs:
```bash
docker-compose logs -f
```

### Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

### Create superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

### Access Django shell:
```bash
docker-compose exec web python manage.py shell
```

### Run tests:
```bash
docker-compose exec web python manage.py test
```

### Rebuild containers (after code changes):
```bash
docker-compose up --build
```

## Environment Variables

You can customize the application using environment variables in `docker-compose.yml`:

- `DEBUG`: Set to `True` or `False` (default: `True`)
- `SECRET_KEY`: Django secret key (default: development key)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts (default: `*`)

## Data Persistence

- Database: SQLite database is stored in a volume and persists between container restarts
- Media files: Uploaded files are stored in a Docker volume
- Static files: Collected static files are stored in a Docker volume

## Troubleshooting

### Port already in use:
If port 8000 is already in use, change it in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8001 to any available port
```

### Reset database:
```bash
docker-compose down -v
docker-compose up --build
```

### View container logs:
```bash
docker-compose logs web
```

## For Frontend Developers

The API is configured to accept requests from any origin (CORS enabled). You can connect your frontend running on `http://localhost:3000` to the API at `http://localhost:8000/api/`.

### Example API endpoints:
- Get available slots: `GET http://localhost:8000/api/slots/?date=2024-01-15`
- Create booking: `POST http://localhost:8000/api/bookings/`
- Get bookings: `GET http://localhost:8000/api/bookings/`

## Production Considerations

⚠️ **Warning**: This setup is for development only. For production:

1. Change `DEBUG=False` in environment variables
2. Set a strong `SECRET_KEY`
3. Configure proper `ALLOWED_HOSTS`
4. Use a production database (PostgreSQL) instead of SQLite
5. Set up proper static file serving (nginx, etc.)
6. Use environment variables or secrets management for sensitive data
7. Enable HTTPS

