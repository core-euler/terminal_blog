import { createHash } from 'node:crypto';

/*
 * Shiki с несколькими темами пишет цвета каждого токена прямо в разметку:
 * одна строка на все темы сразу, плюс отдельные переменные для начертания.
 * Значений мало, повторов много, поэтому токен получает класс, а сами
 * значения уезжают в общий css-файл: разметка худеет примерно в тридцать раз.
 *
 * Разбор идёт по готовым страницам, а не в конвейере markdown: markdown
 * кэшируется, и трансформер отработал бы только на холодном кэше, оставив
 * страницы с классами без правил. Готовый html — единственный источник,
 * который всегда на месте.
 */
const PREFIX = '--shiki-';

/** Тег с атрибутами; кавычки могут содержать `>`, поэтому `<>` вне них не пропускаем. */
const TAG = /<[a-z][a-z0-9-]*(?:"[^"]*"|[^<>])*>/gi;
const ATTR = /\s+([^\s=]+)(?:="([^"]*)")?/g;

/** Стиль разбивается на переменные Shiki (в класс) и всё остальное (остаётся inline). */
export function splitStyle(style: string): { vars: string; rest: string } {
  const vars: string[] = [];
  const rest: string[] = [];
  for (const raw of style.split(';')) {
    const decl = raw.trim();
    if (!decl) continue;
    (decl.startsWith(PREFIX) ? vars : rest).push(`${decl};`);
  }
  return { vars: vars.join(''), rest: rest.join('') };
}

export function className(vars: string): string {
  return `t${createHash('sha1').update(vars).digest('hex').slice(0, 7)}`;
}

function reclassTag(tag: string, rules: Map<string, string>): string {
  const head = /^<([a-z0-9-]+)((?:\s+[^\s=]+(?:="[^"]*")?)*)\s*(\/?)>$/i.exec(tag);
  if (!head) return tag;

  const attrs: [string, string | null][] = [];
  let found: RegExpExecArray | null;
  ATTR.lastIndex = 0;
  while ((found = ATTR.exec(head[2]))) attrs.push([found[1], found[2] ?? null]);

  const at = attrs.findIndex(([name, value]) => name === 'style' && value?.includes(PREFIX));
  if (at < 0) return tag;

  const { vars, rest } = splitStyle(attrs[at][1]!);
  if (!vars) return tag;

  const cls = className(vars);
  rules.set(vars, cls);
  if (rest) attrs[at] = ['style', rest];
  else attrs.splice(at, 1);

  const classAt = attrs.findIndex(([name]) => name === 'class');
  if (classAt < 0) attrs.push(['class', cls]);
  else attrs[classAt] = ['class', `${attrs[classAt][1]} ${cls}`];

  const body = attrs.map(([name, value]) => (value === null ? ` ${name}` : ` ${name}="${value}"`)).join('');
  return `<${head[1]}${body}${head[3] ? ' /' : ''}>`;
}

/**
 * Переносит переменные Shiki из атрибутов в классы. Заодно копит правила:
 * `rules` пополняется парами «значения — имя класса».
 */
export function rewriteTokens(html: string, rules: Map<string, string>): string {
  if (!html.includes(`style="${PREFIX}`)) return html;
  return html.replace(TAG, (tag) => reclassTag(tag, rules));
}

/** Правила для накопленных классов, в устойчивом порядке. */
export function tokenCss(rules: Map<string, string>): string {
  return [...rules]
    .sort(([a], [b]) => (a < b ? -1 : 1))
    .map(([vars, cls]) => `.${cls}{${vars}}`)
    .join('');
}
