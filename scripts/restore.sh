#!/usr/bin/env bash
set -euo pipefail

# Restore script for Edu Auto Grader (PostgreSQL dump + optional uploads archive).
# Targets the isolated production Compose project (edu-auto-grader-prod) and its
# postgres_data_prod (/var/lib/postgresql/data) and uploads_data_prod (/app/uploads) volumes.
# Usage:
#   ./scripts/restore.sh ./backups/db_20261125_030000.dump [./backups/uploads_20261125_030000.tar.gz] [--yes]

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <db_backup.dump> [uploads_backup.tar.gz] [--yes]" >&2
  exit 1
fi

DB_BACKUP_FILE="$1"
shift

UPLOADS_BACKUP_FILE=""
AUTO_CONFIRM="false"

for arg in "$@"; do
  if [[ "${arg}" == "--yes" ]]; then
    AUTO_CONFIRM="true"
  elif [[ -z "${UPLOADS_BACKUP_FILE}" ]]; then
    UPLOADS_BACKUP_FILE="${arg}"
  else
    echo "Error: unexpected argument '${arg}'." >&2
    exit 1
  fi
done

if [[ ! -f "${DB_BACKUP_FILE}" ]]; then
  echo "Error: database backup file not found: ${DB_BACKUP_FILE}" >&2
  exit 1
fi

if [[ -n "${UPLOADS_BACKUP_FILE}" && ! -f "${UPLOADS_BACKUP_FILE}" ]]; then
  echo "Error: uploads backup archive not found: ${UPLOADS_BACKUP_FILE}" >&2
  exit 1
fi

COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-edu-auto-grader-prod}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.production}"

COMPOSE_ARGS=(-p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}")
if [[ -f "${ENV_FILE}" ]]; then
  COMPOSE_ARGS+=(--env-file "${ENV_FILE}")
fi

if [[ "${AUTO_CONFIRM}" != "true" ]]; then
  echo "WARNING: This will overwrite the PostgreSQL database${UPLOADS_BACKUP_FILE:+ and /app/uploads}!"
  read -r -p "Continue? [y/N] " reply
  if [[ ! "${reply}" =~ ^[Yy]$ ]]; then
    echo "[restore] Cancelled."
    exit 0
  fi
fi

echo "[restore] Restoring PostgreSQL from ${DB_BACKUP_FILE}..."
docker compose "${COMPOSE_ARGS[@]}" exec -T db \
  sh -c 'pg_restore --clean --if-exists --no-owner --no-privileges -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  < "${DB_BACKUP_FILE}"

if [[ -n "${UPLOADS_BACKUP_FILE}" ]]; then
  echo "[restore] Restoring uploads from ${UPLOADS_BACKUP_FILE}..."
  docker compose "${COMPOSE_ARGS[@]}" exec -T backend \
    tar -xzf - -C /app \
    < "${UPLOADS_BACKUP_FILE}"
fi

echo "[restore] Restore completed successfully."
