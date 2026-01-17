# Running the project locally (without Docker)

```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

# Running with Docker (Postgres)

1. Build and start services (backend + Postgres + Prometheus):

```bash
# from project root
docker-compose up --build -d
```

2. Sprawdź logi backendu i bazy (przydatne przy problemach):

```bash
docker-compose logs -f backend
docker-compose logs -f db
```

3. Aplikacja powinna być dostępna na: http://localhost:8000
   - endpoint zdrowia: http://localhost:8000/health

4. Volumen Postgresa:
   - Dane Postgresa są zapisywane w wolumenie `pgdata` (zdefiniowanym w `docker-compose.yml`).

5. Wymuszenie inicjalizacji bazy (opcjonalne):

```bash
# uruchomienie inicjalizacji ręcznie wewnątrz kontenera backend
docker-compose exec backend python -m app.init_db
```

# Dodanie migracji (opcjonalnie — Alembic)

Jeśli chcesz używać migracji zamiast `Base.metadata.create_all`:

1. Zainstaluj Alembic w środowisku deweloperskim:

```bash
pip install alembic
```

2. Zainicjuj folder migracji:

```bash
alembic init alembic
```

3. Skonfiguruj `alembic.ini` lub `alembic/env.py`, aby używał adresu z `DATABASE_URL` (np. `postgresql://postgres:example@localhost:5432/app`) oraz importował `app.database.Base.metadata`.

W `alembic/env.py` typowo wystarczy podmienić część konfiguracji SQLAlchemy na coś w stylu:

```py
from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# import your models' metadata
from app.database import Base

config = context.config
fileConfig(config.config_file_name)

# można wczytać DATABASE_URL z env
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL', 'postgresql://postgres:example@localhost:5432/app'))

target_metadata = Base.metadata
```

4. Stwórz migrację automatycznie i zastosuj:

```bash
alembic revision --autogenerate -m "create tables"
alembic upgrade head
```

# Branch i commit

Proponowany branch: `feature/etap5-postgres` (już zasugerowany wcześniej). Po dokonaniu zmian:

```bash
git checkout -b feature/etap5-postgres
git add .
git commit -m "Add Postgres service and DB init (etap5)"
git push -u origin feature/etap5-postgres
```

# Notatki i debug

- Aplikacja już uruchamia `init_db()` przy starcie (w `app/main.py`). Dodałem retry w `app/init_db.py`, żeby backend poczekał na start Postgresa.
- Jeśli backend nie łączy się z DB w Dockerze, sprawdź czy w `docker-compose.yml` adres `DATABASE_URL` ma host `db` (tak jak jest skonfigurowane) i czy kontenery są w tej samej sieci (domyślnie tak).
