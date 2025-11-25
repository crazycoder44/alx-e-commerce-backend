#!/bin/bash
set -e

# Experimental entrypoint that initializes and starts a local PostgreSQL server
# then runs Django migrations/collectstatic and starts the passed CMD (gunicorn).

: "${POSTGRES_DB:=postgres}"
: "${POSTGRES_USER:=postgres}"
: "${POSTGRES_PASSWORD:=postgres}"
: "${POSTGRES_PORT:=5432}"
PGDATA=${PGDATA:-/var/lib/postgresql/data}

find_bin() {
  # try PATH first
  if command -v "$1" >/dev/null 2>&1; then
    command -v "$1"
    return 0
  fi
  # try Debian/Ubuntu typical locations
  for p in /usr/lib/postgresql/*/bin/$1 /usr/local/pgsql/bin/$1; do
    if [ -x "$p" ]; then
      echo "$p"
      return 0
    fi
  done
  return 1
}

INITDB_CMD=$(find_bin initdb) || true
PG_CTL_CMD=$(find_bin pg_ctl) || true
PSQL_CMD=$(find_bin psql) || true

mkdir -p "$PGDATA"
chown -R postgres:postgres "$PGDATA" || true
chmod 700 "$PGDATA" || true

if [ ! -s "$PGDATA/PG_VERSION" ]; then
  echo "[entrypoint] Initializing Postgres database at $PGDATA..."

  if [ -z "$INITDB_CMD" ]; then
    echo "[entrypoint][error] initdb not found in image. Postgres binaries are missing." >&2
    echo "Install Postgres packages or use an image with Postgres binaries." >&2
    exit 127
  fi

  su -s /bin/bash postgres -c "$INITDB_CMD -D '$PGDATA'"

  echo "[entrypoint] Starting temporary Postgres to create user/db..."
  if [ -z "$PG_CTL_CMD" ]; then
    echo "[entrypoint][error] pg_ctl not found in image." >&2
    exit 127
  fi

  su -s /bin/bash postgres -c "$PG_CTL_CMD -D '$PGDATA' -o \"-c listen_addresses='localhost'\" -w start"

  echo "[entrypoint] Creating user and database (if missing)..."
  if [ -z "$PSQL_CMD" ]; then
    echo "[entrypoint][error] psql not found in image." >&2
    exit 127
  fi

  # Write a temporary SQL file with variables expanded by the shell, then execute it as the postgres user.
  TMP_SQL=/tmp/init_db.sql
  cat > "$TMP_SQL" <<SQL
DO

$$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${POSTGRES_USER}') THEN
    EXECUTE format('CREATE USER %I WITH PASSWORD %L', '${POSTGRES_USER}', '${POSTGRES_PASSWORD}');
  END IF;
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}') THEN
    EXECUTE format('CREATE DATABASE %I OWNER %I', '${POSTGRES_DB}', '${POSTGRES_USER}');
  END IF;
END
$$;
SQL

  su -s /bin/bash postgres -c "$PSQL_CMD -v ON_ERROR_STOP=1 --username postgres -f $TMP_SQL"
  rm -f "$TMP_SQL"

  echo "[entrypoint] Stopping temporary Postgres..."
  su -s /bin/bash postgres -c "$PG_CTL_CMD -D '$PGDATA' -m fast -w stop"
fi

echo "[entrypoint] Starting Postgres server..."
if [ -z "$PG_CTL_CMD" ]; then
  echo "[entrypoint][error] pg_ctl not found, cannot start Postgres." >&2
  exit 127
fi
su -s /bin/bash postgres -c "$PG_CTL_CMD -D '$PGDATA' -o \"-c listen_addresses='*' -p ${POSTGRES_PORT}\" -w start"

echo "[entrypoint] Waiting for Postgres to accept connections..."
until su -s /bin/bash postgres -c "$PSQL_CMD -U ${POSTGRES_USER} -c '\\l'" >/dev/null 2>&1; do
  echo "[entrypoint] Postgres not ready yet - sleeping 1s"
  sleep 1
done

if [ -z "$DATABASE_URL" ]; then
  export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:${POSTGRES_PORT}/${POSTGRES_DB}"
  echo "[entrypoint] Set DATABASE_URL=$DATABASE_URL"
fi

echo "[entrypoint] Running Django migrations..."
python manage.py migrate --noinput

echo "[entrypoint] Collecting static files..."
python manage.py collectstatic --noinput || true

echo "[entrypoint] Launching application: $@"
exec "$@"
