#!/usr/bin/env node
// Каталог анимированных ASCII-пьес для сайта: только разрешённые категории.
// Источник — пакет ascii-magic-art; запускается при изменении версии пакета.

import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = 'node_modules/ascii-magic-art';
const allowed = new Set([
  'screens',
  'live-data',
  'explainers',
  'algorithms',
  'demoscene',
  'frames',
  'retro',
  'empty-states',
  'solids',
  'motion-lab',
]);

const names = Object.fromEntries(
  JSON.parse(readFileSync(join(root, 'categories.json'), 'utf8')).map((category) => [category.id, category.name]),
);

const field = (source, key) => {
  const match = source.match(new RegExp(`${key}:\\s*"([^"]*)"`));
  return match ? match[1] : '';
};

const pieces = readdirSync(join(root, 'pieces'))
  .filter((file) => file.endsWith('.js'))
  .map((file) => {
    const source = readFileSync(join(root, 'pieces', file), 'utf8');
    return {
      slug: file.slice(0, -3),
      name: field(source, 'name'),
      category: field(source, 'category'),
      note: field(source, 'note'),
    };
  })
  .filter((piece) => allowed.has(piece.category))
  .sort((a, b) => a.category.localeCompare(b.category) || a.slug.localeCompare(b.slug));

writeFileSync(
  'src/data/ascii-pieces.json',
  `${JSON.stringify(
    pieces.map((piece) => ({ ...piece, categoryName: names[piece.category] ?? piece.category })),
    null,
    2,
  )}\n`,
  'utf8',
);

const counts = pieces.reduce((acc, piece) => acc.set(piece.category, (acc.get(piece.category) ?? 0) + 1), new Map());
console.log(`пьес в каталоге: ${pieces.length}`);
for (const [category, count] of counts) console.log(`  ${category}: ${count}`);
