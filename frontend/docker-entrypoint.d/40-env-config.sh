#!/bin/sh
set -eu

: "${VITE_API_BASE_URL:=/api}"
: "${DOCOPS_API_UPSTREAM:=http://backend:8000}"

envsubst '${VITE_API_BASE_URL}' \
  < /usr/share/nginx/html/config.template.js \
  > /usr/share/nginx/html/config.js

envsubst '${DOCOPS_API_UPSTREAM}' \
  < /etc/nginx/conf.d/default.conf \
  > /tmp/default.conf

mv /tmp/default.conf /etc/nginx/conf.d/default.conf
