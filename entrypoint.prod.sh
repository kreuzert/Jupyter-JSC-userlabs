#!/bin/sh

lsof -v &> /dev/null
LSOF_EC=$?

if [[ ! $LSOF_EC -eq 0 ]]; then
    echo "lsof is not installed"
    exit 255
fi

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for postgres..."
    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done
    echo "PostgreSQL started"
fi

exec "$@"
