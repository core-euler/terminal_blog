---
title: "WB Assist — автоматизация продавца Wildberries"
summary: "Отзывы, статистика и склады в одном месте: продавец тратит на рутину часы, а не дни."
role: "backend, AI, продуктовая часть"
stack: [Python, Wildberries API, GPT, RAG, PostgreSQL]
period: "4+ месяца"
result: "MVP в работе у продавца"
order: 4
cover: 01.webp
---

Продавец на маркетплейсе тонет в рутине: сотни отзывов, пять выгрузок по статистике, склады и уведомления в разных окнах.

<figure class="shot">
  <button type="button" popovertarget="shot-01" aria-label="Открыть снимок в полном размере">
    <img src="./01.webp" alt="WB Assist: отзывы" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-01">
    <button type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./01.webp" alt="WB Assist: отзывы" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

Отзывы влияют на продажи, но отвечать на них вручную некогда. Модель отвечает с учётом тона карточки и истории оценок — не шаблоном, но и не чем попало в публичном ответе.

<figure class="shot">
  <button type="button" popovertarget="shot-02" aria-label="Открыть снимок в полном размере">
    <img src="./02.webp" alt="WB Assist: статистика словами" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-02">
    <button type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./02.webp" alt="WB Assist: статистика словами" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

Вопрос можно задать словами: «почему просели продажи в марте». Система находит нужные срезы и отвечает по данным, а не общими соображениями о сезонности.

<figure class="shot">
  <button type="button" popovertarget="shot-03" aria-label="Открыть снимок в полном размере">
    <img src="./03.webp" alt="WB Assist: дашборд" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-03">
    <button type="button" popovertarget="shot-03" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./03.webp" alt="WB Assist: дашборд" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

Цифры собраны в одном месте: вместо пяти выгрузок и таблиц — один экран, по которому видно, что происходит с продажами.

<figure class="shot">
  <button type="button" popovertarget="shot-04" aria-label="Открыть снимок в полном размере">
    <img src="./04.webp" alt="WB Assist: уведомления" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-04">
    <button type="button" popovertarget="shot-04" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./04.webp" alt="WB Assist: уведомления" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

О проблеме продавец узнаёт раньше, чем увидит её в отчёте за неделю: уведомления приходят сами.

<figure class="shot">
  <button type="button" popovertarget="shot-05" aria-label="Открыть снимок в полном размере">
    <img src="./05.webp" alt="WB Assist: склады" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-05">
    <button type="button" popovertarget="shot-05" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./05.webp" alt="WB Assist: склады" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

Склады и остатки — там же, где отзывы и статистика. Чем меньше окон, тем меньше шансов, что что-то забудут.

<figure class="shot">
  <button type="button" popovertarget="shot-06" aria-label="Открыть снимок в полном размере">
    <img src="./06.webp" alt="WB Assist: ещё один экран" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-06">
    <button type="button" popovertarget="shot-06" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./06.webp" alt="WB Assist: ещё один экран" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

<figure class="shot">
  <button type="button" popovertarget="shot-07" aria-label="Открыть снимок в полном размере">
    <img src="./07.webp" alt="WB Assist: ещё один экран продукта" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-07">
    <button type="button" popovertarget="shot-07" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./07.webp" alt="WB Assist: ещё один экран продукта" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>
