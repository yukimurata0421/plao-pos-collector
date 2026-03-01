#!/usr/bin/env bash
set -euo pipefail

# User-editable variables (or override via environment variables)
PI_USER="${PI_USER:-your_user}"
PI_HOST="${PI_HOST:-your.pi.local}"
PI_DIR="${PI_DIR:-/path/on/pi/with_pos_jsonl}"
ARENA_DIR="${ARENA_DIR:-/mnt/e/arena/data/plao_pos}"
# Windows example (path varies by user): E:\arena\data\plao_pos

if [ ! -d "/mnt/e" ]; then
  echo "WSL mount /mnt/e not found. Check your WSL configuration." >&2
  exit 1
fi

mkdir -p "${ARENA_DIR}"

SSH_OPTS="-o BatchMode=yes -o ConnectTimeout=10"
RSYNC_BASE=(rsync -av -e "ssh ${SSH_OPTS}")

TODAY_UTC=$(date -u +%Y%m%d)
TODAY_FILE="pos_${TODAY_UTC}.jsonl"

# Past days: copy only new files (append-only logs are immutable for past days)
"${RSYNC_BASE[@]}" --ignore-existing \
  "${PI_USER}@${PI_HOST}:${PI_DIR}/pos_*.jsonl" \
  "${ARENA_DIR}/" || true

# Today: follow append-only growth
"${RSYNC_BASE[@]}" --append-verify \
  "${PI_USER}@${PI_HOST}:${PI_DIR}/${TODAY_FILE}" \
  "${ARENA_DIR}/" || true

echo "[OK] Sync complete."
