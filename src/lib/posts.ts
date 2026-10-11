import { getCollection, type CollectionEntry } from 'astro:content';

export type Post = CollectionEntry<'posts'>;

/** Страницы черновиков собираются только в dev. */
export const SHOW_DRAFT_PAGES = import.meta.env.DEV;

export const postUrl = (id: string) => `/posts/${id}/`;
export const tagUrl = (tag: string) => `/tags/${encodeURIComponent(tag)}/`;

const byDateDesc = (a: Post, b: Post) => b.data.date.valueOf() - a.data.date.valueOf();

/** Все посты, включая черновики. */
export async function getAllPosts() {
  return (await getCollection('posts')).sort(byDateDesc);
}

/** Посты для фида, RSS и тегов: без черновиков. */
export async function getPublishedPosts() {
  return (await getCollection('posts', ({ data }) => !data.draft)).sort(byDateDesc);
}

export const formatDate = (d: Date) => d.toISOString().slice(0, 10);

export function readingStats(body = '') {
  const words = body.replace(/```[\s\S]*?```/g, ' ').split(/\s+/).filter(Boolean).length;
  return { words, minutes: Math.max(1, Math.round(words / 180)) };
}
