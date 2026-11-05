#!/bin/sh
# Пограничная служба на VPS: образ, запуск, досылка очереди по расписанию.
set -e

REMOTE=/home/hidecore/terminal-blog/edge

ssh hidecore "mkdir -p $REMOTE/src "
rsync -az --delete --exclude .venv --exclude '.db*' --exclude data/ --exclude __pycache__ \
  edge/ hidecore:$REMOTE/src/

ssh hidecore "cd $REMOTE/src && docker build -q -t coreeuler-edge ." >/dev/null
ssh hidecore "mkdir -p $REMOTE/data"

ssh hidecore "test -f $REMOTE/.env || cat > $REMOTE/.env" <<'ENV'
EDGE_BACKEND_URL=http://127.0.0.1:8081
EDGE_DB_PATH=/data/edge.db
EDGE_CACHE_SECONDS=60
EDGE_TIMEOUT_SECONDS=5
EDGE_ACCEPT_TIMEOUT_SECONDS=2
EDGE_RETENTION_DAYS=30
ENV

ssh hidecore 'bash -s' <<SCRIPT
set -e
docker rm -f coreeuler-edge >/dev/null 2>&1 || true
docker run -d --name coreeuler-edge --restart=always --network host \\
  --env-file $REMOTE/.env -v $REMOTE/data:/data coreeuler-edge >/dev/null
sleep 2
docker ps --filter name=coreeuler-edge --format '{{.Status}}'

crontab -l 2>/dev/null | grep -v 'coreeuler-edge python' > /tmp/cron.new || true
echo "* * * * * docker run --rm --network host --env-file $REMOTE/.env -v $REMOTE/data:/data coreeuler-edge python -c 'from app.worker import run_once; print(run_once())' >> $REMOTE/sync.log 2>&1" >> /tmp/cron.new
crontab /tmp/cron.new
crontab -l | tail -1
SCRIPT

echo "Пограничная служба обновлена"
