#!/bin/sh

HTTP_PORT=8080
if [ -n "$PORT" ]; then
  HTTP_PORT=$PORT
fi

python manage.py migrate
uwsgi --http-socket 0.0.0.0:$HTTP_PORT --module tsukuriga.wsgi
