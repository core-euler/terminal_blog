#!/usr/bin/env node
// Снимок ленты для сборки: сайт остаётся статическим, бэк в момент показа не нужен.

import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';

const target = 'src/data/news.json';
const base = (process.env.PUBLIC_API_BASE ?? 'http://127.0.0.1:8090/api').replace(/\/+$/, '');
// API отдаёт не больше 50 записей за раз.
const limit = Math.min(Number(process.env.NEWS_SNAPSHOT_LIMIT ?? 50), 50);

async function existing() {
  try {
    return JSON.parse(await readFile(target, 'utf8'));
  } catch {
    return null;
  }
}

async function save(snapshot) {
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, `${JSON.stringify(snapshot, null, 2)}\n`, 'utf8');
}

const previous = await existing();

try {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  const response = await fetch(`${base}/news?limit=${limit}`, { signal: controller.signal });
  clearTimeout(timer);
  if (!response.ok) throw new Error(`ответ ${response.status}`);
  const page = await response.json();
  if (!Array.isArray(page.items)) throw new Error('в ответе нет списка новостей');

  await save({
    generated_at: new Date().toISOString(),
    items: page.items.map((item) => ({ ...item, sources: item.sources ?? [] })),
  });
  console.log(`снимок ленты: ${page.items.length}`);
} catch (error) {
  if (previous) {
    console.log(`бэк недоступен (${error.message}), оставляю прошлый снимок: ${previous.items?.length ?? 0}`);
  } else {
    await save({ generated_at: null, items: [] });
    console.log(`бэк недоступен (${error.message}), лента пустая до следующей сборки`);
  }
}
