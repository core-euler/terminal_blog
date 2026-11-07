/*
 * Палитры из терминальных схем. В них нет подсветки кода — только 16 цветов
 * ANSI и пара фонов, поэтому раскладку токенов задаём сами, одинаковую для
 * всех трёх: ключевые слова, строки, числа, вызовы.
 *
 * Источники:
 * - warp, «cyberpunk-2077» — github.com/warpdotdev/themes, standard/cyberpunk-2077.yaml
 * - wezterm, «cyberpunk» — git.kokolor.es/mirror/wezterm, assets/colors/cyberpunk.toml
 * - silkcircuit, вариант neon — github.com/hyperb1iss/silkcircuit, lua/silkcircuit/variants.lua
 */

export interface TerminalPalette {
  id: string;
  label: string;
  base: string;
  text: string;
  ansi: [string, string, string, string, string, string, string, string];
  bright: [string, string, string, string, string, string, string, string];
}

export const TERMINAL_PALETTES: TerminalPalette[] = [
  {
    id: 'warp2077',
    label: '2077 (warp)',
    base: '#11133d',
    text: '#00ff9e',
    ansi: ['#ff8282', '#ff8272', '#00ffe7', '#f9f500', '#a5d5fe', '#ff00fb', '#8688ff', '#f1f1f1'],
    bright: ['#8e8e8e', '#ffc4bd', '#d6fcb9', '#fefdd5', '#c1e3fe', '#ffb1fe', '#e5e6fe', '#feffff'],
  },
  {
    id: 'wezterm',
    label: 'cyberpunk (wezterm)',
    base: '#332a57',
    text: '#e5e5e5',
    ansi: ['#000000', '#ff7092', '#00fbac', '#fffa6a', '#00bfff', '#df95ff', '#86cbfe', '#ffffff'],
    bright: ['#000000', '#ff8aa4', '#21f6bc', '#fff787', '#1bccfd', '#e6aefe', '#99d6fc', '#ffffff'],
  },
  {
    id: 'silkcircuit',
    label: 'SilkCircuit',
    base: '#12101a',
    text: '#f8f8f2',
    ansi: ['#0a0812', '#ff3366', '#00ff66', '#ffcc00', '#6699ff', '#ff00ff', '#00ffcc', '#f8f8f2'],
    bright: ['#728989', '#ff5fa8', '#66ff99', '#ffe699', '#a2bbff', '#ff99ff', '#00ffff', '#ffffff'],
  },
];
