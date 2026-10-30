---
title: "НЕО Ломбард — личный кабинет сети ломбардов"
summary: "Клиент видит свои залоги, оценки и отделения в телефоне, а данные остаются в 1С заказчика."
role: "backend, интеграции, передача проекта"
stack: [Flutter, Dart, Python, FastAPI, 1С, Docker, Caddy]
period: "передача и сопровождение"
result: "API развёрнут на сервере заказчика"
order: 2
cover: 02.webp
---

Клиенту ломбарда не нужно ехать в отделение, чтобы узнать оценку или дату выкупа. Данные при этом остаются в 1С, где их ведёт сам ломбард.

<figure class="shot">
  <button type="button" popovertarget="shot-01" aria-label="Открыть снимок в полном размере">
    <img src="./01.webp" alt="НЕО Ломбард: залоги" width="1440" height="900" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-01">
    <button class="shot-back" type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./01.webp" alt="НЕО Ломбард: залоги" width="1440" height="900" loading="lazy">
    </button>
  </div>
</figure>

В приложении видно свои залоги, оценки и отделения. Человек не звонит и не приезжает ради цифры, которую и так носит в кармане.

<figure class="shot">
  <button type="button" popovertarget="shot-02" aria-label="Открыть снимок в полном размере">
    <img src="./02.webp" alt="НЕО Ломбард: данные из 1С" width="1440" height="900" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-02">
    <button class="shot-back" type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./02.webp" alt="НЕО Ломбард: данные из 1С" width="1440" height="900" loading="lazy">
    </button>
  </div>
</figure>

Между приложением и 1С стоит прослойка: договорённости и учёт остаются там, где были, а клиент получает удобный экран. Двойного ввода нет — значит, нет и расхождений.

<figure class="shot">
  <button type="button" popovertarget="shot-03" aria-label="Открыть снимок в полном размере">
    <img src="./03.webp" alt="НЕО Ломбард: передача проекта" width="1440" height="900" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-03">
    <button class="shot-back" type="button" popovertarget="shot-03" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-03" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./03.webp" alt="НЕО Ломбард: передача проекта" width="1440" height="900" loading="lazy">
    </button>
  </div>
</figure>

Проект жил в трёх расходящихся копиях. Свёл в одну ветку, собрал архив передачи и развернул на сервере заказчика. Остался внешний блокер: пока адрес сервера не разрешён в 1С, приложение доходит до экрана входа и останавливается.
