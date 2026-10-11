import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';
import { POSTS_DIR } from './site.config';

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

export const collections = { posts };
