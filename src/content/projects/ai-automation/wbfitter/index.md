---
title: "WB Fitter — виртуальная примерка для продавца одежды"
summary: "Покупатель присылает фото и видит себя в вещи из каталога продавца — до того, как заплатит и вернёт."
role: "backend, AI-генерация, интеграции"
stack: [Python, Telegram Bot API, ChatGPT, nano banana, Google Sheets]
period: "этап в составе WB-платформы"
result: "работает на живом каталоге продавца"
order: 6
cover: 01.webp
---

Для продавца одежды возврат «не подошло» — это двойная работа и испорченная карточка. Показать посадку заранее дешевле, чем принимать вещь назад.

<figure class="shot">
  <button type="button" popovertarget="shot-01" aria-label="Открыть снимок в полном размере">
    <img src="./01.webp" alt="WB Fitter: выбор вещи" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-01">
    <button class="shot-back" type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-01" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./01.webp" alt="WB Fitter: выбор вещи" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

Покупатель присылает своё фото и выбирает вещь из каталога продавца. Ничего не нужно мерить и никуда идти.

<figure class="shot">
  <button type="button" popovertarget="shot-02" aria-label="Открыть снимок в полном размере">
    <img src="./02.webp" alt="WB Fitter: результат примерки" width="1440" height="810" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-02">
    <button class="shot-back" type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-02" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./02.webp" alt="WB Fitter: результат примерки" width="1440" height="810" loading="lazy">
    </button>
  </div>
</figure>

На выходе он же в этой вещи: лицо и поза сохраняются, меняется одежда. Так видно посадку и цвет, а не «примерно так».

<figure class="shot">
  <button type="button" popovertarget="shot-03" aria-label="Открыть снимок в полном размере">
    <img src="./03.webp" alt="WB Fitter: каталог" width="1408" height="736" loading="lazy" decoding="async">
  </button>
  <div class="shot-full" popover id="shot-03">
    <button class="shot-back" type="button" popovertarget="shot-03" popovertargetaction="hide" aria-label="Закрыть снимок"></button>
    <button class="shot-zoom" type="button" popovertarget="shot-03" popovertargetaction="hide" aria-label="Закрыть снимок">
      <img src="./03.webp" alt="WB Fitter: каталог" width="1408" height="736" loading="lazy">
    </button>
  </div>
</figure>

Каталог продавец ведёт в обычной таблице: обновляет ассортимент сам, без разработчика и без выгрузки на сервер. Чем меньше посредников между товаром и покупателем, тем чаще каталог свежий.
