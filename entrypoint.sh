#!/bin/bash
set -e

if [ "$1" = 'sam-mobotix' ]; then
    exec /app/sam-mobotix
fi

exec "$@"
