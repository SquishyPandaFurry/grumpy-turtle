#!/usr/bin/env bash
# Create the pond as a Sprite service: it starts itself when the Sprite wakes,
# and the runtime restarts it if it crashes. Run once on the Sprite:
#   scripts/setup-service.sh <openrouter_connection_id>
# (Re-running replaces the definition.)
set -euo pipefail
CONN="${1:-${POND_CONNECTION_ID:-}}"
[ -n "$CONN" ] || { echo "usage: $0 <openrouter_connection_id>"; exit 1; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

sprite-env services delete pond 2>/dev/null || true
sprite-env services create pond \
  --cmd python3 \
  --args "$ROOT/pond/server.py" \
  --dir "$ROOT/pond" \
  --env "POND_CONNECTION_ID=$CONN,POND_PORT=8080,PYTHONUNBUFFERED=1" \
  --http-port 8080

sleep 2
echo
echo "Service state:"; sprite-env services get pond || true
echo
echo "Your private pond link (bookmark it, don't share it):"
echo "  <your Sprite URL from 'sprite url'>/?key=$(cat "$ROOT/pond/secret_key.txt")"
