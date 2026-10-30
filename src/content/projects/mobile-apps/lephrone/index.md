---
title: "Lephrone H01 — аромадиффузор с приложением"
summary: "Устройство для дома, которым управляют с телефона: расписание, интенсивность и сценарии на день."
role: "прошивка, мобильное приложение"
stack: [C, Tuya SDK, мобильное приложение]
period: "два этапа"
result: "прошивка сдана, приложение в работе"
order: 3
cover: 04.webp
---

Аромадиффузор, который включается не кнопкой на корпусе, а расписанием в телефоне. Клиент из США, работа разбита на два этапа.

<figure class="shot">
  <button type="button" popovertarget="shot-01" aria-label="Открыть снимок в полном размере">
    <img src="./01.webp" alt="Lephrone: расписание" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-01">
    <button type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./01.webp" alt="Lephrone: расписание" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

Дни и часы задаются заранее: утром одно, вечером другое. Не нужно помнить про кнопку и не нужно возвращаться домой, чтобы включить.

<figure class="shot">
  <button type="button" popovertarget="shot-02" aria-label="Открыть снимок в полном размере">
    <img src="./02.webp" alt="Lephrone: интенсивность" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-02">
    <button type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./02.webp" alt="Lephrone: интенсивность" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

Интенсивность регулируется под комнату и настроение: в спальне тише, в гостиной заметнее.

<figure class="shot">
  <button type="button" popovertarget="shot-03" aria-label="Открыть снимок в полном размере">
    <img src="./03.webp" alt="Lephrone: сценарии" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-03">
    <button type="button" popovertarget="shot-03" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./03.webp" alt="Lephrone: сценарии" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

Сценарии собирают расписание и интенсивность в готовый режим — «работа», «вечер», «отпуск». Пользователю не приходится каждый раз настраивать заново.

<figure class="shot">
  <button type="button" popovertarget="shot-04" aria-label="Открыть снимок в полном размере">
    <img src="./04.webp" alt="Lephrone: прошивка" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-04">
    <button type="button" popovertarget="shot-04" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./04.webp" alt="Lephrone: прошивка" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

Прошивка сделана на модуле Tuya: устройство настраивается в привычном приложении и ведёт себя разумно при обрыве связи и после перезагрузки питания — не требует выдернуть розетку.
