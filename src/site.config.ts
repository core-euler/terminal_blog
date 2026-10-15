export const SITE = {
  /** Как сайт называется в интерфейсе: таб, дерево, statusline. */
  title: '~/blog',
  /** Как сайт называется в поисковой выдаче и в превью ссылок. */
  seoTitle: 'Николай Носков — блог о разработке, LLM и IoT',
  /** Короткое имя для суффикса в <title> внутренних страниц. */
  shortTitle: 'coreeuler.art',
  description: 'Заметки о разработке: Python, LLM-интеграции, IoT.',
  /** Картинка для превью ссылок, 1200×630. */
  ogImage: '/og.png',
  lang: 'ru',
  locale: 'ru_RU',
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
