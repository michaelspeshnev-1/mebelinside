# 07-blok-otpravit-foto · Блок «Пришлите фото» на страницы расчёта

Задание: п. 7, R18 · ~15 мин · Админка: https://mebelinside.ru/adminmeb.php

## Что сделать

1. Открыть https://mebelinside.ru/raschet-stoimosti-kuhni.html и https://mebelinside.ru/raschet-stoimosti-shkafa-kupe.html — есть ли уже блок «Пришлите фото или планировку».
2. Найти страницы: Веб-сайт → Страницы → поиск «расчет» [?] (если это не страницы, а блоки макета — Дизайн → Макеты → вкладка этой страницы).
3. В конец описания каждой страницы (режим «Исходный код») вставить ВЕСЬ код ниже. Если на странице калькулятор-скрипт — вставлять ниже него, сам калькулятор не трогать.
4. Кнопка MAX подхватывает ссылку из шапки; если в шапке MAX нет — кнопка скрывается сама, это нормально.
5. Цели Метрики — не здесь, а в карточке 12d.

## Что вставить

HTML вставлять в режиме «Исходный код» редактора (кнопка `</>`/«HTML»): визуальный редактор CS-Cart ломает `<script>`. Строки «Длины…», «Ключи…», «Примечание…» и текст между блоками — подсказки для тебя, на сайт их не вставлять.

Файл целиком: [site-blocks/blok-otpravit-foto.html](https://github.com/michaelspeshnev-1/mebelinside/blob/main/site-blocks/blok-otpravit-foto.html) · только текст для копирования: https://raw.githubusercontent.com/michaelspeshnev-1/mebelinside/main/site-blocks/blok-otpravit-foto.html

```html
<!-- Блок «Отправить фото / планировку». Вставить как HTML-блок на главную, страницу кухонь, страницы расчёта, /b2b/.
     Без бэкенда: кнопки открывают мессенджеры, ссылки берутся из шапки сайта (иконки WhatsApp/Telegram/MAX уже там).
     Цели Метрики: lead_photo_wa / lead_photo_max / lead_photo_tg / lead_photo_call (создать в Метрике как JS-событие). -->
<section class="mi-photo" id="miPhoto">
  <h2>Пришлите фото или планировку</h2>
  <p>Дадим предварительный ориентир по стоимости. Достаточно фото кухни или помещения — анкету заполнять не нужно.</p>
  <div class="mi-photo-btns">
    <a class="mi-photo-btn" data-ch="wa"  href="https://api.whatsapp.com/send?phone=79289516342&text=%D0%97%D0%B4%D1%80%D0%B0%D0%B2%D1%81%D1%82%D0%B2%D1%83%D0%B9%D1%82%D0%B5%21%20%D0%A5%D0%BE%D1%87%D1%83%20%D1%80%D0%B0%D1%81%D1%87%D1%91%D1%82.%20%D0%9F%D1%80%D0%B8%D1%88%D0%BB%D1%8E%20%D1%84%D0%BE%D1%82%D0%BE%2F%D0%BF%D0%BB%D0%B0%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D1%83." target="_blank" rel="noopener">WhatsApp</a>
    <a class="mi-photo-btn" data-ch="max" href="#" target="_blank" rel="noopener">MAX</a>
    <a class="mi-photo-btn" data-ch="tg"  href="https://t.me/mebel_inside" target="_blank" rel="noopener">Telegram</a>
    <a class="mi-photo-btn mi-photo-btn--call" data-ch="call" href="tel:+79289516342">Позвонить</a>
  </div>
  <p class="mi-photo-note">Отвечаем в рабочее время. Фото используем только для расчёта.</p>
</section>
<style>
.mi-photo{max-width:960px;margin:32px auto;padding:28px 24px;border:1px solid #e6e0d4;background:#fbf9f4;border-radius:8px}
.mi-photo h2{margin:0 0 8px;font-size:26px}
.mi-photo p{margin:0 0 16px}
.mi-photo-btns{display:flex;flex-wrap:wrap;gap:12px}
.mi-photo-btn{display:inline-block;padding:14px 26px;border-radius:6px;background:#2d2a26;color:#fff!important;text-decoration:none;font-weight:600;min-width:140px;text-align:center}
.mi-photo-btn--call{background:#fff;color:#2d2a26!important;border:2px solid #2d2a26}
.mi-photo-note{margin:14px 0 0;font-size:13px;color:#6b655c}
@media(max-width:600px){.mi-photo-btn{flex:1 1 100%}}
</style>
<script>
(function(){
  var box=document.getElementById('miPhoto'); if(!box) return;
  // MAX и Telegram: берём ссылки, которые уже есть в шапке/подвале сайта
  function find(sel){var a=document.querySelector('.tygh-header '+sel+', .tygh-top-panel '+sel+', .tygh-footer '+sel+', '+sel);return a&&a.href;}
  var max=find('a[href*="max.ru"]'), tg=find('a[href*="t.me/"]');
  var bMax=box.querySelector('[data-ch=max]'), bTg=box.querySelector('[data-ch=tg]');
  if(max){bMax.href=max;}else{bMax.style.display='none';}
  if(tg){bTg.href=tg;}
  function goal(name){
    try{ if(window.Ya&&Ya._metrika&&Ya._metrika.getCounters){Ya._metrika.getCounters().forEach(function(c){ym(c.id,'reachGoal',name);});}}catch(e){}
    try{ if(window.dataLayer){dataLayer.push({event:name});} }catch(e){}
  }
  box.addEventListener('click',function(e){
    var a=e.target.closest('[data-ch]'); if(!a) return;
    goal('lead_photo_'+a.getAttribute('data-ch'));
  });
})();
</script>
```

*(конец раздела «Что вставить»)*

## Проверка

- На обеих страницах расчёта виден блок «Пришлите фото или планировку».
- Кнопка WhatsApp открывает чат с номером +7 928 951-63-42, Telegram — канал/чат `mebel_inside`.
- Калькулятор работает как раньше.
- Перед проверкой сбросить кэш: https://mebelinside.ru/adminmeb.php?cc&ctpl, страницу открывать в новой вкладке.

## Нельзя

- Код калькулятора не менять.
- Ничего не удалять (страницы, категории, блоки, товары, файлы) — ненужное выключать (статус «Выключено»/«Скрыто»).
- 301-редирект — только если он прямо назван в этой карточке как решённый Михаилом; любой другой — сначала «да» Михаила.
- Не трогать «Пользовательские CSS» (Дизайн → Редактор тем) — однажды это дало белый экран сайта.
- Не выдумывать: предложение с пометкой [?] в видимом тексте не вставлять (убрать целиком); HTML-комментарии `<!-- … -->` на сайте не видны — их можно оставить.

## Отчёт

Одной строкой Михаилу (он перешлёт в «Главный»):

`п. 7 — блок «Пришлите фото» стоит на <адреса>; кнопки проверены; MAX <есть/скрыта>`

Дальше: [08-litye.md](https://github.com/michaelspeshnev-1/mebelinside/blob/main/zalivka/08-litye.md)
