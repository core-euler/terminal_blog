import { play } from 'ascii-magic-art/runtime/player.js';
import { asciiModules } from '../data/ascii-modules';

/*
 * Оживление ASCII-арта: кадр, снятый на сборке, заменяется анимацией.
 * Размер знака подбирается под ширину блока, чтобы кадр влезал целиком.
 */

type Fitted = { pre: HTMLPreElement; unit: number; max: number };

const fitted = new Map<HTMLElement, Fitted>();
const MIN_SIZE = 3;

/** Сам <pre> или вложенный в фигуру. */
const preOf = (element: HTMLElement) =>
  element.matches('pre') ? (element as HTMLPreElement) : element.querySelector('pre');

function fit(container: HTMLElement) {
  const state = fitted.get(container);
  if (!state) return;
  const available = container.clientWidth || container.getBoundingClientRect().width;
  if (!available || !state.unit) return;
  const size = Math.max(MIN_SIZE, Math.min(state.max, available / state.unit));
  state.pre.style.fontSize = `${size.toFixed(2)}px`;
}

/** Ширина кадра на единицу размера шрифта: снимается с текста до анимации. */
function measure(pre: HTMLPreElement): Omit<Fitted, 'pre'> {
  const max = parseFloat(getComputedStyle(pre).fontSize) || 12;
  pre.style.fontSize = '10px';
  const width = pre.scrollWidth;
  pre.style.fontSize = '';
  return { unit: width > 0 ? width / 10 : 0, max };
}

async function setup(container: HTMLElement) {
  if (fitted.has(container)) return;
  const load = asciiModules[container.dataset.piece ?? ''];
  const pre = preOf(container);
  if (!load || !pre) return;

  fitted.set(container, { pre, ...measure(pre) });
  fit(container);

  const module = await load();
  // Дальше движением управляет сам проигрыватель: он держит кадр, пока фигура
  // на экране, и останавливается за его пределами.
  play(pre, module as never, { speed: Number(container.dataset.speed ?? 1), still: false });
}

let pending = 0;
addEventListener('resize', () => {
  cancelAnimationFrame(pending);
  pending = requestAnimationFrame(() => fitted.forEach((_, container) => fit(container)));
});

export function mountAsciiArt() {
  document.querySelectorAll<HTMLElement>('[data-ascii]').forEach((container) => void setup(container));
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', mountAsciiArt, { once: true });
} else {
  mountAsciiArt();
}
