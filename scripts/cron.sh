#!/bin/sh

CRON="
COMPOSE=/usr/local/bin/docker-compose -f ~/tsukuriga/docker-compose.yml -f ~/tsukuriga/docker-compose.gcp.yml
ENTRYPOINT=\"cd ~/tsukuriga && \$COMPOSE run --rm -d web poetry run\"
* * * * *   \$EXTRYPOINT encode
*/5 * * * * \$EXTRYPOINT gif
0 1 * * *   \$EXTRYPOINT ranking
0 0 * * *   \$EXTRYPOINT contrib
0 0 * * *   \$EXTRYPOINT ping_google
30 18 * * * \$EXTRYPOINT retweet
"

FILEPATH=/var/tmp/cron-$(date +\%Y\%m\%d-\%H\%M\%S).conf
echo "$CRON" > $FILEPATH
crontab $FILEPATH
