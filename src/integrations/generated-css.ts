import type { AstroIntegration } from 'astro';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { rewriteTokens, tokenCss } from '../lib/code-tokens';
import { themesCss } from '../styles/themes';

/*
 * Палитры тем и цвета токенов одинаковы на всех страницах, а нужны до первой
 * отрисовки. Поэтому они собираются в один файл: в dev его отдаёт middleware,
 * при сборке — файл в корне сайта, который браузер берёт из кэша.
 *
 * Цвета токенов при сборке переезжают из атрибутов в классы прямо в готовых
 * страницах: правила известны только после того, как страницы отрисованы.
 */
const FILE = 'shiki.css';

function pages(dir: string): string[] {
  const found: string[] = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) found.push(...pages(full));
    else if (entry.name.endsWith('.html')) found.push(full);
  }
  return found;
}

export function generatedCss(): AstroIntegration {
  return {
    name: 'generated-css',
    hooks: {
      'astro:server:setup': ({ server }) => {
        server.middlewares.use((req, res, next) => {
          if ((req.url ?? '').split('?')[0] !== `/${FILE}`) return next();
          res.setHeader('Content-Type', 'text/css; charset=utf-8');
          res.end(themesCss());
        });
      },

      'astro:build:done': ({ dir }) => {
        const root = fileURLToPath(dir);
        const rules = new Map<string, string>();
        for (const file of pages(root)) {
          const html = fs.readFileSync(file, 'utf-8');
          const rewritten = rewriteTokens(html, rules);
          if (rewritten !== html) fs.writeFileSync(file, rewritten);
        }
        fs.writeFileSync(path.join(root, FILE), themesCss() + tokenCss(rules));
      },
    },
  };
}
