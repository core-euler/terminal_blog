---
title: "InnerCore — дневник снов, веб-версия"
summary: "Сны не забываются: запись голосом, разбор по архетипам, чат по сну и карта повторяющихся символов."
role: "продукт, архитектура, backend"
stack: [Flutter, FastAPI, PostgreSQL, Redis, Celery, MinIO, LLM, embeddings]
period: "SaaS, развивается"
result: "v0.3: разбор после сохранения, карта снов, голосовой ввод"
order: 5
cover: 01.webp
---

Сон забывается за минуты, а вместе с ним уходит и то, что он говорил о человеке. InnerCore сохраняет сон и сразу объясняет его: архетипы, символы, повторяющиеся мотивы.

<figure class="shot">
  <button type="button" popovertarget="shot-01" aria-label="Открыть снимок в полном размере">
    <img src="./01.webp" alt="InnerCore: дневник снов" width="1600" height="763" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-01">
    <button class="shot-back" type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./01.webp" alt="InnerCore: дневник снов" width="1600" height="763" loading="lazy">
    </button>
  </div>
</figure>

Записал сон — он сразу в дневнике, разбор приходит следом. Ждать с пустым экраном не нужно, поэтому привычка записывать не умирает на второй день.

<figure class="shot">
  <button type="button" popovertarget="shot-02" aria-label="Открыть снимок в полном размере">
    <img src="./02.webp" alt="InnerCore: разбор сна" width="1600" height="757" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-02">
    <button class="shot-back" type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./02.webp" alt="InnerCore: разбор сна" width="1600" height="757" loading="lazy">
    </button>
  </div>
</figure>

Разбор не пересказ, а рамка: какие архетипы в сне, что повторяется от ночи к ночи, на что обратить внимание. Читать его интереснее, чем собственный текст, — иначе дневник забрасывают.

<figure class="shot">
  <button type="button" popovertarget="shot-03" aria-label="Открыть снимок в полном размере">
    <img src="./03.webp" alt="InnerCore: чат по сну" width="1600" height="764" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-03">
    <button class="shot-back" type="button" popovertarget="shot-03" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-03" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./03.webp" alt="InnerCore: чат по сну" width="1600" height="764" loading="lazy">
    </button>
  </div>
</figure>

По конкретному сну можно поговорить: спросить, что значит сцена, почему она вернулась, что с этим делать. Ответ опирается на сон, а не на общие слова про сновидения.

<figure class="shot">
  <button type="button" popovertarget="shot-04" aria-label="Открыть снимок в полном размере">
    <img src="./04.webp" alt="InnerCore: карта символов" width="1600" height="764" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-04">
    <button class="shot-back" type="button" popovertarget="shot-04" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-04" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./04.webp" alt="InnerCore: карта символов" width="1600" height="764" loading="lazy">
    </button>
  </div>
</figure>

Карта собирает символы в узлы и группирует их по архетипам. Через месяц видно не отдельные сны, а сюжеты, которые возвращаются.

<figure class="shot">
  <button type="button" popovertarget="shot-05" aria-label="Открыть снимок в полном размере">
    <img src="./05.webp" alt="InnerCore: голосовой ввод" width="1600" height="756" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-05">
    <button class="shot-back" type="button" popovertarget="shot-05" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-05" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./05.webp" alt="InnerCore: голосовой ввод" width="1600" height="756" loading="lazy">
    </button>
  </div>
</figure>

Сон можно надиктовать голосом. Утром это быстрее, чем печатать, и именно поэтому запись вообще происходит.

<figure class="shot">
  <button type="button" popovertarget="shot-06" aria-label="Открыть снимок в полном размере">
    <img src="./06.webp" alt="InnerCore: список снов" width="1600" height="761" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-06">
    <button class="shot-back" type="button" popovertarget="shot-06" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-06" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./06.webp" alt="InnerCore: список снов" width="1600" height="761" loading="lazy">
    </button>
  </div>
</figure>

Сны лежат плотной сеткой — по ним быстро пробежать глазами. Прогресс разбора видно сразу: что уже разобрано, что ещё в работе.

<figure class="shot">
  <button type="button" popovertarget="shot-07" aria-label="Открыть снимок в полном размере">
    <img src="./07.webp" alt="InnerCore: первый вход" width="1600" height="759" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-07">
    <button class="shot-back" type="button" popovertarget="shot-07" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-07" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./07.webp" alt="InnerCore: первый вход" width="1600" height="759" loading="lazy">
    </button>
  </div>
</figure>

Первый вход ведёт по шагам, а не бросает в пустой дневник: пустой продукт выглядит сломанным, даже если работает.

<figure class="shot">
  <button type="button" popovertarget="shot-08" aria-label="Открыть снимок в полном размере">
    <img src="./08.webp" alt="InnerCore: разбор в работе" width="1600" height="764" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-08">
    <button class="shot-back" type="button" popovertarget="shot-08" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-08" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./08.webp" alt="InnerCore: разбор в работе" width="1600" height="764" loading="lazy">
    </button>
  </div>
</figure>

Разбор идёт в фоне и догоняет запись. Дневник остаётся отзывчивым, даже когда модель думает.

<figure class="shot">
  <button type="button" popovertarget="shot-09" aria-label="Открыть снимок в полном размере">
    <img src="./09.webp" alt="InnerCore: веб-версия" width="1600" height="517" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-09">
    <button class="shot-back" type="button" popovertarget="shot-09" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-09" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./09.webp" alt="InnerCore: веб-версия" width="1600" height="517" loading="lazy">
    </button>
  </div>
</figure>

Здесь снимки веб-версии. Мобильная — отдельной карточкой: [InnerCore для iOS и Android](/portfolio/mobile-apps/innercore/).
