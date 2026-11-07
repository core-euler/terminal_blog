import { CELL_W } from 'ascii-magic-art/runtime/canvas.js';
import { play } from 'ascii-magic-art/runtime/player.js';
import { asciiModules } from '../data/ascii-modules';
import { PANES } from '../data/ascii-panes';

/*
 * Пьеса в подвале боковой панели. Выбор случайный и делается в браузере:
 * при каждой загрузке страницы колонка показывает новую анимацию из своей
 * категории. Пьесы шире колонки, поэтому размер знака считается от ширины:
 * кадр ужимается целиком, без обрезки по краям.
 */

const MIN_SIZE = 1.5;

async function mount(host: HTMLElement) {
  if (host.dataset.mounted === '1') return;
  const pool = PANES[host.dataset.paneArt ?? ''] ?? [];
  if (pool.length === 0) return;

  const slug = pool[Math.floor(Math.random() * pool.length)];
  const load = asciiModules[slug];
  if (!load) return;

  host.dataset.piece = slug;
  const module = await load();
  const width = host.clientWidth - 16;
  if (width <= 0) {
    // Панель спрятана: на телефоне дерево — popover, он раскроется позже.
    host.closest('[popover]')?.addEventListener('toggle', () => void mount(host), { once: true });
    return;
  }
  host.dataset.mounted = '1';

  const frame = document.createElement('pre');
  frame.className = 'pane-art-frame';
  frame.setAttribute('aria-hidden', 'true');
  frame.style.margin = '0';
  frame.style.padding = '0 8px 8px';
  host.append(frame);

  // Ширина кадра в знаках переводится в пиксели: знак занимает CELL_W от кегля.
  // Пересчитываем на каждое изменение колонки: на телефоне панель раскрывается
  // уже после первой отрисовки и её ширина меняется.
  const fit = () => {
    const available = host.clientWidth - 16;
    if (available <= 0) return;
    frame.style.fontSize = `${Math.max(MIN_SIZE, available / (module.meta.cols * CELL_W)).toFixed(2)}px`;
  };
  fit();
  requestAnimationFrame(fit);
  new ResizeObserver(fit).observe(host);

  play(frame, module as never, { speed: 0.8, still: false });
}

document.querySelectorAll<HTMLElement>('[data-pane-art]').forEach((host) => {
  // Спрятанные пьесы не монтируем: на телефоне нижней анимации дерева нет.
  if (getComputedStyle(host).display === 'none') return;
  void mount(host);
});
