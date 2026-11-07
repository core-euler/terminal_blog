/*
 * Правая колонка есть на каждой странице.
 *
 * В статье список приходит со сборки: заголовки с якорями. На лентах колонка
 * показывает то, из чего лента состоит, — названия записей, новостей или тем,
 * и ведёт туда же, куда ведёт сама лента. Остальным разделам остаются
 * заголовки страницы. Колонка не исчезает ни на одной странице.
 */

const buffer = document.querySelector('main.buffer');
const list = document.querySelector<HTMLElement>('[data-outline-list]');
const counter = document.querySelector('.outline .pane-meta');

/** Строка колонки: отступ, значок, подпись и адрес. */
function row(depth: number, kind: string, text: string, href: string) {
  const item = document.createElement('li');
  item.style.setProperty('--depth', String(Math.max(0, depth)));

  const link = document.createElement('a');
  link.className = 'row';
  link.href = href;
  link.title = text;
  // Уровень строки виден в разметке: по нему красятся раздел и подраздел.
  link.dataset.depth = String(Math.max(0, depth));

  const badge = document.createElement('span');
  badge.className = 'outline-kind';
  badge.setAttribute('aria-hidden', 'true');
  badge.textContent = kind;

  const name = document.createElement('span');
  name.className = 'name';
  name.textContent = text;

  link.append(badge, name);
  item.append(link);
  return item;
}

/** Лента: записи блога, новости темы, темы раздела. */
function feedRows(): HTMLElement[] {
  const links = [...buffer!.querySelectorAll<HTMLAnchorElement>('a.feed-title, a.folder-row')];
  return links.map((anchor) => {
    const text = (anchor.querySelector('.folder-name')?.textContent ?? anchor.textContent ?? '').trim();
    return row(0, '$', text, anchor.getAttribute('href') ?? '#');
  });
}

/** Разделы без ленты: страница сама рассказывает о своей структуре. */
function headingRows(): HTMLElement[] {
  const headings = [...buffer!.querySelectorAll<HTMLElement>('.lines :is(h1, h2, h3):not(.pane-title)')].filter(
    (heading) => !heading.closest('aside'),
  );

  // У заголовков лент якорей нет: выдаём свои, иначе пункту некуда вести.
  headings.forEach((heading, index) => {
    if (!heading.id) heading.id = `outline-${index + 1}`;
  });

  const base = headings[0]?.tagName === 'H1' ? 1 : 2;
  return headings.map((heading) => {
    const level = Number(heading.tagName.slice(1));
    return row(level - base, '#'.repeat(level), heading.textContent?.trim() ?? '', `#${heading.id}`);
  });
}

if (buffer && list && list.children.length === 0) {
  const fromFeed = feedRows();
  const rows = fromFeed.length > 0 ? fromFeed : headingRows();
  list.append(...rows);
  if (counter) counter.textContent = String(rows.length);
}
