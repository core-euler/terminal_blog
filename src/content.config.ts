import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';
import { POSTS_DIR, PROJECTS_DIR } from './site.config';

const posts = defineCollection({
  // Пост — это папка: <категория>/<слаг>/index.md, медиа лежат рядом.
  loader: glob({
    pattern: '**/index.md',
    base: `./${POSTS_DIR}`,
    generateId: ({ entry }) => entry.replace(/\/index\.md$/, ''),
  }),
  schema: z.object({
    title: z.string().min(1),
    date: z.coerce.date(),
    description: z.string().min(1),
    tags: z.array(z.string().min(1)).default([]),
    draft: z.boolean().default(false),
  }).strict(),
});

const projects = defineCollection({
  // Проект — тоже папка: <категория>/<слаг>/index.md, снимки лежат рядом.
  loader: glob({
    pattern: '**/index.md',
    base: `./${PROJECTS_DIR}`,
    generateId: ({ entry }) => entry.replace(/\/index\.md$/, ''),
  }),
  schema: z.object({
    title: z.string().min(1),
    /** Одна строка для карточки и метаописания. */
    summary: z.string().min(1),
    role: z.string().min(1),
    stack: z.array(z.string().min(1)).default([]),
    /** Сколько заняло, свободным текстом: «3 месяца», «200 часов». */
    period: z.string().optional(),
    /** Что получилось в итоге. */
    result: z.string().optional(),
    /** Снимок для карточки в оглавлении. Остальные идут в тексте по порядку. */
    cover: z.string().min(1),
    links: z.array(z.object({ label: z.string().min(1), href: z.string().url() })).default([]),
    /** Порядок в категории, по возрастанию. */
    order: z.number().default(100),
  }).strict(),
});

export const collections = { posts, projects };
