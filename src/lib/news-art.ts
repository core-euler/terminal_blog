import { dividerFor, frameOf, pieceFor } from './ascii';

/*
 * Раскладка тела новости с артом.
 *
 * Автор делит текст на смысловые части строкой `---`: между частями встаёт
 * разделитель, после первой — пьеса по теме новости. Если деления нет, а
 * абзацев много, части делятся пополам: разделитель должен быть всегда.
 */

export type NewsBlock =
  | { kind: 'text'; paragraphs: string[] }
  | { kind: 'rule'; frame: string }
  | { kind: 'piece'; slug: string; frame: string };

const isSeparator = (line: string) => /^-{3,}\s*$/.test(line.trim());

/** Абзацы тела, разрезанные на смысловые части. */
function parts(body: string): string[][] {
  const result: string[][] = [];
  let current: string[][] = [[]];
  let buffer: string[] = [];

  const flushParagraph = () => {
    const text = buffer.join('\n').trim();
    if (text) current[current.length - 1].push(text);
    buffer = [];
  };

  for (const line of body.split('\n')) {
    if (isSeparator(line)) {
      flushParagraph();
      current.push([]);
      continue;
    }
    if (line.trim() === '') {
      flushParagraph();
      continue;
    }
    buffer.push(line);
  }
  flushParagraph();

  const cleaned = current.map((part) => part.filter(Boolean)).filter((part) => part.length > 0);
  if (cleaned.length > 0) result.push(...cleaned);

  // Частей нет, а текст длинный — делим пополам, чтобы разделитель был виден.
  if (result.length === 1 && result[0].length >= 6) {
    const half = Math.ceil(result[0].length / 2);
    return [result[0].slice(0, half), result[0].slice(half)];
  }
  return result;
}

/** Последовательность блоков для страницы новости. */
export function newsBlocks(news: { slug: string; topic: string; body: string }): NewsBlock[] {
  const blocks: NewsBlock[] = [];
  const sections = parts(news.body);
  const piece = pieceFor([news.topic], news.slug);
  const pieceFrame = frameOf(piece);
  const ruleFrame = frameOf(dividerFor(news.slug));

  sections.forEach((section, index) => {
    if (index > 0 && ruleFrame) blocks.push({ kind: 'rule', frame: ruleFrame });
    blocks.push({ kind: 'text', paragraphs: section });
    if (index === 0 && pieceFrame) blocks.push({ kind: 'piece', slug: piece, frame: pieceFrame });
  });

  return blocks.length > 0 ? blocks : [{ kind: 'text', paragraphs: [news.body.trim()] }];
}
