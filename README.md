
# Description

LibraryLite is a small web application (university project) for user registration and basic management of a book collection via a web interface.

Run with Docker

1. Build and start services (from project root):

```bash
docker-compose up --build -d
```

2. View logs (helpful for debugging):

```bash
docker-compose logs -f backend
docker-compose logs -f db
```

3. Access the application in your browser:

- Web UI: http://localhost:8000
- Health endpoint: http://localhost:8000/health

4. Force database initialization (optional):

```bash
docker-compose exec backend python -m app.init_db
```

Notes

- This repository includes Docker, Prometheus and Grafana configuration used during development.

- Prometheus: collects runtime metrics from the backend (HTTP metrics, request durations, etc.) to help observe application health and performance.
- Grafana: dashboards are provided to visualise Prometheus metrics and make it easier to inspect trends and alerts.
- Database: the project uses a relational database (configured in `docker-compose.yml`) for storing users and books; the DB is persisted in a Docker volume so data survives container restarts.

