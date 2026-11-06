#!/bin/sh
# Сборка сайта на домашнем сервере: исходники, зависимости, таймер выкладки.
# Запускается с машины разработчика. Конфиг nginx остаётся за deploy.sh.
set -e

HOST=${HOST:-local}
DIR=coreeuler/site

ssh $HOST "mkdir -p ~/$DIR"
rsync -az --delete --exclude node_modules --exclude dist --exclude .git --exclude .astro \
  --exclude .tmp --exclude .built-snapshot \
  ./ $HOST:~/$DIR/

scp -q deploy/home/coreeuler-site.service deploy/home/coreeuler-site.timer $HOST:/tmp/

ssh $HOST 'bash -s' <<REMOTE
set -e
cd ~/$DIR
PATH=/opt/node22/bin:$PATH
[ -d node_modules ] || npm ci --no-audit --no-fund >/dev/null
sudo -n mv /tmp/coreeuler-site.service /etc/systemd/system/coreeuler-site.service
sudo -n mv /tmp/coreeuler-site.timer /etc/systemd/system/coreeuler-site.timer
sudo -n systemctl daemon-reload
sudo -n systemctl enable --now coreeuler-site.timer >/dev/null 2>&1
systemctl is-active coreeuler-site.timer
REMOTE
