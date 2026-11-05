// Лента из снимка: читается на сборке, в рантайме к API не ходит.

import snapshot from '../data/news.json';

export type StaticSource = {
  url: string;
  title: string | null;
};

export type StaticNews = {
  slug: string;
  title: string;
  body: string;
  topic: string;
  event_date: string;
  published_at: string;
  sources: StaticSource[];
};

const items = ((snapshot.items ?? []) as StaticNews[]).slice();

export const generatedAt = snapshot.generated_at as string | null;

export const allNews = (): StaticNews[] => items;

export const findBySlug = (slug: string): StaticNews | undefined =>
  items.find((item) => item.slug === slug);

export const summary = (text: string, limit = 160): string => {
  const flat = text.replace(/\s+/g, ' ').trim();
  return flat.length > limit ? `${flat.slice(0, limit - 3).trimEnd()}…` : flat;
};

export const paragraphs = (text: string): string[] =>
  text
    .split(/\n{2,}/)
    .map((part) => part.replace(/\s*\n\s*/g, ' ').trim())
    .filter(Boolean);
