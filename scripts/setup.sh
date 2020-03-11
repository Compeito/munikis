#!/bin/sh

set -e
cd `dirname $0`/../

echo "データ全て削除して開発用初期データを挿入します。よろしいですか？[y/N]"
read ANSWER
if [ "$ANSWER" != "y" ]; then
  exit 1
fi

docker-compose down && docker-compose build web
docker-compose up --no-deps -d db

echo "パッケージのインストール"
docker-compose run --no-deps web poetry install --no-root
echo "データベースのマイグレーション"
docker-compose run --no-deps web python manage.py migrate
echo "データベースの初期化"
docker-compose run --no-deps web python manage.py flush --no-input
echo "mediaディレクトリ下を削除"
rm -rf web/media/*
echo "初期データ作成"
docker-compose run --no-deps web python manage.py seed
echo "ランキング作成"
docker-compose run --no-deps web python manage.py ranking

docker-compose down && docker-compose up -d
