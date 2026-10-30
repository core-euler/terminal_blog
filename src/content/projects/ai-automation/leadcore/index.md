---
title: "LeadCore — поиск заказов в Telegram-чатах"
summary: "Бот читает чаты, отбирает заказы и складывает их в базу: кому что нужно, где болит, за что платят."
role: "продукт, backend"
stack: [Python, FastAPI, PostgreSQL, Telegram Bot API, LLM]
period: "свой продукт"
result: "работает в проде, есть тарифы и админка"
order: 1
cover: 01.webp
---

Заказы приходят в чаты, а не на почту. Кто читает чаты руками — теряет часы; кто не читает — теряет заказы.

<figure class="shot">
  <button type="button" popovertarget="shot-01" aria-label="Открыть снимок в полном размере">
    <img src="./01.webp" alt="LeadCore: лента найденных заказов" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-01">
    <button type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./01.webp" alt="LeadCore: лента найденных заказов" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

Бот просматривает всю новую ленту и оставляет только сообщения, где действительно есть задача и бюджет. Дорогая проверка достаётся единицам сообщений, а не всему потоку, поэтому подписка стоит дешевле, чем час внимания.

<figure class="shot">
  <button type="button" popovertarget="shot-02" aria-label="Открыть снимок в полном размере">
    <img src="./02.webp" alt="LeadCore: карточка заказа" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-02">
    <button type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./02.webp" alt="LeadCore: карточка заказа" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

Найденное не теряется: база показывает, кому что нужно, где болит и какие темы повторяются. Через неделю видно, за что на рынке платят, а за что нет, — без чтения сотен чатов.

<figure class="shot">
  <button type="button" popovertarget="shot-03" aria-label="Открыть снимок в полном размере">
    <img src="./03.webp" alt="LeadCore: разбор и кластеры" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-03">
    <button type="button" popovertarget="shot-03" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./03.webp" alt="LeadCore: разбор и кластеры" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

По найденным болям бот собирает черновики постов: не «полезные советы», а ответ на то, что люди уже спрашивают. Тарифы, лимиты и админка сделаны так, чтобы продукт работал без ежедневного участия.
