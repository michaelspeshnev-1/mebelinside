# 12d-metrika-celi · Цели Яндекс Метрики и скрипт

Задание: п. 12, техпакет шаг 5, R18 · ~30 мин · Админка: https://mebelinside.ru/adminmeb.php

## Что сделать

1. Узнать номер счётчика: metrika.yandex.ru → счётчик mebelinside.ru → номер. Если доступа нет — остановиться, отчёт «нужен номер счётчика».
2. Метрика → Настройки → Цели → создать цели из раздела 4.1 (тип «JavaScript-событие», идентификаторы — точно как в таблице).
3. Скрипт 4.2: вставить номер счётчика вместо `0` в `COUNTER_ID`. Куда вставлять на сайте — в разделе 4.2 [?]; если это требует правки шаблона и в админке нет HTML-блока на все страницы — остановиться, отчёт «нужен Claude Code».
4. Проверка 4.3 — с `?_ym_debug=1`.

## Что вставить

Копия из [`site-blocks/tech/forma-otpravit-foto.md`](https://github.com/michaelspeshnev-1/mebelinside/blob/main/site-blocks/tech/forma-otpravit-foto.md), раздел 4:

#### 4. Цели Яндекс Метрики

##### 4.1. Создать в Метрике (Настройки → Цели → Добавить цель → «JavaScript-событие»)

| Цель (название) | Идентификатор | Когда срабатывает |
|---|---|---|
| Звонок (клик по телефону) | `click_call` | клик по любой ссылке `tel:` на сайте |
| WhatsApp | `click_wa` | клик по ссылке `wa.me` / `api.whatsapp.com` |
| Telegram | `click_tg` | клик по ссылке `t.me/` |
| MAX | `click_max` | клик по ссылке `max.ru` |
| Форма «Отправить фото» | `form_photo_sent` | показ страницы «спасибо» после отправки формы |
| Квиз: начал | `quiz_start` | первое действие в калькуляторе (`#p-area` / `#p-meters`) |
| Квиз: заявка | `quiz_cta` | клик по кнопке результата калькулятора (`.cta`, `.cta2`) |
| Все заявки (составная) | — | составная цель из всех выше, кроме `quiz_start` — для отчётов |

Старые идентификаторы из `blok-otpravit-foto.html` (`lead_photo_wa|max|tg|call`) **не создавать** — заменены этими.
Где был клик, передаётся параметром визита `place` (шапка, блок «Отправить фото», подвал, карточка…).

##### 4.2. Скрипт (один на весь сайт)

Куда: тот же файл, где стоит счётчик Метрики [?] (найти: Дизайн → Шаблоны → поиск `mc.yandex.ru`, или модуль/поле
«Код Метрики» в настройках), **сразу после кода счётчика**. Если счётчик стоит модулем — в
`abt__unitheme2/templates/hooks/index/head_scripts.post.tpl` (там уже живёт калькулятор, `TZ-kalkulyator-pravki.md`) —
обернуть в `{literal}…{/literal}`, иначе Smarty сломает фигурные скобки.

```html
<script>
/* Цели Метрики — Мебель Inside. COUNTER_ID — номер счётчика Метрики [?]: Метрика → Настройки → «Номер счётчика»
   или Ctrl+U на сайте → ym(ЧИСЛО, "init"). */
(function () {
  var COUNTER_ID = 0; // [?] заменить 0 на номер счётчика (пока 0 — цели не отправляются)

  function goal(name, params) {
    try { if (COUNTER_ID && typeof ym === 'function') ym(COUNTER_ID, 'reachGoal', name, params || {}); } catch (e) {}
  }

  function placeOf(el) {
    if (el.closest('#miPhoto, .mi-photo')) return 'blok_foto';
    if (el.closest('header, .tygh-header, .tygh-top-panel')) return 'shapka';
    if (el.closest('footer, .tygh-footer')) return 'podval';
    return 'stranica';
  }

  // Звонок и мессенджеры — по всем ссылкам сайта (шапка, подвал, блоки, карточки)
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var h = a.getAttribute('href') || '';
    var p = { place: placeOf(a), page: location.pathname };
    if (/^tel:/i.test(h)) goal('click_call', p);
    else if (/wa\.me|whatsapp\.com/i.test(h)) goal('click_wa', p);
    else if (/\/\/t\.me\//i.test(h)) goal('click_tg', p);
    else if (/max\.ru/i.test(h)) goal('click_max', p);
  }, true);

  // Квиз/калькулятор (разметка из head_scripts.post.tpl: панели #p-area и #p-meters, кнопки .cta и .cta2)
  var quizStarted = false;
  document.addEventListener('input', function (e) {
    if (quizStarted) return;
    if (e.target.closest && e.target.closest('#p-area, #p-meters')) { quizStarted = true; goal('quiz_start'); }
  }, true);
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('#p-area .cta, #p-meters .cta, #p-area .cta2, #p-meters .cta2');
    if (b) goal('quiz_cta', { page: location.pathname });
  }, true);

  // Форма «Отправить фото»: страница после отправки ([?] проверить параметр в п. 2.8 — здесь sent=Y)
  if (/[?&]sent=Y\b/.test(location.search) && /otpravit-foto/.test(location.pathname)) {
    goal('form_photo_sent', { page: document.referrer || '' });
  }
})();
</script>
```

Замечания:
- Клик по кнопке WhatsApp в калькуляторе (`.cta2`) посчитается и как `click_wa`, и как `quiz_cta` — это нормально:
  в отчёте видно и канал, и что человек пришёл из квиза.
- Если форма выводится блоком на других страницах (п. 2.7), после отправки адрес будет не `/otpravit-foto/` [?] —
  тогда убрать условие `otpravit-foto` и оставить только `sent=Y` (после проверки, что `sent=Y` больше нигде не встречается).
- Если в Метрике включён «Вебвизор/Отслеживание форм» — дополнительная автоцель «Отправка формы» не мешает, но в отчётах
  ориентироваться на `form_photo_sent`.

##### 4.3. Проверка (обязательно, иначе KPI итерации 1 не посчитать)

1. Открыть сайт с `?_ym_debug=1` в адресе (например `https://mebelinside.ru/?_ym_debug=1`) → F12 → Консоль.
2. Нажать телефон в шапке, WhatsApp/Telegram/MAX в блоке, кнопку калькулятора, отправить тестовую форму.
3. В консоли — строки `Reach goal` с нужным идентификатором и `place`. Нет строки → цель не сработала.
4. Через 10–30 минут — Метрика → Отчёты → Конверсии: по каждой цели есть хотя бы 1 достижение.
5. Тестовую заявку удалить из почты, в журнал — «6 целей пишут данные» (KPI R18).

*(конец раздела «Что вставить»)*

## Проверка

- `https://mebelinside.ru/?_ym_debug=1` → F12 → Консоль: при клике WhatsApp/Telegram/MAX/телефон видно событие с именем цели.
- В Метрике цели появились (данные — через несколько часов).
- Перед проверкой сбросить кэш: https://mebelinside.ru/adminmeb.php?cc&ctpl, страницу открывать в новой вкладке.

## Нельзя

- Код счётчика Метрики не трогать и не дублировать.
- Ничего не удалять (страницы, категории, блоки, товары, файлы) — ненужное выключать (статус «Выключено»/«Скрыто»).
- 301-редирект — только если он прямо назван в этой карточке как решённый Михаилом; любой другой — сначала «да» Михаила.
- Не трогать «Пользовательские CSS» (Дизайн → Редактор тем) — однажды это дало белый экран сайта.
- Не выдумывать: предложение с пометкой [?] в видимом тексте не вставлять (убрать целиком); HTML-комментарии `<!-- … -->` на сайте не видны — их можно оставить.

## Отчёт

Одной строкой Михаилу (он перешлёт в «Главный»):

`п. 12 — Метрика: целей создано N, скрипт <вставлен в …/не вставлен: …>, `_ym_debug` <события видны/нет>`

Дальше: [12e-podval.md](https://github.com/michaelspeshnev-1/mebelinside/blob/main/zalivka/12e-podval.md)
