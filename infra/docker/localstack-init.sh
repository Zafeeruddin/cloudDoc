#!/bin/sh
set -eu

aws --endpoint-url "$LOCALSTACK_ENDPOINT" sqs create-queue --queue-name "$DOCOPS_QUEUE_NAME" >/dev/null
