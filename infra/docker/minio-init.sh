#!/bin/sh
set -eu

until mc alias set local http://minio:9000 minioadmin minioadmin; do
  sleep 2
done

mc mb --ignore-existing local/docops-documents-local
mc anonymous set none local/docops-documents-local
