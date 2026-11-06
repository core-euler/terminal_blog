#!/usr/bin/env node
// Список пьес, которые сайт умеет показывать: статический импорт для каждой.
// Источник — src/lib/ascii-pools.json; запускать после правки пулов.

import { readFileSync, writeFileSync } from 'node:fs';

const pools = JSON.parse(readFileSync('src/lib/ascii-pools.json', 'utf8'));
const slugs = [...new Set([...pools.dividers, ...pools.fallback, ...Object.values(pools.byTheme).flat()])].sort();

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
