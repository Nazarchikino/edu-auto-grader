#!/usr/bin/env bash
set -euo pipefail

# Daily backup script for Edu Auto Grader (PostgreSQL custom dump + uploads archive).
# Targets the isolated production Compose project (edu-auto-grader-prod) and its
# postgres_data_prod (/var/lib/postgresql/data) and uploads_data_prod (/app/uploads) volumes.
# Usage:
#   ./scripts/backup.sh
#   RETENTION_BACKUP_DAYS=30 BACKUP_DIR=/var/backups/edu-auto-grader ./scripts/backup.sh

COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-edu-auto-grader-prod}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.production}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_BACKUP_DAYS="${RETENTION_BACKUP_DAYS:-14}"

if ! [[ "${RETENTION_BACKUP_DAYS}" =~ ^[0-9]+$ ]]; then
  echo "Error: RETENTION_BACKUP_DAYS must be a non-negative integer." >&2
  exit 1
fi

COMPOSE_ARGS=(-p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}")
if [[ -f "${ENV_FILE}" ]]; then
  COMPOSE_ARGS+=(--env-file "${ENV_FILE}")
fi

mkdir -p "${BACKUP_DIR}"
TIMESTAMP="$(date -u +%Y%m%d_%H%M%S)"
DB_BACKUP_FILE="${BACKUP_DIR}/db_${TIMESTAMP}.dump"
UPLOADS_BACKUP_FILE="${BACKUP_DIR}/uploads_${TIMESTAMP}.tar.gz"

echo "[backup] Starting backup at ${TIMESTAMP} UTC..."

docker compose "${COMPOSE_ARGS[@]}" exec -T db \
  sh -c 'pg_dump -Fc -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  > "${DB_BACKUP_FILE}"

if [[ ! -s "${DB_BACKUP_FILE}" ]]; then
  rm -f "${DB_BACKUP_FILE}"
  echo "Error: PostgreSQL dump is empty." >&2
  exit 1
fi

docker compose "${COMPOSE_ARGS[@]}" exec -T backend \
  tar -czf - -C /app uploads \
  > "${UPLOADS_BACKUP_FILE}"

if [[ ! -s "${UPLOADS_BACKUP_FILE}" ]]; then
  rm -f "${UPLOADS_BACKUP_FILE}"
  echo "Error: Uploads archive is empty." >&2
  exit 1
fi

find "${BACKUP_DIR}" -maxdepth 1 -type f \
  \( -name "db_*.dump" -o -name "uploads_*.tar.gz" \) \
  -mtime +"${RETENTION_BACKUP_DAYS}" -delete

echo "[backup] Completed successfully:"
echo "  - Database: ${DB_BACKUP_FILE} ($(du -h "${DB_BACKUP_FILE}" | cut -f1))"
echo "  - Uploads:  ${UPLOADS_BACKUP_FILE} ($(du -h "${UPLOADS_BACKUP_FILE}" | cut -f1))"
echo "  - Retention policy: delete backups older than ${RETENTION_BACKUP_DAYS} days"
