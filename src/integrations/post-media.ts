import type { AstroIntegration } from 'astro';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { POSTS_DIR } from '../site.config';

/**
 * Видео (и прочие файлы, которые astro:assets не обрабатывает) лежат рядом
 * с index.md. URL поста повторяет путь папки (/posts/<кат>/<слаг>/), поэтому
 * в markdown достаточно относительного `<video src="./loop.mp4">`.
 * В dev файлы отдаются middleware с поддержкой Range (Safari без неё не
 * играет mp4), при сборке — копируются в dist/posts/.
 */
const MEDIA = new Map([
  ['.mp4', 'video/mp4'],
  ['.webm', 'video/webm'],
]);

export function postMedia(): AstroIntegration {
  let postsRoot = '';

  return {
    name: 'post-media',
    hooks: {
      'astro:config:done': ({ config }) => {
        postsRoot = path.join(fileURLToPath(config.root), POSTS_DIR);
      },

      'astro:server:setup': ({ server }) => {
        server.middlewares.use('/posts/', (req, res, next) => {
          const rel = decodeURIComponent((req.url ?? '').split('?')[0]);
          const type = MEDIA.get(path.extname(rel).toLowerCase());
          const file = path.join(postsRoot, rel);
          if (!type || !file.startsWith(postsRoot) || !fs.existsSync(file)) return next();

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
      },

      'astro:build:done': ({ dir }) => {
        const out = path.join(fileURLToPath(dir), 'posts');
        fs.cpSync(postsRoot, out, {
          recursive: true,
          filter: (src) =>
            fs.statSync(src).isDirectory() || MEDIA.has(path.extname(src).toLowerCase()),
        });
      },
    },
  };
}
