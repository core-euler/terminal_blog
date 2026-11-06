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

export type Topic = {
  /** Имя папки в разделе news. */
  name: string;
  count: number;
  /** Дата самой свежей новости темы. */
  latest: string;
};

const items = ((snapshot.items ?? []) as StaticNews[]).slice();

export const generatedAt = snapshot.generated_at as string | null;

export const allNews = (): StaticNews[] => items;

export const topicUrl = (topic: string): string => `/news/${encodeURIComponent(topic)}/`;

export const newsUrl = (news: StaticNews): string => `${topicUrl(news.topic)}${encodeURIComponent(news.slug)}/`;

export const findBySlug = (slug: string): StaticNews | undefined =>
  items.find((item) => item.slug === slug);

/** Темы, в которых есть новости. Порядок — по свежести последней новости. */
export const topics = (): Topic[] => {
  const grouped = new Map<string, Topic>();
  for (const item of items) {
    const known = grouped.get(item.topic);
    if (known) {
      known.count += 1;
      if (item.event_date > known.latest) known.latest = item.event_date;
    } else {
      grouped.set(item.topic, { name: item.topic, count: 1, latest: item.event_date });
    }
  }
  return [...grouped.values()].sort((a, b) => b.latest.localeCompare(a.latest) || a.name.localeCompare(b.name));
};

export const byTopic = (topic: string): StaticNews[] => items.filter((item) => item.topic === topic);

export const summary = (text: string, limit = 160): string => {
  const flat = text.replace(/\s+/g, ' ').trim();
  return flat.length > limit ? `${flat.slice(0, limit - 3).trimEnd()}…` : flat;
};

export const paragraphs = (text: string): string[] =>
  text
    .split(/\n{2,}/)
    .map((part) => part.replace(/\s*\n\s*/g, ' ').trim())
    .filter(Boolean);
