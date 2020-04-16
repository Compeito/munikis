#!/bin/sh

set -e
cd `dirname $0`/../

cd tsukuriga
git fetch origin
git reset --hard origin/migration/gcp-run

CRON="
ENTRYPOINT=\"cd ~/tsukuriga && docker-compose run --rm -d web poetry run\"
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
