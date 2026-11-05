#!/bin/sh
# Домашний сервер: код API, окружение, миграции, службы. Запускается с машины разработчика.
set -e

HOST=${HOST:-local}
DIR=coreeuler/backend

ssh $HOST 'sudo -n apt-get install -y -qq postgresql python3-venv >/dev/null'

ssh $HOST "mkdir -p ~/$DIR"
rsync -az --delete --exclude .venv --exclude .tmp --exclude __pycache__ --exclude .uv-cache --exclude .env \
  backend/ $HOST:~/$DIR/

ssh $HOST 'bash -s' <<REMOTE
set -e
cd ~/$DIR
PW_FILE=~/.coreeuler-db-password
if [ ! -f "\$PW_FILE" ]; then
  PW=\$(openssl rand -hex 24)
  printf '%s' "\$PW" > "\$PW_FILE"; chmod 600 "\$PW_FILE"
  sudo -n -u postgres psql -q -c "CREATE ROLE coreeuler LOGIN PASSWORD '\$PW'" || \
    sudo -n -u postgres psql -q -c "ALTER ROLE coreeuler PASSWORD '\$PW'"
fi
sudo -n -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='coreeuler'" | grep -q 1 || \
  sudo -n -u postgres createdb -O coreeuler coreeuler

[ -d .venv ] || python3 -m venv .venv
./.venv/bin/pip install -q -e .

if [ ! -f .env ]; then
  PW=\$(cat "\$PW_FILE")
  cat > .env <<ENV
CORE_DATABASE_URL=postgresql+psycopg://coreeuler:\${PW}@127.0.0.1:5432/coreeuler
CORE_NEWS_AGENT_TOKEN=\$(openssl rand -hex 24)
CORE_HASH_PEPPER=\$(openssl rand -hex 32)
CORE_CORS_ORIGINS=https://coreeuler.art
CORE_TRUST_PROXY_HEADERS=true
CORE_NEWS_SOURCES_PATH=sources.toml
ENV
  chmod 600 .env
fi

./.venv/bin/python -m alembic upgrade head
REMOTE

rsync -az deploy/home/*.service $HOST:/tmp/
ssh $HOST 'bash -s' <<'REMOTE'
set -e
sudo -n mv /tmp/coreeuler-*.service /etc/systemd/system/
sudo -n systemctl daemon-reload
sudo -n systemctl enable --now coreeuler-api.service coreeuler-tunnel.service
REMOTE

echo "API и туннель подняты. Агент новостей включается отдельно:"
echo "  ssh $HOST 'sudo -n systemctl enable --now coreeuler-news.service'"
