// @ts-check
import { defineConfig } from 'astro/config';
import { postMedia } from './src/integrations/post-media.ts';
import { satteri } from '@astrojs/markdown-satteri';
import { shikiThemes } from './src/styles/themes.ts';
import { postMarkup } from './src/lib/markdown-color.ts';

export default defineConfig({
  site: 'https://coreeuler.art',
  trailingSlash: 'always',
  // Тулбар Astro в dev перекрывает statusline, а островов для инспекции тут нет.
  devToolbar: { enabled: false },
  integrations: [postMedia()],
  markdown: {
    // Директивы нужны для :red[...]; ```ascii обрабатывает тот же плагин.
    processor: satteri({ features: { directive: true }, mdastPlugins: [postMarkup] }),
    // Цвета всех тем попадают в разметку как --shiki-<id>, переключает их CSS.
    shikiConfig: { themes: shikiThemes, defaultColor: false },
  },
});
