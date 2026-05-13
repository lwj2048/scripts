#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <username> <password>" >&2
  exit 1
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTH_DIR="${SCRIPT_DIR}/auth"
mkdir -p "${AUTH_DIR}"
docker run --rm httpd:2.4-alpine htpasswd -nbB "$1" "$2" > "${AUTH_DIR}/.htpasswd"
echo "Wrote ${AUTH_DIR}/.htpasswd"
