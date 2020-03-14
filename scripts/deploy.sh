#!/bin/sh

set -e
cd `dirname $0`/../

alias docker-compose-prod='docker-compose -f docker-compose.yml -f docker-compose.prod.yml'

# イメージの再ビルド
docker-compose-prod build

# DB以外のボリュームの削除
docker volume rm tsukuriga_venv
docker volume rm tsukuriga_node_modules
docker volume rm tsukuriga_sock

# 依存関係の更新とDBマイグレーション
docker-compose-prod up --no-deps -d db
docker-compose-prod run --no-deps --rm web python manage.py migrate

# js/cssの再ビルドと配置
rm -rf nginx/assets/bundles/*
rm -rf nginx/assets/webpack-stats.json
docker-compose-prod run --no-deps --rm node bash -c "yarn && yarn run build"
docker-compose-prod run --no-deps --rm web python manage.py collectstatic --no-input

docker-compose-prod up -d --force-recreate
