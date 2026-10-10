# 05-glavnaya-faq-proizvodstvo · Главная: блоки «Частые вопросы» и «Собственное производство»

Задание: п. 5, R36 · ~25 мин · Админка: https://mebelinside.ru/adminmeb.php

## Что сделать

1. Дизайн → Макеты → вкладка «Главная». Скриншот макета до правки.
2. Найти текущий блок производства (подгружается скриптом). Если он есть в макете — шестерёнка → «Выключить» (не удалять). Если в макете его нет (он в шаблоне `head_scripts.post.tpl`) — не трогать шаблон в этой карточке, отметить в отчёте.
3. В тот же контейнер → «+» → «Добавить блок» → «Создать новый блок» → «HTML-блок», имя «MI Производство главная», режим «Исходный код» → вставить ВЕСЬ код блока 1. Оболочка — без заголовка.
4. Сверить список банков рассрочки в блоке 2 (вопрос про рассрочку) с тем, что сейчас на сайте (подвал/страница оплаты). Ушедший банк убрать и из `<p>`, и из JSON-LD; если сверить негде — оставить как есть и написать в отчёте.
5. Ниже, над подвалом (после блока заявки) → новый «HTML-блок» «MI FAQ главная» → вставить ВЕСЬ код блока 2.
6. Сохранить, сбросить кэш.

## Что вставить

HTML вставлять в режиме «Исходный код» редактора (кнопка `</>`/«HTML»): визуальный редактор CS-Cart ломает `<script>`. Строки «Длины…», «Ключи…», «Примечание…» и текст между блоками — подсказки для тебя, на сайт их не вставлять.

##### Блок 1 — производство

Файл целиком: [site-blocks/proizvodstvo-glavnaya.html](https://github.com/michaelspeshnev-1/mebelinside/blob/main/site-blocks/proizvodstvo-glavnaya.html) · только текст для копирования: https://raw.githubusercontent.com/michaelspeshnev-1/mebelinside/main/site-blocks/proizvodstvo-glavnaya.html

```html
<!--
  БЛОК «СОБСТВЕННОЕ ПРОИЗВОДСТВО» ДЛЯ ГЛАВНОЙ mebelinside.ru (R36). Подготовлен 07.10.2026, агент «SEO».
  Зачем: сейчас блок производства и плашки банков на главной вставляются JavaScript-ом и ОТСУТСТВУЮТ
  в HTML, который отдаёт сервер (аудит 17.08, SEO-ai-poisk.md п. 2.1). ИИ-роботы (Алиса, Нейро, ChatGPT,
  Perplexity) JS почти не выполняют — для них главного аргумента «свой цех» на главной нет.
  Этот блок — обычный HTML + CSS, без JS. Все классы с префиксом mi-, стили только внутри .mi-prod.
  Факты: свой цех с 2009, 1000+ заказов, 45–60 дней (Эвоглосс/AGT — от 30), гарантия 2 года, ЧПУ-раскрой,
  присадка, кромка, обработка акрилового камня и HPL (НЕ литьё), монтаж сами. Woodtec не упоминаем.

  КУДА ВСТАВЛЯТЬ (CS-Cart):
  1. Админка → Дизайн → Макеты → вкладка «Главная» (Home page).
  2. Найти текущий блок производства (тот, что подгружается скриптом) — запомнить его место и
     ВЫКЛЮЧИТЬ его (шестерёнка → «Выключить»), не удалять: так откат займёт один клик.
  3. В тот же контейнер → «+» → «Добавить блок» → «Создать новый блок» → тип «HTML-блок».
     Название: «MI Производство главная». Во вкладке «Содержимое» выключить визуальный редактор
     (режим «HTML»/«Исходный код») и вставить ВЕСЬ код ниже этого комментария. Сохранить.
  4. Оболочка блока — без заголовка (заголовок H2 уже внутри блока).
  5. Если старый блок производства не в макете, а вставляется скриптом в шаблоне/«Вставка кода» —
     закомментировать только этот скрипт (сделать копию файла *.bak-ДАТА-claude перед правкой).
  6. Плашки банков (вторая секция ниже, .mi-banks) — то же: старые JS-плашки выключить, эту оставить.
     Если плашки банков уже есть в подвале обычным HTML — секцию .mi-banks удалить из вставки.
     ПЕРЕД ВСТАВКОЙ проверить актуальность списка банков.

  КАК ПРОВЕРИТЬ:
  - Главная в инкогнито: блок на месте; на телефоне (375 px) карточки в 2 колонки, список в 1.
  - Ctrl+U (исходный код) → поиск «Собственное производство» и «ЧПУ-раскрой» — текст ДОЛЖЕН быть в коде.
    (Если находится только через «Просмотреть код элемента», но не через Ctrl+U — блок всё ещё рисует JS.)
  - Ссылки «Посмотреть цех» и «Оплата и рассрочка» открываются (200).
  - python3 tools/seo_audit.py https://mebelinside.ru --limit 5 — без новых ошибок.

  КАК ОТКАТИТЬ:
  - Дизайн → Макеты → Главная → «MI Производство главная» → «Выключить»; старый блок → «Включить».
    Очистить кеш: Администрирование → Хранилище → Очистить кеш.
-->
<style>
.mi-prod{max-width:1100px;margin:40px auto;padding:32px 16px;color:#2d2a26;font-size:16px;line-height:1.6;box-sizing:border-box}
.mi-prod *{box-sizing:border-box}
.mi-prod__title{margin:0 0 8px;font-size:28px;line-height:1.25}
.mi-prod__lead{margin:0 0 24px;max-width:760px}
.mi-prod__facts{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:0 0 28px;padding:0;list-style:none}
.mi-prod__fact{background:#f4f1ea;border-radius:8px;padding:18px 16px;border-top:3px solid #c9a55c}
.mi-prod__num{display:block;font-size:28px;font-weight:700;line-height:1.1;color:#15533f}
.mi-prod__cap{display:block;margin-top:6px;font-size:14px;line-height:1.4;color:#5c574f}
.mi-prod__cols{display:grid;grid-template-columns:1fr 1fr;gap:28px}
.mi-prod__sub{margin:0 0 10px;font-size:19px;line-height:1.3}
.mi-prod__list{margin:0;padding:0;list-style:none}
.mi-prod__list li{position:relative;padding:0 0 10px 26px}
.mi-prod__list li::before{content:"";position:absolute;left:4px;top:9px;width:10px;height:10px;border-radius:2px;background:#15533f}
.mi-prod__links{margin:24px 0 0}
.mi-prod__btn{display:inline-block;margin:0 10px 10px 0;padding:12px 22px;border-radius:6px;background:#2d2a26;color:#fff!important;text-decoration:none;font-weight:600}
.mi-prod__btn--ghost{background:transparent;color:#2d2a26!important;border:2px solid #2d2a26}
.mi-banks{max-width:1100px;margin:0 auto 40px;padding:18px 16px;border:1px solid #e6e0d4;border-radius:8px;background:#fbf9f4;font-size:15px;line-height:1.5;color:#2d2a26;box-sizing:border-box}
.mi-banks__title{margin:0 0 8px;font-size:17px;font-weight:600}
.mi-banks__list{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 8px;padding:0;list-style:none}
.mi-banks__list li{padding:6px 12px;border-radius:20px;background:#fff;border:1px solid #e6e0d4;white-space:nowrap}
.mi-banks a{color:#15533f}
.mi-banks__note{margin:0}
@media(max-width:900px){.mi-prod__facts{grid-template-columns:repeat(2,1fr)}}
@media(max-width:640px){.mi-prod{margin:28px auto;padding:20px 16px}.mi-prod__title{font-size:23px}.mi-prod__cols{grid-template-columns:1fr;gap:20px}.mi-prod__num{font-size:24px}.mi-prod__btn{display:block;text-align:center;margin:0 0 10px}}
</style>
<section class="mi-prod" id="miProd">
  <h2 class="mi-prod__title">Собственное производство</h2>
  <p class="mi-prod__lead"><b>Мебель Инсайд — фабрика корпусной мебели полного цикла в Пятигорске.</b> Проектируем, изготавливаем в своём цехе, доставляем и устанавливаем сами — без посредников и перепродажи.</p>
  <ul class="mi-prod__facts">
    <li class="mi-prod__fact"><span class="mi-prod__num">с 2009</span><span class="mi-prod__cap">года работает наш цех в Пятигорске</span></li>
    <li class="mi-prod__fact"><span class="mi-prod__num">1000+</span><span class="mi-prod__cap">выполненных заказов</span></li>
    <li class="mi-prod__fact"><span class="mi-prod__num">45–60 дней</span><span class="mi-prod__cap">срок по договору; Эвоглосс и AGT — от 30 дней</span></li>
    <li class="mi-prod__fact"><span class="mi-prod__num">2 года</span><span class="mi-prod__cap">гарантия по договору</span></li>
  </ul>
  <div class="mi-prod__cols">
    <div>
      <h3 class="mi-prod__sub">Что делаем в цеху</h3>
      <ul class="mi-prod__list">
        <li>ЧПУ-раскрой ЛДСП</li>
        <li>Присадка — отверстия под фурнитуру по проекту</li>
        <li>Кромкование деталей</li>
        <li>Обработка искусственного акрилового камня и HPL-пластика для столешниц</li>
        <li>Сборка, доставка и монтаж — своими мастерами</li>
      </ul>
    </div>
    <div>
      <h3 class="mi-prod__sub">Что это даёт вам</h3>
      <ul class="mi-prod__list">
        <li>Бесплатный 3D-проект: видите мебель до распила, правки — до запуска в цех</li>
        <li>Смета с марками и артикулами материалов и фурнитуры</li>
        <li>Фурнитура Blum, Hettich, Makmart — по выбору и бюджету</li>
        <li>Срок фиксируется в договоре</li>
        <li>Работаем по Пятигорску и всему КМВ</li>
      </ul>
    </div>
  </div>
  <p class="mi-prod__links">
    <a class="mi-prod__btn" href="https://mebelinside.ru/proizvodstvo.html">Посмотреть цех</a>
    <a class="mi-prod__btn mi-prod__btn--ghost" href="https://mebelinside.ru/materialy/">Материалы и декоры</a>
  </p>
</section>
<section class="mi-banks" id="miBanks">
  <p class="mi-banks__title">Рассрочка и кредит на мебель</p>
  <ul class="mi-banks__list">
    <li>ОТП Банк</li>
    <li>Халва · Совкомбанк</li>
    <li>Ренессанс Кредит</li>
    <li>Русский Стандарт</li>
    <li>Яндекс Пэй / Сплит</li>
  </ul>
  <p class="mi-banks__note">Оформление в шоуруме или онлайн. <a href="https://mebelinside.ru/oplata-i-dostavka.html">Оплата и рассрочка — подробнее</a></p>
</section>
```

##### Блок 2 — частые вопросы (+ разметка FAQPage)

Файл целиком: [site-blocks/faq-glavnaya.html](https://github.com/michaelspeshnev-1/mebelinside/blob/main/site-blocks/faq-glavnaya.html) · только текст для копирования: https://raw.githubusercontent.com/michaelspeshnev-1/mebelinside/main/site-blocks/faq-glavnaya.html

```html
<!--
  БЛОК «ЧАСТЫЕ ВОПРОСЫ» ДЛЯ ГЛАВНОЙ mebelinside.ru (R36). Подготовлен 07.10.2026, агент «SEO».
  Видимый текст и JSON-LD FAQPage сгенерированы из одного списка — совпадают ДОСЛОВНО.
  Если меняете вопрос или ответ — меняйте ОДИНАКОВО в HTML и в JSON-LD (иначе разметку снимут).
  Факты — только подтверждённые (KONTENT-ZAVOD.md, CENNOST-i-rubriki.md, PAGES-glavnaya-i-kuhni-drafty.md).
  Цен на кухни нет (подтверждена только цена шкафов-купе из МДФ). Без aggregateRating.
  Этот блок ЗАМЕНЯЕТ черновик FAQ из PAGES-glavnaya-i-kuhni-drafty.md, раздел 1.10 — второй FAQ на главную не ставить
  (на странице должна быть ОДНА разметка FAQPage).

  ПЕРЕД ВСТАВКОЙ ПРОВЕРИТЬ: список банков в вопросе про рассрочку — актуален ли (Яндекс Сплит, ОТП, Халва,
  Ренессанс, Русский Стандарт). Если банк ушёл — убрать его и из <p>, и из JSON-LD.

  КУДА ВСТАВЛЯТЬ (CS-Cart):
  1. Админка → Дизайн → Макеты → вкладка «Главная» (Home page).
  2. В нужном контейнере (ближе к низу, над подвалом, после блока заявки) → «+» → «Добавить блок» →
     «Создать новый блок» → тип «HTML-блок» (HTML block). Название: «MI FAQ главная».
  3. Во вкладке «Содержимое» ВЫКЛЮЧИТЬ визуальный редактор (кнопка «HTML»/«Исходный код»),
     вставить ВЕСЬ код этого файла ниже этого комментария (стили + section + script JSON-LD). Сохранить.
     Если визуальный редактор вырезает <script> или <details> — выбрать тип «HTML-блок с поддержкой Smarty»
     (Smarty-теги в коде не используются; фигурные скобки JSON обернуть в {literal}...{/literal}).
  4. Настройки блока: оболочка (wrapper) — без заголовка, чтобы не было двух «Частые вопросы».

  КАК ПРОВЕРИТЬ:
  - Открыть главную в окне инкогнито: блок виден, вопросы раскрываются кликом (без JS, тег <details>).
  - Ctrl+U (исходный код страницы) → поиск «FAQPage» и «Частые вопросы» — должны быть в серверном HTML.
  - https://webmaster.yandex.ru/tools/microtest/ (Валидатор микроразметки) и
    https://search.google.com/test/rich-results — вставить адрес главной: FAQPage без ошибок.
  - Телефон (ширина 375 px): текст не вылезает за край.
  - python3 tools/seo_audit.py https://mebelinside.ru --limit 5 — в колонке JSON-LD главной появится FAQPage.

  КАК ОТКАТИТЬ:
  - Дизайн → Макеты → Главная → у блока «MI FAQ главная» шестерёнка → «Выключить» (или «Удалить»).
    Остальные блоки не затрагиваются. Сбросить кеш: Администрирование → Хранилище → Очистить кеш.
-->
<style>
.mi-faq{max-width:960px;margin:40px auto;padding:0 16px;font-size:16px;line-height:1.6;color:#2d2a26;box-sizing:border-box}
.mi-faq *{box-sizing:border-box}
.mi-faq__title{margin:0 0 20px;font-size:28px;line-height:1.25}
.mi-faq__item{border-bottom:1px solid #e6e0d4}
.mi-faq__item:first-of-type{border-top:1px solid #e6e0d4}
.mi-faq__q{list-style:none;cursor:pointer;position:relative;padding:16px 40px 16px 0}
.mi-faq__q::-webkit-details-marker{display:none}
.mi-faq__q h3{margin:0;font-size:18px;line-height:1.4;font-weight:600;color:#15533f}
.mi-faq__q::after{content:"+";position:absolute;right:8px;top:12px;font-size:26px;line-height:1;color:#c9a55c;transition:transform .2s}
.mi-faq__item[open] .mi-faq__q::after{transform:rotate(45deg)}
.mi-faq__a{padding:0 0 18px}
.mi-faq__a p{margin:0}
.mi-faq__more{margin:20px 0 0;font-size:15px}
.mi-faq__more a{color:#15533f}
@media(max-width:600px){.mi-faq{margin:28px auto}.mi-faq__title{font-size:23px}.mi-faq__q h3{font-size:16px}}
</style>
<section class="mi-faq" id="miFaq">
  <h2 class="mi-faq__title">Частые вопросы</h2>
  <details class="mi-faq__item">
    <summary class="mi-faq__q"><h3>Сколько делается мебель на заказ?</h3></summary>
    <div class="mi-faq__a"><p>45–60 дней с момента согласования проекта, срок прописан в договоре. Фасады Эвоглосс и AGT — от 30 дней. Фрезерованные фасады, классика и эмаль занимают больше времени: фрезеровка, покраска и сушка добавляют срок. Кухни из массива — 60–80 дней.</p></div>
  </details>
  <details class="mi-faq__item">
    <summary class="mi-faq__q"><h3>Замер платный?</h3></summary>
    <div class="mi-faq__a"><p>Замер бесплатный после предварительного просчёта в шоуруме (Пятигорск, Кисловодское шоссе, 22, ТЦ «Пазл», 2 этаж). Выезд на замер без просчёта — 1500 ₽ по Пятигорску и 2000 ₽ по Ессентукам, Кисловодску, Минеральным Водам и Железноводску, эта сумма вычитается из стоимости заказа.</p></div>
  </details>
  <details class="mi-faq__item">
    <summary class="mi-faq__q"><h3>Можно увидеть мебель до изготовления?</h3></summary>
    <div class="mi-faq__a"><p>Да. 3D-проект делаем бесплатно: вы видите кухню или шкаф до распила, а правки вносим до запуска в производство.</p></div>
  </details>
  <details class="mi-faq__item">
    <summary class="mi-faq__q"><h3>Какая гарантия?</h3></summary>
    <div class="mi-faq__a"><p>2 года на изделия, гарантия закреплена в договоре.</p></div>
  </details>
  <details class="mi-faq__item">
    <summary class="mi-faq__q"><h3>Из каких материалов вы делаете мебель?</h3></summary>
    <div class="mi-faq__a"><p>Фасады — МДФ в эмали, МДФ в плёнке ПВХ, AGT, Rehau, Cleaf, Эвоглосс, пластик, шпон, массив дерева. Корпус — ЛДСП Egger с кромкой. Столешницы — искусственный акриловый камень (Samsung Staron, LG Hi-Macs, Grandex) и HPL-пластик. Марки и артикулы материалов указываем в смете.</p></div>
  </details>
  <details class="mi-faq__item">
    <summary class="mi-faq__q"><h3>Какую фурнитуру вы ставите?</h3></summary>
    <div class="mi-faq__a"><p>Blum (Австрия), Hettich, Grass, Makmart, DTC, Boyard — по вашему выбору и бюджету. Марка и артикулы фурнитуры фиксируются в смете.</p></div>
  </details>
  <details class="mi-faq__item">
    <summary class="mi-faq__q"><h3>Вы сами производите мебель?</h3></summary>
    <div class="mi-faq__a"><p>Да. Собственный цех в Пятигорске работает с 2009 года: ЧПУ-раскрой, присадка, кромка, обработка акрилового камня и HPL-пластика. Выполнено более 1000 заказов. Доставку и монтаж делаем своими силами.</p></div>
  </details>
  <details class="mi-faq__item">
    <summary class="mi-faq__q"><h3>В каких городах вы работаете?</h3></summary>
    <div class="mi-faq__a"><p>Пятигорск, Ессентуки, Кисловодск, Минеральные Воды, Железноводск, Лермонтов, Георгиевск и населённые пункты КМВ. Шоурум — в Пятигорске, Кисловодское шоссе, 22, ТЦ «Пазл», 2 этаж.</p></div>
  </details>
  <details class="mi-faq__item">
    <summary class="mi-faq__q"><h3>Сколько стоит мебель на заказ?</h3></summary>
    <div class="mi-faq__a"><p>Цена зависит от размеров, материалов фасадов и фурнитуры, поэтому кухни и гардеробные считаем по проекту. Шкафы-купе из МДФ — от 37 000 ₽ за погонный метр. Пришлите фото или планировку — дадим предварительный ориентир; точную сумму называем после замера и 3D-проекта. Доставка и подъём считаются отдельно, по факту.</p></div>
  </details>
  <details class="mi-faq__item">
    <summary class="mi-faq__q"><h3>Как оплатить и есть ли рассрочка?</h3></summary>
    <div class="mi-faq__a"><p>Оплата в два этапа: предоплата при заключении договора и остаток перед монтажом, суммы прописываются в договоре. Можно оплатить картой, по QR-коду (СБП), безналичным расчётом для организаций, а также в рассрочку или кредит: ОТП Банк, Халва (Совкомбанк), Ренессанс Кредит, Русский Стандарт, Яндекс Пэй / Сплит.</p></div>
  </details>
  <p class="mi-faq__more">Не нашли ответ? Позвоните <a href="tel:+79289516342">+7 928 951-63-42</a>, <a href="tel:+79034440781">+7 903 444-07-81</a> или <a href="#miPhoto">пришлите фото или планировку</a>.</p>
</section>
<script type="application/ld+json">
{
 "@context": "https://schema.org",
 "@type": "FAQPage",
 "mainEntity": [
  {
   "@type": "Question",
   "name": "Сколько делается мебель на заказ?",
   "acceptedAnswer": {
    "@type": "Answer",
    "text": "45–60 дней с момента согласования проекта, срок прописан в договоре. Фасады Эвоглосс и AGT — от 30 дней. Фрезерованные фасады, классика и эмаль занимают больше времени: фрезеровка, покраска и сушка добавляют срок. Кухни из массива — 60–80 дней."
   }
  },
  {
   "@type": "Question",
   "name": "Замер платный?",
   "acceptedAnswer": {
    "@type": "Answer",
    "text": "Замер бесплатный после предварительного просчёта в шоуруме (Пятигорск, Кисловодское шоссе, 22, ТЦ «Пазл», 2 этаж). Выезд на замер без просчёта — 1500 ₽ по Пятигорску и 2000 ₽ по Ессентукам, Кисловодску, Минеральным Водам и Железноводску, эта сумма вычитается из стоимости заказа."
   }
  },
  {
   "@type": "Question",
   "name": "Можно увидеть мебель до изготовления?",
   "acceptedAnswer": {
    "@type": "Answer",
    "text": "Да. 3D-проект делаем бесплатно: вы видите кухню или шкаф до распила, а правки вносим до запуска в производство."
   }
  },
  {
   "@type": "Question",
   "name": "Какая гарантия?",
   "acceptedAnswer": {
    "@type": "Answer",
    "text": "2 года на изделия, гарантия закреплена в договоре."
   }
  },
  {
   "@type": "Question",
   "name": "Из каких материалов вы делаете мебель?",
   "acceptedAnswer": {
    "@type": "Answer",
    "text": "Фасады — МДФ в эмали, МДФ в плёнке ПВХ, AGT, Rehau, Cleaf, Эвоглосс, пластик, шпон, массив дерева. Корпус — ЛДСП Egger с кромкой. Столешницы — искусственный акриловый камень (Samsung Staron, LG Hi-Macs, Grandex) и HPL-пластик. Марки и артикулы материалов указываем в смете."
   }
  },
  {
   "@type": "Question",
   "name": "Какую фурнитуру вы ставите?",
   "acceptedAnswer": {
    "@type": "Answer",
    "text": "Blum (Австрия), Hettich, Grass, Makmart, DTC, Boyard — по вашему выбору и бюджету. Марка и артикулы фурнитуры фиксируются в смете."
   }
  },
  {
   "@type": "Question",
   "name": "Вы сами производите мебель?",
   "acceptedAnswer": {
    "@type": "Answer",
    "text": "Да. Собственный цех в Пятигорске работает с 2009 года: ЧПУ-раскрой, присадка, кромка, обработка акрилового камня и HPL-пластика. Выполнено более 1000 заказов. Доставку и монтаж делаем своими силами."
   }
  },
  {
   "@type": "Question",
   "name": "В каких городах вы работаете?",
   "acceptedAnswer": {
    "@type": "Answer",
    "text": "Пятигорск, Ессентуки, Кисловодск, Минеральные Воды, Железноводск, Лермонтов, Георгиевск и населённые пункты КМВ. Шоурум — в Пятигорске, Кисловодское шоссе, 22, ТЦ «Пазл», 2 этаж."
   }
  },
  {
   "@type": "Question",
   "name": "Сколько стоит мебель на заказ?",
   "acceptedAnswer": {
    "@type": "Answer",
    "text": "Цена зависит от размеров, материалов фасадов и фурнитуры, поэтому кухни и гардеробные считаем по проекту. Шкафы-купе из МДФ — от 37 000 ₽ за погонный метр. Пришлите фото или планировку — дадим предварительный ориентир; точную сумму называем после замера и 3D-проекта. Доставка и подъём считаются отдельно, по факту."
   }
  },
  {
   "@type": "Question",
   "name": "Как оплатить и есть ли рассрочка?",
   "acceptedAnswer": {
    "@type": "Answer",
    "text": "Оплата в два этапа: предоплата при заключении договора и остаток перед монтажом, суммы прописываются в договоре. Можно оплатить картой, по QR-коду (СБП), безналичным расчётом для организаций, а также в рассрочку или кредит: ОТП Банк, Халва (Совкомбанк), Ренессанс Кредит, Русский Стандарт, Яндекс Пэй / Сплит."
   }
  }
 ]
}
</script>
```

*(конец раздела «Что вставить»)*

## Проверка

- На главной — «Собственное производство» и «Частые вопросы» (10 вопросов), открываются ответы.
- Ctrl+U (исходный код) → Ctrl+F «Свой цех» и «FAQPage» — находятся (значит, видны роботам, не через JS).
- Ctrl+F «литьё» и «Woodtec» на главной — 0 (если старый JS-блок выключить не удалось — записать).
- FAQPage на главной ровно один: Ctrl+U → Ctrl+F `"FAQPage"` — 1 совпадение.
- Телефон (F12 → режим телефона): блоки не вылезают за экран.
- Перед проверкой сбросить кэш: https://mebelinside.ru/adminmeb.php?cc&ctpl, страницу открывать в новой вкладке.

## Нельзя

- Старый FAQ из `PAGES-glavnaya-i-kuhni-drafty.md` (раздел 1.10) не ставить — FAQ на главной один.
- Шаблон `head_scripts.post.tpl` в этой карточке не редактировать (это карточка 08).
- Ничего не удалять (страницы, категории, блоки, товары, файлы) — ненужное выключать (статус «Выключено»/«Скрыто»).
- 301-редирект — только если он прямо назван в этой карточке как решённый Михаилом; любой другой — сначала «да» Михаила.
- Не трогать «Пользовательские CSS» (Дизайн → Редактор тем) — однажды это дало белый экран сайта.
- Не выдумывать: предложение с пометкой [?] в видимом тексте не вставлять (убрать целиком); HTML-комментарии `<!-- … -->` на сайте не видны — их можно оставить.

## Отчёт

Одной строкой Михаилу (он перешлёт в «Главный»):

`п. 5 — главная: блоки «Производство» и «FAQ» вставлены, старый блок производства <выключен / в шаблоне — не тронут>, банки <сверены / не с чем сверить>`

Дальше: [06a-glavnaya-bloki.md](https://github.com/michaelspeshnev-1/mebelinside/blob/main/zalivka/06a-glavnaya-bloki.md)
