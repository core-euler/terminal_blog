import { play } from 'ascii-magic-art/runtime/player.js';
import { asciiModules } from '../data/ascii-modules';

/*
 * Оживление ASCII-арта: кадр, снятый на сборке, заменяется анимацией.
 * Размер знака подбирается под ширину блока, чтобы кадр влезал целиком.
 */

type Fitted = { pre: HTMLPreElement; unit: number; max: number };

const mounted = new Map<HTMLElement, Fitted>();
const started = new WeakSet<HTMLElement>();
const MIN_SIZE = 3;

function fit(figure: HTMLElement) {
  const state = mounted.get(figure);
  if (!state) return;
  const available = figure.clientWidth || figure.getBoundingClientRect().width;
  if (!available || !state.unit) return;
  const size = Math.max(MIN_SIZE, Math.min(state.max, available / state.unit));
  state.pre.style.fontSize = `${size.toFixed(2)}px`;
}

/** Ширина кадра на единицу размера шрифта: снимается с текста до анимации. */
function measure(pre: HTMLPreElement) {
  pre.style.fontSize = '10px';
  const width = pre.scrollWidth;
  return width > 0 ? width / 10 : 0;
}

async function mount(figure: HTMLElement) {
  if (started.has(figure)) return;
  const load = asciiModules[figure.dataset.piece ?? ''];
  const pre = figure.querySelector('pre');
  if (!load || !pre) return;
  started.add(figure);
  const max = parseFloat(getComputedStyle(figure).getPropertyValue('--ascii-size')) || 12;
  mounted.set(figure, { pre, unit: measure(pre), max });
  fit(figure);
  const module = await load();
  const stop = play(pre, module as never, { speed: Number(figure.dataset.speed ?? 1) });
  // Кадр замирает, когда арт уходит с экрана: не жжём батарею в фоне.
  new IntersectionObserver((entries) => {
    for (const entry of entries) if (!entry.isIntersecting) stop();
  }).observe(figure);
}

let pending = 0;
addEventListener('resize', () => {
  cancelAnimationFrame(pending);
  pending = requestAnimationFrame(() => mounted.forEach((_, figure) => fit(figure)));
});

export function mountAsciiArt() {
  document.querySelectorAll<HTMLElement>('[data-ascii]').forEach((figure) => void mount(figure));
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', mountAsciiArt, { once: true });
} else {
  mountAsciiArt();
}
