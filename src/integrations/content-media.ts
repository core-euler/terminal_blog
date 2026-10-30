import type { AstroIntegration } from 'astro';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { POSTS_DIR, PROJECTS_DIR } from '../site.config';

/**
 * Файлы, которые лежат рядом с index.md и не проходят через astro:assets:
 * видео в постах и готовые снимки в портфолио. Адрес страницы повторяет путь
 * папки, поэтому в markdown достаточно относительного `./loop.mp4`, а на
 * странице проекта — `./01.webp`.
 * В dev файлы отдаются middleware с поддержкой Range (Safari без неё не
 * играет mp4), при сборке копируются в dist.
 */
const MEDIA = new Map([
  ['.mp4', 'video/mp4'],
  ['.webm', 'video/webm'],
  ['.webp', 'image/webp'],
]);

/** Папка коллекции → префикс адреса, под которым живут её страницы. */
const ROOTS = [
  { dir: POSTS_DIR, url: '/posts/' },
  { dir: PROJECTS_DIR, url: '/portfolio/' },
];

export function contentMedia(): AstroIntegration {
  const roots = ROOTS.map((root) => ({ ...root, abs: '' }));

  return {
    name: 'content-media',
    hooks: {
      'astro:config:done': ({ config }) => {
        for (const root of roots) {
          root.abs = path.join(fileURLToPath(config.root), root.dir);
        }
      },

      'astro:server:setup': ({ server }) => {
        for (const root of roots) {
          server.middlewares.use(root.url, (req, res, next) => {
            const rel = decodeURIComponent((req.url ?? '').split('?')[0]);
            const type = MEDIA.get(path.extname(rel).toLowerCase());
            const file = path.join(root.abs, rel);
            if (!type || !file.startsWith(root.abs) || !fs.existsSync(file)) return next();

            const size = fs.statSync(file).size;
            const range = /bytes=(\d*)-(\d*)/.exec(req.headers.range ?? '');
            res.setHeader('Content-Type', type);
            res.setHeader('Accept-Ranges', 'bytes');

            if (!range) {
              res.setHeader('Content-Length', size);
              fs.createReadStream(file).pipe(res);
              return;
            }
            const start = range[1] ? Number(range[1]) : size - Number(range[2]);
            const end = range[1] && range[2] ? Math.min(Number(range[2]), size - 1) : size - 1;
            res.statusCode = 206;
            res.setHeader('Content-Range', `bytes ${start}-${end}/${size}`);
            res.setHeader('Content-Length', end - start + 1);
            fs.createReadStream(file, { start, end }).pipe(res);
          });
        }
      },

      'astro:build:done': ({ dir }) => {
        const dist = fileURLToPath(dir);
        for (const root of roots) {
          // Копируем только сами файлы: если копировать дерево целиком,
          // от папок без медиа (и от черновиков) останутся пустые каталоги,
          // а nginx на пустой каталог отвечает 403 вместо 404.
          const walk = (from: string) => {
            for (const entry of fs.readdirSync(from, { withFileTypes: true })) {
              const src = path.join(from, entry.name);
              if (entry.isDirectory()) {
                walk(src);
                continue;
              }
              if (!MEDIA.has(path.extname(entry.name).toLowerCase())) continue;
              const dest = path.join(dist, root.url, path.relative(root.abs, src));
              fs.mkdirSync(path.dirname(dest), { recursive: true });
              fs.copyFileSync(src, dest);
            }
          };
          if (fs.existsSync(root.abs)) walk(root.abs);
        }
      },
    },
  };
}
