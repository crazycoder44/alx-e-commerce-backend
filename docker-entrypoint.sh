#!/bin/bash
set -e

# Experimental entrypoint that initializes and starts a local PostgreSQL server
# then runs Django migrations/collectstatic and starts the passed CMD (gunicorn).

: "${POSTGRES_DB:=postgres}"
: "${POSTGRES_USER:=postgres}"
: "${POSTGRES_PASSWORD:=postgres}"
: "${POSTGRES_PORT:=5432}"
PGDATA=${PGDATA:-/var/lib/postgresql/data}

mkdir -p "$PGDATA"
chown -R postgres:postgres "$PGDATA"
chmod 700 "$PGDATA"

if [ ! -s "$PGDATA/PG_VERSION" ]; then
  echo "[entrypoint] Initializing Postgres database at $PGDATA..."
  su -s /bin/bash postgres -c "initdb -D '$PGDATA'"

  echo "[entrypoint] Starting temporary Postgres to create user/db..."
  su -s /bin/bash postgres -c "pg_ctl -D '$PGDATA' -o \"-c listen_addresses='localhost'\" -w start"

  echo "[entrypoint] Creating user and database..."
  su -s /bin/bash postgres -c "psql -v ON_ERROR_STOP=1 --username postgres <<-EOSQL
    CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';
    CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};
EOSQL"

  echo "[entrypoint] Stopping temporary Postgres..."
  su -s /bin/bash postgres -c "pg_ctl -D '$PGDATA' -m fast -w stop"
fi

echo "[entrypoint] Starting Postgres server..."
su -s /bin/bash postgres -c "pg_ctl -D '$PGDATA' -o \"-c listen_addresses='*' -p ${POSTGRES_PORT}\" -w start"

echo "[entrypoint] Waiting for Postgres to accept connections..."
until su -s /bin/bash postgres -c "psql -U ${POSTGRES_USER} -c '\\l'" >/dev/null 2>&1; do
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
