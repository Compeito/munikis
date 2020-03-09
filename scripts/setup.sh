#!/bin/sh

cd `dirname $0`/../

docker-compose down && docker-compose build web

echo "パッケージのインストール"
docker-compose run web poetry install --no-root
echo "データベースのマイグレーション"
docker-compose run web python manage.py migrate
echo "データベースの初期化"
docker-compose run web python manage.py flush --no-input
echo "mediaディレクトリ下を削除"
rm -rf web/media/*
echo "初期データ作成"
docker-compose run web python manage.py seed
echo "ランキング作成"
docker-compose run web python manage.py ranking

docker-compose down && docker-compose up -d
