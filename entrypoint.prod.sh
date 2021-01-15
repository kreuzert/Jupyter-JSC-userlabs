#!/bin/sh

lsof -v &> /dev/null
LSOF_EC=$?

if [[ ! $LSOF_EC -eq 0 ]]; then
    echo "lsof is not installed"
    exit 255
fi

/usr/sbin/sshd -f /etc/ssh/sshd_config

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for postgres..."
    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done
    echo "PostgreSQL started"
fi

su app -c "cd /home/app/web && /usr/local/bin/gunicorn -w 4 --bind 0.0.0.0 userlab.wsgi"
