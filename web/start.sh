#!/bin/sh

HTTP_PORT=8080
if [ -n "$PORT" ]; then
  HTTP_PORT=$PORT
fi

# Cloud Runが定義する環境変数で本番環境を判定
# https://cloud.google.com/run/docs/reference/container-contract?hl=ja#env-vars
if [ -n "$K_SERVICE" ]; then
  python manage.py migrate
fi

if [ $DEBUG = "true" ]; then
  python manage.py runserver_plus 0.0.0.0:8080
else
  uwsgi --http-socket 0.0.0.0:$HTTP_PORT --ini uwsgi.ini
fi
