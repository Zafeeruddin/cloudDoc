#!/bin/sh
set -eu

until aws --endpoint-url="$LOCALSTACK_ENDPOINT" sqs create-queue --queue-name "$DOCOPS_QUEUE_NAME" >/dev/null 2>&1; do
  sleep 2
done
