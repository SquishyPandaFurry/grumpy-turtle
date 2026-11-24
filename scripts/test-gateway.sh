#!/usr/bin/env bash
# One test call to OpenRouter through the Sprites connector gateway.
# Run on the Sprite:  scripts/test-gateway.sh <connection_id>
# No API key: the gateway recognises this Sprite and adds the key itself.
set -euo pipefail
CONN="${1:-${POND_CONNECTION_ID:-}}"
[ -n "$CONN" ] || { echo "usage: $0 <openrouter_connection_id>"; exit 1; }
MODEL="${POND_MODEL:-anthropic/claude-haiku-4.5}"
BASE="${POND_GATEWAY_BASE:-https://api.sprites.dev/v1/gateway/openrouter/$CONN/v1}"

echo "== Connectors this Sprite can use (gateway/list)"
curl -sS https://api.sprites.dev/v1/gateway/list || true
echo
echo "== Test call: POST $BASE/chat/completions"
curl -sS -w '\nHTTP %{http_code}\n' "$BASE/chat/completions" \
  -H 'Content-Type: application/json' \
  -d "{\"model\":\"$MODEL\",\"max_tokens\":60,\"messages\":[{\"role\":\"user\",\"content\":\"You are a sleepy old turtle. Say hello to a child in one short sentence.\"}]}"
