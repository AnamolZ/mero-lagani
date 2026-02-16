
### Mero-Lagani

Mero-Lagani is an automated market tracker that keeps an eye on company listings and market activity so you don’t have to. It collects and updates financial data in the background, saving you from checking multiple sites manually.

The system uses browser automation to fetch fresh data, stores it in Redis for fast access, and refreshes everything daily. It’s built to stay fast, reliable, and easy to scale as it grows.

---

### Runner (No Docker)

This project can be run locally without using Docker. Follow the steps below to start both the backend services.

#### Python Service

Install dependencies and start the Django server:

```
uv sync
uv run python manage.py runserver
```

## System Architecture

### Overview
This project is an automated system designed to scrape IPO data from MeroShare, cache it for high-performance access, and notify users of new opportunities.

### Core Components

1.  **Scraper (Selenium)**:
    - Located in `crawler/services/meroshare.py`.
    - Uses headless Chrome to log in to MeroShare and extract the "My ASBA" list.

2.  **Scheduler**:
    - Located in `crawler/services/scheduler.py`.
    - Runs a background thread that triggers the synchronization command every 60 minutes.

3.  **Data Storage & Caching**:
    - **Redis (Cache)**: Stores the full list of IPOs as a JSON string for the external Go API to consume.
    - **Redis (Deduplication)**: Uses a Redis Set (`seen_ipos`) to track which IPOs have already been processed to prevent duplicate emails.
    - **SQLite (Database)**: Acts as a persistent log for the admin panel.

4.  **Asynchronous Notifications (Celery)**:
    - Located in `crawler/tasks.py`.
    - When a new IPO is detected, the `sync_ipos` command triggers a Celery task.
    - The Celery worker processes this task in the background, sending emails via SMTP.

### Workflow
1.  **Trigger**: Scheduler (or Admin API) calls `sync_ipos`.
2.  **Scrape**: Selenium fetches current data.
3.  **Process**:
    - API Cache (`ipo_list`) is overwritten with fresh data.
    - Each IPO is checked against the Redis Set `seen_ipos`.
4.  **Notify**: If an IPO is new (not in Set), a Celery task is queued.
5.  **Deliver**: Celery worker picks up the task and sends emails.

## Installation

##### For superuser creation

```
uv run python manage.py createsuperuser
```

##### Commands

To manually check for new IPOs and send notifications:
```
uv run python manage.py sync_ipos
```

To clear the local IPO database (reset "new" detection):
```
uv run python manage.py clear_ipos
```

#### Celery Worker (Email Service)
The email notifications are now handled asynchronously by Celery.

To run the worker locally (without Docker):
```bash
# Make sure you have a Redis instance running on port 6379
uv run celery -A config worker --loglevel=info
```

When using Docker, the `celery` container starts automatically.

#### Go API Service

Navigate to the Go API directory and run the server:

```
cd go-api
go run main.go
```

Both services should now be running locally.

---

### Runner (Docker)

This project can be run locally using Docker. Follow the instructions below to manage backend services.

#### Build Services

Build all Docker images before starting the containers.

```bash
docker-compose build
```

#### Start Services

Start all services defined in `docker-compose.yml`.

```bash
docker-compose up
```

#### Clear IPO Cache

Removes all IPO records stored in Redis.

```bash
docker-compose exec web uv run python manage.py clear_ipos --force
```

#### Sync IPOs

Fetches the latest IPOs and updates the Redis cache.

```bash
docker-compose exec web uv run python manage.py sync_ipos
```

---