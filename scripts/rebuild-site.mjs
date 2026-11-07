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

const run = (command, args, options = {}) => {
  execFileSync(command, args, { stdio: 'inherit', env: process.env, ...options });
};

const capture = (command, args) =>
  execFileSync(command, args, { encoding: 'utf8', env: process.env }).trim();

/*
 * Эта копия — только для сборки, правок в ней не бывает. Перед сборкой
 * приводим её к состоянию репозитория: иначе на сайт уедет версия,
 * которую в последний раз выложили руками.
 */
function syncSource() {
  const before = capture('git', ['rev-parse', 'HEAD']);
  try {
    run('git', ['fetch', '--prune', '--quiet', 'origin']);
    run('git', ['reset', '--hard', '--quiet', 'origin/main']);
  } catch {
    // Связи с репозиторием нет: собираем то, что уже лежит, иначе новости
    // не выйдут вовсе из-за недоступного GitHub.
    console.log('код: репозиторий недоступен, собираем текущую копию');
  }
  const after = capture('git', ['rev-parse', 'HEAD']);
  const changed = before === after ? '' : capture('git', ['diff', '--name-only', before, after]);
  console.log(`код: ${after.slice(0, 7)}${changed ? `, изменено файлов ${changed.split('\n').length}` : ''}`);

  // Зависимости ставятся заново только когда менялся замок или их нет вовсе.
  if (changed.split('\n').includes('package-lock.json') || !existsSync('node_modules')) {
    run('npm', ['ci', '--no-audit', '--no-fund']);
  }
  return after;
}

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

// Сборка нужна, если изменилась лента или сам код в репозитории.
const commit = syncSource();
const stamp = `${commit} ${fingerprint}`;
const previous = existsSync(marker) ? readFileSync(marker, 'utf8').trim() : '';
if (previous === stamp) {
  console.log(`лента без изменений: ${items.length}`);
  process.exit(0);
}

run('node', ['scripts/fetch-news.mjs']);
run('npx', ['astro', 'build']);
// Ассеты живут дольше одной сборки: открытая вкладка держит старый HTML.
run('rsync', ['-az', '--delete', '--exclude=/\_astro', 'dist/', `${target}:${remoteSite}`]);
run('rsync', ['-az', 'dist/_astro/', `${target}:${remoteSite}/_astro/`]);
run('ssh', [target, `find ${remoteSite}/_astro -type f -mtime +7 -delete`]);
run('ssh', [target, 'docker exec blog-nginx nginx -c /nginx/nginx.conf -s reload']);

writeFileSync(marker, `${stamp}\n`, 'utf8');
console.log(`опубликовано: ${items.length} новостей`);
