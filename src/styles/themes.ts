import { flavors } from '@catppuccin/palette';
import tokyoNight from '@shikijs/themes/tokyo-night';
import gruvbox from '@shikijs/themes/gruvbox-dark-medium';
import dracula from '@shikijs/themes/dracula';
import monokai from '@shikijs/themes/monokai';
import nord from '@shikijs/themes/nord';
import rosePine from '@shikijs/themes/rose-pine';
import kanagawa from '@shikijs/themes/kanagawa-wave';
import everforest from '@shikijs/themes/everforest-dark';
import oneDark from '@shikijs/themes/one-dark-pro';

/*
 * Хексы здесь не вписаны руками: Catppuccin берётся из @catppuccin/palette,
 * остальные темы — из тех же тем Shiki, которыми подсвечивается код.
 *
 * Каждая тема задаёт «сырые» цвета --c-*. Для не-Catppuccin тем задаются
 * только base/text и три акцента, а слои (mantle, crust, surface*, overlay*,
 * subtext*) выводятся из них через color-mix — так перепады яркости между
 * панелями одинаково выглядят во всех темах.
 */

interface ShikiTheme {
  name?: string;
  displayName?: string;
  type?: string;
  colors?: Record<string, string>;
}

type Ansi = 'Magenta' | 'Blue' | 'Green' | 'Cyan' | 'Yellow' | 'Red';

export interface ThemeDef {
  id: string;
  label: string;
  appearance: 'dark' | 'light';
  /** Имя темы Shiki для подсветки кода. */
  shiki: string;
  vars: Record<string, string>;
}

const ROLE_ORDER = ['link', 'active', 'tag'] as const;

function catppuccin(id: string, flavor: keyof typeof flavors, shiki: string): ThemeDef {
  const f = flavors[flavor];
  const c = f.colors;
  const vars: Record<string, string> = {};
  for (const key of [
    'crust', 'mantle', 'base', 'surface0', 'surface1', 'surface2',
    'overlay0', 'overlay1', 'subtext0', 'subtext1', 'text',
  ] as const) {
    vars[key] = c[key].hex;
  }
  vars.link = c.mauve.hex;
  vars.active = c.blue.hex;
  vars.tag = c.green.hex;
  // Цвета для разметки постов (:red[...] и т. п.).
  Object.assign(vars, {
    red: c.red.hex,
    orange: c.peach.hex,
    yellow: c.yellow.hex,
    green: c.green.hex,
    cyan: c.teal.hex,
    blue: c.blue.hex,
    purple: c.mauve.hex,
    pink: c.pink.hex,
  });
  return { id, label: `Catppuccin ${f.name}`, appearance: f.dark ? 'dark' : 'light', shiki, vars };
}

/**
 * Акценты берутся из ANSI-палитры терминала темы. `roles` — какой слот ANSI
 * отдать ссылкам / активному элементу / тегам (не во всех темах есть, например,
 * зелёный), `bright` — брать ли яркий вариант слота.
 */
function fromShiki(
  id: string,
  theme: ShikiTheme,
  opts: { roles?: [Ansi, Ansi, Ansi]; bright?: boolean; label?: string } = {},
): ThemeDef {
  const colors = theme.colors ?? {};
  const pick = (slot: Ansi) => {
    const bright = colors[`terminal.ansiBright${slot}`];
    const normal = colors[`terminal.ansi${slot}`];
    const value = opts.bright === false ? normal ?? bright : bright ?? normal;
    if (!value) throw new Error(`Тема ${theme.name}: нет цвета terminal.ansi${slot}`);
    return value;
  };
  const roles = opts.roles ?? ['Magenta', 'Blue', 'Green'];
  const vars: Record<string, string> = {
    base: colors['editor.background']!,
    text: colors['editor.foreground']!,
  };
  ROLE_ORDER.forEach((role, i) => (vars[role] = pick(roles[i])));
  // Цвета для разметки постов; orange и pink в ANSI нет — они выводятся в CSS.
  vars.red = pick('Red');
  vars.yellow = pick('Yellow');
  vars.green = pick('Green');
  vars.cyan = pick('Cyan');
  vars.blue = pick('Blue');
  vars.purple = pick('Magenta');
  return {
    id,
    label: opts.label ?? theme.displayName ?? theme.name!,
    appearance: theme.type === 'light' ? 'light' : 'dark',
    shiki: theme.name!,
    vars,
  };
}

export const THEMES: ThemeDef[] = [
  catppuccin('mocha', 'mocha', 'catppuccin-mocha'),
  catppuccin('macchiato', 'macchiato', 'catppuccin-macchiato'),
  catppuccin('latte', 'latte', 'catppuccin-latte'),
  fromShiki('tokyonight', tokyoNight, { roles: ['Magenta', 'Blue', 'Cyan'] }),
  fromShiki('gruvbox', gruvbox, { label: 'Gruvbox' }),
  fromShiki('dracula', dracula, { roles: ['Magenta', 'Cyan', 'Green'], label: 'Dracula' }),
  fromShiki('monokai', monokai),
  fromShiki('nord', nord, { roles: ['Magenta', 'Cyan', 'Green'] }),
  fromShiki('rosepine', rosePine, { roles: ['Magenta', 'Cyan', 'Yellow'] }),
  fromShiki('kanagawa', kanagawa, { label: 'Kanagawa' }),
  fromShiki('everforest', everforest, { label: 'Everforest' }),
  fromShiki('onedark', oneDark),
];

export const DEFAULT_THEME = 'mocha';

/** Имена цветов для постов: `:red[текст]` → `<span class="c-red">`. */
export const TEXT_COLORS = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'pink', 'dim'] as const;

export const FONT_SIZES = [
  { id: 's', label: 'Мелкий текст', scale: 0.9 },
  { id: 'm', label: 'Обычный текст', scale: 1 },
  { id: 'l', label: 'Крупный текст', scale: 1.14 },
] as const;
export const DEFAULT_FONT_SIZE = 'm';

/** Карта для shikiConfig.themes: `--shiki-<id>` в разметке кода. */
export const shikiThemes = Object.fromEntries(THEMES.map((t) => [t.id, t.shiki]));

/** CSS всех тем. Встраивается в <head>, поэтому переключение не мигает. */
export function themesCss(): string {
  const mix = (a: string, b: string, pct: number) => `color-mix(in oklab,var(--c-${a}),${b} ${pct}%)`;
  // Выведенные слои: работают, если тема не задала их явно (как Catppuccin).
  const derived = [
    `--c-mantle:${mix('base', 'black', 16)}`,
    `--c-crust:${mix('base', 'black', 32)}`,
    `--c-surface0:${mix('base', 'var(--c-text)', 10)}`,
    `--c-surface1:${mix('base', 'var(--c-text)', 17)}`,
    `--c-surface2:${mix('base', 'var(--c-text)', 26)}`,
    `--c-overlay0:${mix('base', 'var(--c-text)', 42)}`,
    `--c-overlay1:${mix('base', 'var(--c-text)', 52)}`,
    `--c-subtext0:${mix('base', 'var(--c-text)', 68)}`,
    `--c-subtext1:${mix('base', 'var(--c-text)', 82)}`,
    `--c-orange:color-mix(in oklab,var(--c-red),var(--c-yellow))`,
    `--c-pink:color-mix(in oklab,var(--c-red) 45%,var(--c-purple))`,
    `--c-dim:var(--c-subtext0)`,
  ].join(';');

  const blocks = [`:root{${derived}}`];
  // Тема всегда задаётся атрибутом на <html> (его рендерит сервер), поэтому
  // слои темы по умолчанию не протекают в темы, где они выводятся.
  for (const t of THEMES) {
    const root = `:root[data-theme="${t.id}"]`;
    const vars = Object.entries(t.vars).map(([k, v]) => `--c-${k}:${v}`).join(';');
    blocks.push(`${root}{color-scheme:${t.appearance};${vars}}`);
    // Код: Shiki с defaultColor:false кладёт цвета всех тем в --shiki-<id>.
    blocks.push(
      `${root} .astro-code span{color:var(--shiki-${t.id});font-style:var(--shiki-${t.id}-font-style);font-weight:var(--shiki-${t.id}-font-weight)}`,
    );
  }
  for (const s of FONT_SIZES) {
    blocks.push(`:root[data-font-size="${s.id}"]{--text-scale:${s.scale}}`);
  }
  blocks.push(TEXT_COLORS.map((c) => `.c-${c}{color:var(--c-${c})}`).join(''));
  return blocks.join('\n');
}
