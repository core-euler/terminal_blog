/*
 * Правая колонка есть на каждой странице. У статей список заголовков приходит
 * со сборки, остальным разделам его неоткуда взять — собираем из самого
 * буфера: страницы, разделы, записи портфолио. Заголовков нет — колонка
 * показывает пустое состояние, но не исчезает.
 */

const buffer = document.querySelector('main.buffer');
const list = document.querySelector<HTMLElement>('[data-outline-list]');

if (buffer && list && list.children.length === 0) {
  const headings = [...buffer.querySelectorAll<HTMLElement>('.lines :is(h1, h2, h3):not(.pane-title)')].filter(
    (heading) => !heading.closest('aside'),
  );

  // У заголовков лент якорей нет: выдаём свои, иначе пункту некуда вести.
  headings.forEach((heading, index) => {
    if (!heading.id) heading.id = `outline-${index + 1}`;
  });

  const base = headings[0]?.tagName === 'H1' ? 1 : 2;
  const rows = headings.map((heading) => {
    const depth = Math.max(0, Number(heading.tagName.slice(1)) - base);
    const item = document.createElement('li');
    item.style.setProperty('--depth', String(depth));

    const link = document.createElement('a');
    link.className = 'row';
    link.href = `#${heading.id}`;

    const kind = document.createElement('span');
    kind.className = 'outline-kind';
    kind.setAttribute('aria-hidden', 'true');
    kind.textContent = '#'.repeat(Number(heading.tagName.slice(1)));

    const name = document.createElement('span');
    name.className = 'name';
    name.textContent = heading.textContent?.trim() ?? '';

    link.append(kind, name);
    item.append(link);
    return item;
  });

  list.append(...rows);

  const counter = document.querySelector('.outline .pane-meta');
  if (counter) counter.textContent = String(rows.length);
}
