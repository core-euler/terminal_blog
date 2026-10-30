---
title: "LearnCore — платформа обучения с AI-режимами"
summary: "Курсы, прогресс и AI-режимы по материалу курса: человек учится шаг за шагом, а не листает текст."
role: "backend, архитектура"
stack: [Python, FastAPI, PostgreSQL, LLM, RAG, SSE]
period: "MVP"
result: "закрыт весь скоуп MVP"
order: 2
cover: 01.webp
---

Курс, который проходят с моделью рядом: не «прочитал статью», а видно, где остановился, что понял и что спросить.

<figure class="shot">
  <button type="button" popovertarget="shot-01" aria-label="Открыть снимок в полном размере">
    <img src="./01.webp" alt="LearnCore: курс и прогресс" width="1440" height="900" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-01">
    <button class="shot-back" type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./01.webp" alt="LearnCore: курс и прогресс" width="1440" height="900" loading="lazy">
    </button>
  </div>
</figure>

Материал разбит на шаги, прогресс сохраняется. Человек возвращается и продолжает с того же места — а не начинает заново и не бросает на третьем уроке.

<figure class="shot">
  <button type="button" popovertarget="shot-02" aria-label="Открыть снимок в полном размере">
    <img src="./02.webp" alt="LearnCore: режим с моделью" width="1440" height="900" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-02">
    <button class="shot-back" type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./02.webp" alt="LearnCore: режим с моделью" width="1440" height="900" loading="lazy">
    </button>
  </div>
</figure>

Модель отвечает по материалу курса, а не по интернету вообще. Подключить другую модель можно без переделки платформы — это запас на будущее, когда сегодняшняя подорожает или уйдёт.

<figure class="shot">
  <button type="button" popovertarget="shot-03" aria-label="Открыть снимок в полном размере">
    <img src="./03.webp" alt="LearnCore: длинный ответ" width="1440" height="900" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-03">
    <button class="shot-back" type="button" popovertarget="shot-03" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-03" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./03.webp" alt="LearnCore: длинный ответ" width="1440" height="900" loading="lazy">
    </button>
  </div>
</figure>

Ответ приходит по мере готовности и не обрывается на плохой сети: человек видит, как появляется текст, вместо пустого экрана и таймера.
