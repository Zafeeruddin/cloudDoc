#!/bin/sh
set -eu

until /usr/bin/mc alias set local http://minio:9000 minioadmin minioadmin >/dev/null 2>&1; do
  sleep 2
done
/usr/bin/mc mb --ignore-existing local/docops-documents-local
/usr/bin/mc anonymous set none local/docops-documents-local
