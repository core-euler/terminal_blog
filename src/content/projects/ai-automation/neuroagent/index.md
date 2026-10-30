---
title: "NeuronAgent — бот с генерацией текста и картинок"
summary: "Нейросеть в Телеграме по подписке: ответ на голосовое, картинка по описанию, рефералка и админка."
role: "backend, интеграции, AI"
stack: [Python, Telegram Bot API, OpenAI, Midjourney, ЮKassa, TPAY]
period: "100 часов"
result: "около 3 000 активных пользователей в месяц"
order: 7
cover: 01.webp
---

Клиент хотел продавать подписку на нейросеть в Телеграме, без своего приложения и без разработчика в штате. Сделал полный цикл — от бота до платежей.

<figure class="shot">
  <button type="button" popovertarget="shot-01" aria-label="Открыть снимок в полном размере">
    <img src="./01.webp" alt="NeuronAgent: диалог с ботом" width="1440" height="733" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-01">
    <button type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./01.webp" alt="NeuronAgent: диалог с ботом" width="1440" height="733" loading="lazy">
    </button>
  </div>
</figure>

Пользователь отправляет голосовое, бот отвечает текстом. Второй режим — картинка по описанию. Ничего не нужно устанавливать: мессенджер уже у всех.

<figure class="shot">
  <button type="button" popovertarget="shot-02" aria-label="Открыть снимок в полном размере">
    <img src="./02.webp" alt="NeuronAgent: генерация картинки" width="1440" height="740" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-02">
    <button type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./02.webp" alt="NeuronAgent: генерация картинки" width="1440" height="740" loading="lazy">
    </button>
  </div>
</figure>

Вокруг продукта — подписки, рефералка и админка с аналитикой. Лимиты считаются до запроса, а не после: каждый ответ модели стоит денег, и считать это «потом» — значит платить из своего кармана.
