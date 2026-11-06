import type { MdastPluginDefinition } from 'satteri';
import { dividerFor, frameOf, pieceFor } from './ascii';

/*
 * Арт в постах: подпись к статье и разделители смысловых частей.
 *
 * Пьесу выбирает сайт, а не автор: тема берётся из тегов, рисунок — из пулов.
 * Разделитель ставится перед каждым заголовком второго уровня, кроме первого,
 * поэтому граница частей видна без разметки в тексте.
 */

const escape = (value: string) =>
  value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/** Теги из блока frontmatter: `tags: [ml, python]` или `tags:\n  - ml`. */
function tagsOf(frontmatter: string): string[] {
  const inline = frontmatter.match(/^tags:\s*\[(.*)\]/m);
  if (inline) {
    return inline[1]
      .split(',')
      .map((tag) => tag.trim().replace(/^["']|["']$/g, ''))
      .filter(Boolean);
  }
  const list = frontmatter.match(/^tags:\s*\n((?:\s*-\s*.+\n?)+)/m);
  if (!list) return [];
  return list[1]
    .split('\n')
    .map((line) => line.replace(/^\s*-\s*/, '').trim().replace(/^["']|["']$/g, ''))
    .filter(Boolean);
}

const articleArt = (frame: string, slug: string) =>
  `<figure class="ascii-figure" data-ascii data-piece="${slug}" style="--ascii-size:13px">` +
  `<pre class="ascii-art">${escape(frame)}</pre></figure>`;

const ruleArt = (frame: string, slug: string) =>
  `<pre class="ascii-rule" data-ascii data-piece="${slug}" style="--ascii-size:10px">${escape(frame)}</pre>`;

export const asciiArt: MdastPluginDefinition = {
  name: 'ascii-art',

  before(root, ctx) {
    // Astro снимает frontmatter до плагина и кладёт его в общий набор данных.
    const data = (ctx.data as { astro?: { frontmatter?: { tags?: unknown } } }).astro;
    const given = data?.frontmatter?.tags;
    const tags = Array.isArray(given)
      ? given.map((tag) => String(tag))
      : typeof given === 'string'
        ? given.split(',').map((tag) => tag.trim())
        : tagsOf(
            (root.children.find((child) => child.type === 'yaml') as { value?: string } | undefined)?.value ?? '',
          );
    const seed = ctx.fileURL?.pathname ?? tags.join('-');

    const piece = pieceFor(tags, seed);
    const frame = frameOf(piece);
    if (frame) {
      // Подпись к статье — после вводного абзаца.
      const intro = root.children.find((child) => child.type === 'paragraph');
      if (intro) ctx.insertAfter(intro, { type: 'html', value: articleArt(frame, piece) } as never);
    }

    const divider = dividerFor(seed);
    const rule = frameOf(divider);
    if (!rule) return;
    const headings = root.children.filter(
      (child) => child.type === 'heading' && (child as { depth?: number }).depth === 2,
    );
    for (const heading of headings.slice(1)) {
      ctx.insertBefore(heading, { type: 'html', value: ruleArt(rule, divider) } as never);
    }
  },
};
