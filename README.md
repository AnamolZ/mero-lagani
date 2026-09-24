# Mero-Lagani

Mero-Lagani is an automated market tracker and IPO notification system for MeroShare. It collects and updates financial/IPO data in the background using browser automation (headless Chrome + Selenium), caches it in Redis for high-performance access, serves it through a blazing-fast Go API, and dispatches asynchronous email notifications using Celery.

---

## System Architecture

```
+-----------------------------------------------------------+
|                      MeroShare Portal                     |
+-----------------------------+-----------------------------+
                              | (Headless Chrome / Selenium)
                              v
                  +-----------------------+
                  |  Django Web & Scraper | <--- Port 8000
                  +-----------+-----------+
                              |
       +----------------------+----------------------+
       | (Cache & Deduplication)                     | (Task Queue)
       v                                             v
+--------------+                             +---------------+
| Redis (6379) |                             | Celery Worker |
+-------+------+                             +-------+-------+
        |                                            |
        |                                            v
        v (Consume cached JSON)             (Async SMTP Emails)
+---------------+
|  Go Fiber API | <--- Port 8080
+---------------+
```

### Core Components
1. **Scraper (Selenium)**: Located in `crawler/services/meroshare.py`. Uses headless Chrome to log in to MeroShare and extract active issues.
2. **Scheduler**: Runs a background thread that periodically triggers synchronization.
3. **Redis**:
   - Stores the full list of IPOs as JSON in DB 1 (`ipo_list`) for the Go API.
   - Deduplicates IPOs using a Redis Set in DB 1 (`seen_ipos`).
   - Acts as task broker and results backend in DB 0 for Celery.
4. **Go Fiber API**: Fast endpoint on port `8080` with rate limiting that serves cached IPO records from Redis.
5. **Celery Worker**: Asynchronously dispatches HTML email notifications via SMTP.

---

## Docker Hub Images

Pre-built Docker images are published on Docker Hub:

- **Main Application (Django + Scraper + Celery)**:
  ```bash
  docker pull err0rz/mero-lagani:latest
  ```
- **Go Fiber API**:
  ```bash
  docker pull err0rz/mero-lagani-api:latest
  ```

---

## Quickstart with Docker Compose

The easiest way to run the entire stack is with Docker Compose.

### 1. Environment Setup
Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` and fill in your MeroShare credentials and email SMTP settings:
```env
# MeroShare Automation Credentials
MEROSHARE_DP_ID=your_dp_id
MEROSHARE_USERNAME=your_username
MEROSHARE_PASSWORD=your_password

# SMTP Email Configuration (e.g. Brevo)
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password
```

### 2. Pull & Start Services
Pull the latest images from Docker Hub and start all containers:
```bash
docker compose pull
docker compose up -d
```

### 3. Verify Running Services
```bash
docker compose ps
```
The stack runs:
- `web`: Django backend & scraper at `http://localhost:8000`
- `api`: Go Fiber API at `http://localhost:8080`
- `redis`: Redis server (mapped to `localhost:6389` on host, internal `6379`)
- `celery`: Background email worker

### 4. Test the Endpoints
- **Go API (Cached Data)**:
  ```bash
  curl http://localhost:8080/api/ipos/
  ```
- **Django API (Trigger Fresh Scrape)**:
  ```bash
  curl http://localhost:8000/api/ipos/
  ```

### 5. Running Container Commands
- **Manual IPO Scrape & Sync**:
  ```bash
  docker compose exec web uv run python manage.py sync_ipos
  ```
- **Clear IPO Cache**:
  ```bash
  docker compose exec web uv run python manage.py clear_ipos
  ```
- **Create Superuser**:
  ```bash
  docker compose exec web uv run python manage.py createsuperuser
  ```
- **View Container Logs**:
  ```bash
  docker compose logs -f web
  docker compose logs -f celery
  docker compose logs -f api
  ```

---

## Running Standalone Docker Container

If you only want to run the web application container:

```bash
docker run -d \
  --name mero-lagani \
  -p 8000:8000 \
  --env-file .env \
  err0rz/mero-lagani:latest
```

---

## Local Development (Without Docker)

### Prerequisites
- Python 3.12+ (or [uv](https://docs.astral.sh/uv/))
- Google Chrome installed (for Selenium)
- Redis instance running on `localhost:6389` (or `6379`)
- Go 1.22+ (for `go-api`)

### 1. Python Django Service
```bash
# Install dependencies
uv sync

# Run database migrations
uv run python manage.py migrate

# Start development server
uv run python manage.py runserver
```

### 2. Celery Worker (Email Notifications)
```bash
uv run celery -A config worker --loglevel=info
```

### 3. Go API Service
```bash
cd go-api
go run main.go
```