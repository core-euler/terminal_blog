---
title: "Notify — календарь подписок в Telegram"
summary: "Все списания в одном календаре: сколько уходит, куда и когда следующее, и что будет через месяц."
role: "продукт, приложение"
stack: [TypeScript, Telegram Mini App]
period: "простое приложение"
result: "подписки в одном центре"
order: 6
cover: 01.webp
---

Подписки списывают деньги в разные дни, и вспоминаешь о них обычно после смс от банка. Notify собирает их в один календарь — открывается из Телеграма, ставить ничего не нужно.

<figure class="shot">
  <button type="button" popovertarget="shot-01" aria-label="Открыть снимок в полном размере">
    <img src="./01.webp" alt="Notify: календарь подписок" width="1440" height="900" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-01">
    <button class="shot-back" type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./01.webp" alt="Notify: календарь подписок" width="1440" height="900" loading="lazy">
    </button>
  </div>
</figure>

На каждой дате видно, что и сколько спишется, а по всему периоду считается, сколько уходит и сколько уйдёт в ближайший месяц. Вопрос «куда уходят деньги» перестаёт быть загадкой.

Управление в одном центре: добавить подписку, поправить дату или сумму, отключить ненужную. Приложение само показывает, что будет дальше, и предупреждает о списании — не нужно помнить про каждую.
