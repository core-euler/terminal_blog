// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { postMedia } from './src/integrations/post-media.ts';
import { generatedCss } from './src/integrations/generated-css.ts';
import { satteri } from '@astrojs/markdown-satteri';
import { shikiThemes } from './src/styles/themes.ts';
import { postMarkup } from './src/lib/markdown-color.ts';

export default defineConfig({
  site: 'https://coreeuler.art',
  trailingSlash: 'always',
  // Тулбар Astro в dev перекрывает statusline, а островов для инспекции тут нет.
  devToolbar: { enabled: false },
  // Карта сайта: черновики в неё не попадают, служебный 404 тоже.
  integrations: [
    postMedia(),
    generatedCss(),
    sitemap({
      filter: (page) => !page.endsWith('/404/') && !page.includes('/tags/черновик'),
      changefreq: 'monthly',
      serialize(item) {
        item.priority = item.url === 'https://coreeuler.art/' ? 1 : 0.7;
        return item;
      },
    }),
  ],
  markdown: {
    // Директивы нужны для :red[...]; ```ascii обрабатывает тот же плагин.
    processor: satteri({ features: { directive: true }, mdastPlugins: [postMarkup] }),
    // Цвета всех тем попадают в разметку как --shiki-<id>, переключает их CSS.
    shikiConfig: { themes: shikiThemes, defaultColor: false },
  },
});
