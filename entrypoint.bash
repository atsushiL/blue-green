#!/bin/bash

set -eu

poetry run python manage.py makemigrations
poetry run python manage.py migrate

if [ $DEBUG_FLAG = "True" ]
then
    poetry run python manage.py runserver 0.0.0.0:8000
else
    poetry run gunicorn ag_smile_leaseback_crm_back.wsgi:application --bind 0.0.0.0:8000
fi
