#!/bin/sh

HTTP_PORT=8080
if [ -n "$PORT" ]; then
  HTTP_PORT=$PORT
fi

python manage.py migrate

if [ $DEBUG = "true" ]; then
  python manage.py runserver_plus 0.0.0.0:8080
else
  uwsgi \
    --http-socket 0.0.0.0:$HTTP_PORT \
    --master \
    --processes 4 \
    --threads 4 \
    --module tsukuriga.wsgi
fi
