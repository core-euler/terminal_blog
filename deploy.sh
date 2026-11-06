#!/bin/sh
# Сборка и публикация блога: файлы и конфиг nginx уезжают на VPS.
set -e

npm run build

# Ассеты не удаляем сразу: у открытых вкладок ещё старый HTML, и он просит
# прежние имена файлов. Хвост старше недели убираем.
rsync -az --delete --exclude=/_astro dist/ hidecore:/home/hidecore/terminal-blog/site/
rsync -az dist/_astro/ hidecore:/home/hidecore/terminal-blog/site/_astro/
ssh hidecore 'find /home/hidecore/terminal-blog/site/_astro -type f -mtime +7 -delete'
rsync -az deploy/nginx.conf hidecore:/home/hidecore/terminal-blog/nginx/nginx.conf
ssh hidecore 'docker exec blog-nginx nginx -t -c /nginx/nginx.conf && docker exec blog-nginx nginx -c /nginx/nginx.conf -s reload'

echo "Опубликовано: https://coreeuler.art/"

# Локальное превью на домашнем сервере: ./deploy.sh --local
if [ "${1:-}" = "--local" ]; then
  rsync -az --delete --rsync-path="sudo rsync" dist/ local:/var/www/terminal-blog/
  echo "Превью: http://192.168.0.123/"
fi
