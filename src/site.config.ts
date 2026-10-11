export const SITE = {
  title: '~/blog',
  description: 'Заметки о вебе, инструментах и путешествиях.',
  lang: 'ru',
  author: {
    name: 'Алекс Морозов',
    note: 'Фронтенд-разработчик. Пишу про инструменты, типографику и медленные путешествия.',
    url: 'https://example.com/',
  },
} as const;

/** Папка коллекции постов: из неё же строится дерево в сайдбаре. */
export const POSTS_DIR = 'src/content/posts';
