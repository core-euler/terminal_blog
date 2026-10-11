---
title: "Пост как папка"
date: 2026-08-28
description: "Как устроены коллекции контента в этом блоге: одна папка на пост, картинки рядом с текстом и схема фронтматтера, которая роняет сборку."
tags: [astro, content]
draft: false
---

Каждый пост здесь — отдельная папка. Внутри лежит `index.md` и всё, что к нему относится: картинки, видео, иногда исходники. Удалить пост — значит удалить одну папку, и ничего не останется висеть в `public/`.

## Структура

```text
src/content/posts/
├── dev/
│   ├── content-collections/
│   │   └── index.md
│   └── neovim-as-a-blog/
│       ├── index.md
│       ├── fractal.png
│       ├── loop.mp4
│       └── palette.png
└── travel/
    └── autumn-in-tbilisi/
        ├── index.md
        └── old-town.jpg
```

Дерево в сайдбаре строится из этой же структуры рекурсивно, так что новая категория появляется в навигации сама.

## Схема

Фронтматтер проверяется через zod. Лишнее поле или дата, которую нельзя разобрать, — и сборка падает с понятной ошибкой, а не выкатывает страницу с `undefined` в заголовке.

```ts
const posts = defineCollection({
  loader: glob({ pattern: '**/index.md', base: './src/content/posts' }),
  schema: z.object({
    title: z.string().min(1),
    date: z.coerce.date(),
    description: z.string().min(1),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }).strict(),
});
```

Черновики помечаются `draft: true`. В дереве они видны с тильдой, как несохранённый файл, но в ленту и RSS не попадают.
