
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

#### Go API Service

Navigate to the Go API directory and run the server:

```
cd go-api
go run main.go
```

Both services should now be running locally.

---