# 20. Калькулятор: замер по правилу + кликабельные контакты (Михаил 08.10, 🔥)

Замечание Михаила 08.10 (скрин): в калькуляторе кнопка «Заказать **бесплатный** замер» и подпись
«Замер и дизайн-проект — бесплатно», хотя замер бесплатный только после просчёта. Окно «Свяжитесь
с нами» — системный `alert`: телефоны не нажимаются, WhatsApp/Telegram/MAX не открываются.
Эта карточка заменяет пп. 2–3 из `TZ-kalkulyator-pravki.md`: вместо `alert` будет своё окно со ссылками.

**Файл:** `abt__unitheme2/templates/hooks/index/head_scripts.post.tpl`
(админка: Дизайн → Шаблоны → abt__unitheme2 → templates → hooks → index).
Файл выводится **на всех страницах** — сначала сделать резервную копию содержимого.
Блок калькулятора встречается **дважды** (`#p-area` и `#p-meters`) — править оба.

## 1. Тексты (в обеих панелях)

| Было | Стало |
|---|---|
| кнопка «Заказать бесплатный замер» | «Получить точный расчёт» |
| «Срок изготовления: 30–60 дней» | «Срок изготовления: 45–60 дней · AGT — от 30 дней» |
| «Замер и дизайн-проект — бесплатно» | «3D-проект — бесплатно. Замер — бесплатно после просчёта в шоуруме; без просчёта 1500 ₽ Пятигорск, 2000 ₽ КМВ — вычитаем из заказа» |
| подпись «…точная стоимость — после бесплатного замера» | «…точная стоимость — после замера» |

## 2. Кнопка

Было: `<button class="cta" onclick="callback()">Заказать бесплатный замер</button>`
Стало: `<button class="cta" onclick="callback()">Получить точный расчёт</button>`
(имя функции оставляем `callback` — меньше правок; меняется только её тело, п. 3).

## 3. Функция `callback()` — заменить целиком

Найти `function callback(){ … }` (внутри — `alert('Свяжитесь с нами:…')`) и заменить на:

```javascript
function callback(){
  var d=document, old=d.getElementById('mi-cb');
  if(old){ old.style.display='flex'; return; }
  var max='';
  try{ var m=(parent.document||d).querySelector('a[href*="max.ru"]'); if(m) max=m.href; }catch(e){}
  var B='display:block;margin:8px 0;padding:12px 14px;border-radius:10px;text-decoration:none;font:600 16px/1.2 sans-serif;text-align:center;';
  var h='<div style="background:#fff;color:#222;max-width:360px;width:92%;border-radius:16px;padding:22px;box-shadow:0 10px 40px rgba(0,0,0,.4)">'
   +'<div style="font:700 18px sans-serif;margin-bottom:6px">Свяжитесь с нами</div>'
   +'<div style="font:14px/1.4 sans-serif;color:#555;margin-bottom:10px">Пришлите размеры или план — посчитаем точно и сделаем 3D-проект бесплатно.</div>'
   +'<a target="_top" href="tel:+79289516342" style="'+B+'background:#1f9d55;color:#fff">📞 +7 928 951-63-42</a>'
   +'<a target="_top" href="tel:+79034440781" style="'+B+'background:#1f9d55;color:#fff">📞 +7 903 444-07-81</a>'
   +'<a target="_blank" rel="noopener" href="https://api.whatsapp.com/send?phone=79289516342&text=%D0%97%D0%B4%D1%80%D0%B0%D0%B2%D1%81%D1%82%D0%B2%D1%83%D0%B9%D1%82%D0%B5!%20%D0%A5%D0%BE%D1%87%D1%83%20%D1%82%D0%BE%D1%87%D0%BD%D1%8B%D0%B9%20%D1%80%D0%B0%D1%81%D1%87%D1%91%D1%82" style="'+B+'background:#25d366;color:#fff">WhatsApp</a>'
   +'<a target="_blank" rel="noopener" href="https://t.me/mebel_inside" style="'+B+'background:#2aabee;color:#fff">Telegram</a>'
   +(max?'<a target="_blank" rel="noopener" href="'+max+'" style="'+B+'background:#6b4eff;color:#fff">MAX</a>':'')
   +'<a href="#" onclick="document.getElementById(\'mi-cb\').style.display=\'none\';return false" style="'+B+'color:#555;background:#eee">Закрыть</a>'
   +'</div>';
  var w=d.createElement('div'); w.id='mi-cb';
  w.style.cssText='position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;z-index:99999';
  w.innerHTML=h;
  w.addEventListener('click',function(e){ if(e.target===w) w.style.display='none'; });
  d.body.appendChild(w);
}
```

Что делает: и на телефоне, и на компьютере открывается окно с **кнопками**: два телефона (`tel:` —
на телефоне сразу звонок), WhatsApp (с готовым «Здравствуйте! Хочу точный расчёт»), Telegram,
MAX — если на сайте в шапке/подвале есть ссылка на `max.ru` (прямой ссылки MAX в репозитории нет —
[?] Михаил, пришлите её, впишем явно). Закрывается кнопкой или кликом по фону.

## 4. Проверка (после сохранения, Ctrl+F5 / сброс кэша шаблонов)

1. Главная и карточка товара открываются, вёрстка цела (файл общий для всех страниц).
2. `/rasschitat-stoimost.html`, `/raschet-stoimosti-kuhni.html`: кнопка «Получить точный расчёт» →
   окно; клик по телефону предлагает звонок, WhatsApp/Telegram открываются в новой вкладке.
3. Слова «бесплатный замер» на странице нет (Ctrl+F «бесплатн» — только «3D-проект — бесплатно»
   и «бесплатно после просчёта»).
4. Сломалось — вернуть резервную копию. Отчёт одной строкой Главному.

## Не трогаем

Цены классов (Эконом/Оптимум/Премиум за п.м.) — оставлены как есть по решению в
`TZ-kalkulyator-pravki.md` п. 6; отдельный вопрос Михаилу, см. журнал 08.10.
