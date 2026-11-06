#!/usr/bin/env node
// Сборка и выкладка при изменении ленты. Запускается таймером на домашнем сервере:
// снимок уже собран в API, поэтому сборка нужна только когда опубликовано что-то новое.

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';

const api = (process.env.PUBLIC_API_BASE ?? 'http://127.0.0.1:8000/api').replace(/\/+$/, '');
const target = process.env.SITE_DEPLOY_TARGET ?? 'hidecore@213.176.113.167';
const remoteSite = process.env.SITE_REMOTE_DIR ?? '/home/hidecore/terminal-blog/site/';
const marker = process.env.SITE_MARKER ?? '.built-snapshot';

const run = (command, args) => {
  execFileSync(command, args, { stdio: 'inherit', env: process.env });
};

async function fetchPage() {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`${api}/news?limit=50`, { signal: controller.signal });
    if (!response.ok) throw new Error(`ответ ${response.status}`);
    return await response.json();
  } finally {
    clearTimeout(timer);
  }
}

const page = await fetchPage();
const items = Array.isArray(page.items) ? page.items : [];
const fingerprint = createHash('sha256')
  .update(items.map((item) => `${item.slug}:${item.published_at}`).join('\n'))
  .digest('hex');

const previous = existsSync(marker) ? readFileSync(marker, 'utf8').trim() : '';
if (previous === fingerprint) {
  console.log(`лента без изменений: ${items.length}`);
  process.exit(0);
}

run('node', ['scripts/fetch-news.mjs']);
run('npx', ['astro', 'build']);
run('rsync', ['-az', '--delete', 'dist/', `${target}:${remoteSite}`]);
run('ssh', [target, 'docker exec blog-nginx nginx -c /nginx/nginx.conf -s reload']);

writeFileSync(marker, `${fingerprint}\n`, 'utf8');
console.log(`опубликовано: ${items.length} новостей`);
