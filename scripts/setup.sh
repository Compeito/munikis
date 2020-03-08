#!/bin/sh

# Dockerイメージの作成
docker-compose build web

# パッケージのインストールとデータベースのマイグレーション
docker-compose run web poetry install
docker-compose run web python manage.py migrate

docker-compose down
