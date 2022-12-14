#!/bin/bash

# DB
echo "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" >> .env
echo "MYSQL_USER=$MYSQL_USER" >> .env
echo "MYSQL_PASSWORD=$MYSQL_PASSWORD" >> .env
echo "MYSQL_DATABASE=$MYSQL_DATABASE" >> .env
echo "MYSQL_HOST=$MYSQL_HOST" >> .env
echo "MYSQL_PORT=$MYSQL_PORT" >> .env

# Django
echo "DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY" >> .env
echo "DJANGO_ALLOWED_HOSTS=$DJANGO_ALLOWED_HOSTS" >> .env
echo "DEBUG_FLAG=$DEBUG_FLAG" >> .env
echo "TRUSTED_ORIGINS=$TRUSTED_ORIGINS" >> .env
echo "CRM_BASE_URL=$CRM_BASE_URL" >> .env
