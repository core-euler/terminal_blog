#!/usr/bin/env node
// Список пьес, которые сайт умеет показывать: статический импорт для каждой.
// Источники — src/lib/ascii-pools.json и прямые ссылки в разметке; запускать
// после правки пулов или появления новой пьесы в страницах.

import { readFileSync, writeFileSync } from 'node:fs';
import { readdirSync } from 'node:fs';
import { join } from 'node:path';

const pools = JSON.parse(readFileSync('src/lib/ascii-pools.json', 'utf8'));

/** Пьесы, названные в разметке и скриптах напрямую. */
function namedInSource(dir) {
  const found = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) {
      found.push(...namedInSource(path));
      continue;
    }
    if (!/\.(astro|ts)$/.test(entry.name)) continue;
    for (const match of readFileSync(path, 'utf8').matchAll(/(?:piece|piece=)["'=]?\{?["']([a-z0-9-]+)["']/g)) found.push(match[1]);
  }
  return found;
}

const slugs = [
  ...new Set([
    ...pools.dividers,
    ...pools.fallback,
    ...Object.values(pools.byTheme).flat(),
    ...namedInSource('src'),
  ]),
].sort();

const lines = slugs.map((slug) => `  '${slug}': () => import('ascii-magic-art/pieces/${slug}.js'),`);
const source = `// Сгенерировано scripts/build-ascii-modules.mjs. Руками не править.
export const asciiModules: Record<string, () => Promise<{ default: () => (t: number) => unknown }>> = {
${lines.join('\n')}
};
`;

writeFileSync('src/data/ascii-modules.ts', source, 'utf8');

// Первый кадр каждой пьесы: он попадает в разметку, поэтому читается без
// динамического импорта — тот внутри markdown-плагина недоступен.
const frames = {};
for (const slug of slugs) {
  const module = await import(`ascii-magic-art/pieces/${slug}.js`);
  const frame = module.default()(0);
  frames[slug] = typeof frame === 'string' ? frame : String(frame?.text ?? '');
}
writeFileSync('src/data/ascii-frames.json', `${JSON.stringify(frames)}\n`, 'utf8');

console.log(`пьес в сборке: ${slugs.length}, кадров снято: ${Object.keys(frames).length}`);
