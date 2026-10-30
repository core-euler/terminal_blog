---
title: "InnerCore — дневник снов, приложение"
summary: "Сны не забываются: запись голосом, разбор по архетипам, чат по сну и карта повторяющихся символов."
role: "продукт, архитектура, backend"
stack: [Flutter, FastAPI, PostgreSQL, Redis, Celery, MinIO, LLM, embeddings]
period: "SaaS, развивается"
result: "v0.3: разбор после сохранения, карта снов, голосовой ввод"
order: 5
cover: 02.webp
---

Сон забывается за минуты, а вместе с ним уходит и то, что он говорил о человеке. InnerCore сохраняет сон и сразу объясняет его: архетипы, символы, повторяющиеся мотивы.

<figure class="shot">
  <button type="button" popovertarget="shot-01" aria-label="Открыть снимок в полном размере">
    <img src="./01.webp" alt="InnerCore в телефоне" width="1440" height="900" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-01">
    <button type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./01.webp" alt="InnerCore в телефоне" width="1440" height="900" loading="lazy">
    </button>
  </div>
</figure>

Записал сон — он сразу в дневнике, разбор приходит следом. Телефон под рукой утром, поэтому привычка записывать не умирает на второй день.

<figure class="shot">
  <button type="button" popovertarget="shot-02" aria-label="Открыть снимок в полном размере">
    <img src="./02.webp" alt="InnerCore: карта символов в приложении" width="1440" height="900" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-02">
    <button type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./02.webp" alt="InnerCore: карта символов в приложении" width="1440" height="900" loading="lazy">
    </button>
  </div>
</figure>

Карта собирает символы в узлы и группирует их по архетипам. Через месяц видно не отдельные сны, а сюжеты, которые возвращаются.

<figure class="shot">
  <button type="button" popovertarget="shot-03" aria-label="Открыть снимок в полном размере">
    <img src="./03.webp" alt="InnerCore: сон и разбор" width="1440" height="900" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-03">
    <button type="button" popovertarget="shot-03" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./03.webp" alt="InnerCore: сон и разбор" width="1440" height="900" loading="lazy">
    </button>
  </div>
</figure>

По конкретному сну можно поговорить: спросить, что значит сцена и почему она вернулась. Ответ опирается на сон, а не на общие слова про сновидения.

Здесь снимки приложения. Веб-версия — отдельной карточкой: [InnerCore в браузере](/portfolio/ai-automation/innercore/).
