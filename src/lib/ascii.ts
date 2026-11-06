import pools from './ascii-pools.json';
import frames from '../data/ascii-frames.json';

/*
 * Подбор ASCII-арта для статьи.
 *
 * Тема статьи (теги поста, тема новости) переводится в набор пьес одного
 * смысла: про базы — таблицы, про железо — платы и датчики. Из набора пьеса
 * выбирается по отпечатку слага, поэтому одна и та же статья всегда получает
 * одну и ту же пьесу, а соседние статьи — разные.
 *
 * Кадр берётся из снимка, снятого скриптом: он же остаётся в разметке без
 * скриптов и при reduced motion.
 */

/** Отпечаток строки: устойчив между сборками и не зависит от платформы. */
export function fingerprint(value: string): number {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function pool(themes: string[]): string[] {
  const picked: string[] = [];
  for (const theme of themes) {
    const list = (pools.byTheme as Record<string, string[]>)[theme.toLowerCase()];
    if (list) picked.push(...list);
  }
  return picked.length > 0 ? [...new Set(picked)] : pools.fallback;
}

/** Пьеса для статьи: по тегам и теме, при нехватке — общий набор. */
export function pieceFor(themes: string[], seed: string): string {
  const candidates = pool(themes);
  return candidates[fingerprint(seed) % candidates.length];
}

/** Разделитель смысловых частей. */
export function dividerFor(seed: string): string {
  return pools.dividers[fingerprint(seed) % pools.dividers.length];
}

/*
 * Пьеса из категории каталога. Нужна там, где тема не привязана к тексту:
 * например, раздел сайта берёт верхнюю пьесу из тел, нижнюю — из схем.
 */
export function pieceFromCategory(category: string, seed: string): string {
  const list = (pools.categories as Record<string, string[]>)[category];
  const candidates = list && list.length > 0 ? list : pools.fallback;
  return candidates[fingerprint(seed) % candidates.length];
}

const snapshot = frames as Record<string, string>;

/** Кадр пьесы, снятый на сборке. Неизвестная пьеса — пустая строка. */
export function frameOf(slug: string): string {
  return snapshot[slug] ?? '';
}
