---
title: "Crypto Caller — алерт о цене звонком"
summary: "Сервис звонит на телефон, когда цена дошла до нужного уровня: пуш можно не заметить, звонок — нет."
role: "backend, интеграции"
stack: [Python, Twilio, биржевые API, PostgreSQL]
period: "80 часов"
result: "подписки и биллинг"
order: 4
cover: 01.webp
---

Цена ходит и ночью, а трейдер спит. Пользователь ставит уровень, сервис звонит, когда цена до него дошла.

<figure class="shot">
  <button type="button" popovertarget="shot-01" aria-label="Открыть снимок в полном размере">
    <img src="./01.webp" alt="Crypto Caller: настройка алерта" width="1402" height="670" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-01">
    <button type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./01.webp" alt="Crypto Caller: настройка алерта" width="1402" height="670" loading="lazy">
    </button>
  </div>
</figure>

Звонок вместо пуша выбран намеренно: пуш можно не заметить в беззвучном режиме, звонок — нет. Внутри подписки с лимитом алертов, и одна цель даёт один звонок, сколько бы раз цена её ни пересекла.
