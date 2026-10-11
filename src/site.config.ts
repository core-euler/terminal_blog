export const SITE = {
  title: '~/blog',
  description: 'Заметки о разработке: Python, LLM-интеграции, IoT.',
  lang: 'ru',
  author: {
    name: 'Николай Носков',
    note: 'Backend-разработчик: Python, LLM-интеграции, IoT. Петрозаводск.',
    url: 'https://t.me/CoreEuler',
    links: [
      { label: 'telegram', href: 'https://t.me/CoreEuler' },
      { label: 'kwork', href: 'https://kwork.ru/user/coreeuler' },
      { label: 'habr', href: 'https://habr.com/ru/users/okoloboga/' },
    ],
  },
} as const;

/** Папка коллекции постов: из неё же строится дерево в сайдбаре. */
export const POSTS_DIR = 'src/content/posts';
