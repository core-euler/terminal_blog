---
title: "SvaraPro — карточная игра в Telegram со ставками"
summary: "Карточный стол на шесть человек прямо в мессенджере: партии в реальном времени, ставки, рефералка."
role: "backend, realtime, интеграции"
stack: [Nest.js, PostgreSQL, WebSocket, TON, USDT]
period: "200 часов"
result: "MVP сдан"
order: 1
cover: 02.webp
---

Карточная игра для шести человек внутри Телеграма: стол, ходы, ставки. Ничего не нужно скачивать — игра открывается из мессенджера.

<figure class="shot">
  <button type="button" popovertarget="shot-01" aria-label="Открыть снимок в полном размере">
    <img src="./01.webp" alt="SvaraPro: карточный стол" width="1440" height="900" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-01">
    <button type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./01.webp" alt="SvaraPro: карточный стол" width="1440" height="900" loading="lazy">
    </button>
  </div>
</figure>

Всё сложное здесь — синхронность. Шесть игроков ждут хода друг друга, а сеть у всех разная: сервер держит состояние партии и не даёт двоим сходить одним ходом. Обрыв связи не ломает стол — игрок возвращается в партию, а не начинает заново.

<figure class="shot">
  <button type="button" popovertarget="shot-02" aria-label="Открыть снимок в полном размере">
    <img src="./02.webp" alt="SvaraPro: ставки и рефералка" width="1440" height="900" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-02">
    <button type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./02.webp" alt="SvaraPro: ставки и рефералка" width="1440" height="900" loading="lazy">
    </button>
  </div>
</figure>

Вокруг игры — реферальная программа, чтобы игроки приводили новых, и ставки в TON и USDT с проверкой баланса до начала партии. Расширение механик осталось за рамками согласованного объёма — это отдельный этап, а не забытая работа.
