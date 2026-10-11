import type { MdastPluginDefinition } from 'satteri';
import { TEXT_COLORS } from '../styles/themes';

/*
 * Цвет в постах, который следует за темой.
 *
 *   Текст :red[красным] и :dim[приглушённо].
 *
 *   ```ascii wave alt="Кот"
 *    /\_/\
 *   ( :yellow[o].:yellow[o] )
 *   ```
 *
 * Внутри ```ascii работает та же запись :цвет[...]; внутри цветного куска
 * `]` пишется как `\]`, а `\` — как `\\`. Слова в meta включают анимацию (wave, pulse, blink), строка `%%`
 * делит арт на кадры (fps=N — скорость), alt="…" — описание для скринридеров.
 */

const COLORS = new Set<string>(TEXT_COLORS);
const EFFECTS = new Set(['wave', 'pulse', 'blink']);
const FRAME_SEPARATOR = /^%%[ \t]*$/m;

const escapeHtml = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/** `:red[...]` внутри ASCII-арта → <span class="c-red">. */
function colorize(src: string): string {
  let html = '';
  let last = 0;
  for (const m of src.matchAll(/:([a-z]+)\[((?:\\.|[^\]\\])*)\]/g)) {
    if (!COLORS.has(m[1])) continue;
    html += escapeHtml(src.slice(last, m.index));
    html += `<span class="c-${m[1]}">${escapeHtml(m[2].replace(/\\(.)/g, '$1'))}</span>`;
    last = m.index! + m[0].length;
  }
  return html + escapeHtml(src.slice(last));
}

function parseMeta(meta: string) {
  const attrs: Record<string, string> = {};
  const words: string[] = [];
  for (const m of meta.matchAll(/([a-z]+)=(?:"([^"]*)"|(\S+))|(\S+)/g)) {
    if (m[4]) words.push(m[4]);
    else attrs[m[1]] = m[2] ?? m[3];
  }
  return { attrs, words };
}

function asciiBlock(value: string, meta: string): string {
  const { attrs, words } = parseMeta(meta);
  const effects = words.filter((w) => EFFECTS.has(w));
  const frames = value.split(FRAME_SEPARATOR).map((f) => f.replace(/^\n|\n$/g, ''));
  const a11y = attrs.alt ? ` role="img" aria-label="${escapeHtml(attrs.alt)}"` : ' aria-hidden="true"';
  const classes = ['ascii', 'ln', ...effects.map((e) => `ascii-${e}`)].join(' ');

  if (frames.length === 1) {
    return `<pre class="${classes}"${a11y}>${colorize(frames[0])}</pre>`;
  }

  // Кадры одной высоты стоят столбиком; CSS прокручивает их steps(N) — без JS.
  const rows = Math.max(...frames.map((f) => f.split('\n').length));
  const padded = frames.map((f) => f + '\n'.repeat(rows - f.split('\n').length));
  const fps = Math.min(30, Math.max(1, Number(attrs.fps) || 6));
  const style = `--frames:${frames.length};--rows:${rows};--frame-time:${(1 / fps).toFixed(3)}s`;
  const reel = padded.map((f) => colorize(f)).join('\n');
  return `<pre class="${classes} ascii-frames"${a11y} style="${style}"><span class="ascii-reel">${reel}</span></pre>`;
}

export const postMarkup: MdastPluginDefinition = {
  name: 'post-markup',

  textDirective(node, ctx) {
    if (COLORS.has(node.name)) {
      ctx.setProperty(node, 'data', { hName: 'span', hProperties: { className: [`c-${node.name}`] } });
      return;
    }
    // Не наша директива (например, «в 10:30» или «см.:tip») — возвращаем как было.
    const label = node.children.length ? `[${ctx.textContent(node)}]` : '';
    return { type: 'text', value: `:${node.name}${label}` };
  },

  code(node) {
    if (node.lang !== 'ascii') return;
    return { type: 'html', value: asciiBlock(node.value, node.meta ?? '') };
  },
};
