#!/bin/sh
set -eu

: "${VITE_API_BASE_URL:=http://localhost:8000}"

envsubst '${VITE_API_BASE_URL}' \
  < /usr/share/nginx/html/config.template.js \
  > /usr/share/nginx/html/config.js
