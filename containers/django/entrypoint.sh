#!/bin/bash
set -eu

mkdir -p ${APP_ROOT}/tmp/gunicorn_sockets

# Run Django application
poetry run gunicorn ag_smile_leaseback_crm_back.wsgi:application --bind=unix://${APP_ROOT}/tmp/gunicorn_socket

exec "$@"
