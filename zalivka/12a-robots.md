# 12a-robots · robots.txt: дополнить

Задание: п. 12, техпакет шаг 2 · ~15 мин · Админка: https://mebelinside.ru/adminmeb.php

## Что сделать

1. Открыть https://mebelinside.ru/robots.txt — сохранить текст (скопировать в отчёт-бэкап).
2. Найти, где он правится: Веб-сайт → SEO → robots.txt [?]; если пункта нет — панель Timeweb → Файловый менеджер → корень сайта (где `index.php`) → `robots.txt`.
3. Вставить блок ниже в группу `User-agent: *` и в каждую отдельную группу Yandex/Googlebot, если они есть. `Clean-param` — один раз.
4. Строку `Disallow: /var/` НЕ добавлять, если не уверен, где лежат собранные CSS/JS (см. комментарии в файле).
5. Проверка в Яндекс Вебмастере → Инструменты → Анализ robots.txt (список URL — в конце файла).

## Что вставить

Файл: [site-blocks/tech/robots-dobavit.txt](https://github.com/michaelspeshnev-1/mebelinside/blob/main/site-blocks/tech/robots-dobavit.txt) · текст: https://raw.githubusercontent.com/michaelspeshnev-1/mebelinside/main/site-blocks/tech/robots-dobavit.txt

```
# ============================================================================
# robots.txt — ЧТО ДОБАВИТЬ (техпакет, волна A, 07.10.2026)
# Основа: ARHITEKTURA-sayta-v2.md, п. 4 — только технические URL.
# Смысловые страницы (лофт-дубли, /dizayn/, /kuhn/, /mebel-dlya-biznesa-ru/) здесь НЕ закрываем — после выгрузки R34.
#
# КАК ВСТАВЛЯТЬ (подробно — TECHPAKET-zalivka.md, шаг 1):
#  1. Сначала скачать текущий robots.txt (https://mebelinside.ru/robots.txt) и сохранить копию
#     в репозиторий: site-blocks/tech/robots-backup-ГГГГ-ММ-ДД.txt.
#  2. Блок «Disallow/Allow» ниже вставить в КАЖДУЮ группу, где он нужен: `User-agent: *`, а также
#     `User-agent: Yandex` и `User-agent: Googlebot`, если такие группы есть отдельно
#     (робот читает ТОЛЬКО свою группу, правила из `*` на него тогда не действуют). [?] открыть файл и посмотреть группы.
#     Группы ИИ-ботов (GPTBot, ClaudeBot, YandexAdditional и т. д.) не трогать — пусть остаются открытыми.
#  3. Строку уже существующую не дублировать (сравнить глазами).
#  4. НЕ трогать: `Disallow: /*features_hash=` (оставить как есть), строку `Sitemap:`, группы ИИ-ботов.
#  5. Пагинацию НЕ закрывать: ни `page=`, ни `/page-N/` — в списке ниже их нет и быть не должно.
# ============================================================================


# ---------- вставить в группу User-agent: * (и в Yandex / Googlebot, если они отдельные) ----------

# Сортировки, вид и число товаров на странице (дубли листингов)
Disallow: /*sort_by=
Disallow: /*sort_order=
Disallow: /*items_per_page=
Disallow: /*layout=

# Служебные параметры CS-Cart
Disallow: /*subcats=
Disallow: /*dispatch[

# Корзина, оформление, профиль, вход, заказы
Disallow: /*dispatch=checkout.
Disallow: /*dispatch=cart.
Disallow: /*dispatch=profiles.
Disallow: /*dispatch=auth.
Disallow: /*dispatch=orders.

# Поиск по сайту
Disallow: /*dispatch=products.search
Disallow: /*search_performed=
Disallow: /*?q=
Disallow: /*&q=

# Сравнение и избранное
Disallow: /*dispatch=product_features.compare
Disallow: /*dispatch=wishlist.

# Технические папки
Disallow: /images/enh_test/
Disallow: /backups/
Disallow: /api/
Disallow: /app/
Disallow: /var/
# ВАЖНО: CS-Cart собирает CSS/JS темы в /var/cache/misc/assets/ — их закрывать нельзя
# (Google и Яндекс должны видеть оформление). Allow длиннее Disallow — он побеждает.
# [?] Проверить: Ctrl+U на главной → найти «.css» и «.js» → если какой-то файл лежит в /var/ по другому пути,
#     добавить для этого пути свою строку Allow. Если не получается проверить — строку `Disallow: /var/` НЕ добавлять.
Allow: /var/cache/misc/assets/

# Админка: строку `Disallow: /adminmeb.php` из ARHITEKTURA п. 4 сознательно НЕ добавляем.
# Админка закрыта паролем и в индекс не попадает, а robots.txt публичный — строка подсказала бы
# любому, где вход в админку. Если Михаил всё же хочет — раскомментировать:
# Disallow: /adminmeb.php


# ---------- вставить ОДИН раз, в любом месте файла (директива Яндекса, межсекционная) ----------

# Метки рекламы и соцсетей: Яндекс склеивает URL с этими параметрами с чистым адресом.
# Google Clean-param не читает — для него нужен canonical на чистый URL (см. TECHPAKET-zalivka.md, шаг 1.4).
Clean-param: utm_source&utm_medium&utm_campaign&utm_content&utm_term&yclid&gclid&fbclid


# ---------- проверка после заливки ----------
# 1. https://mebelinside.ru/robots.txt открывается, новые строки видны.
# 2. Вебмастер → Инструменты → Анализ robots.txt: ошибок 0; вписать в «Разрешены ли URL?»:
#      https://mebelinside.ru/                                                   → разрешён
#      https://mebelinside.ru/mebel-dlya-doma-ru/kuhni/kuhni-na-zakaz-v-pyatigorske/          → разрешён
#      https://mebelinside.ru/mebel-dlya-doma-ru/kuhni/kuhni-na-zakaz-v-pyatigorske/?page=2   → разрешён (пагинация!)
#      https://mebelinside.ru/mebel-dlya-doma-ru/kuhni/kuhni-na-zakaz-v-pyatigorske/?sort_by=price&sort_order=asc → запрещён
#      https://mebelinside.ru/index.php?dispatch=checkout.cart                    → запрещён
#      https://mebelinside.ru/index.php?dispatch=products.search&q=кухня          → запрещён
#      https://mebelinside.ru/kuhni-na-zakaz-essentuki.html?utm_source=vk          → разрешён (склеится по Clean-param)
#      URL любого CSS из исходного кода главной                                   → разрешён
# 3. Google Search Console → Настройки → Отчёт robots.txt: файл прочитан без ошибок.
```

*(конец раздела «Что вставить»)*

## Проверка

- robots.txt открывается, старые строки на месте, новые добавлены.
- Вебмастер: главная, категории кухонь, страницы — «разрешён»; сортировки/корзина/поиск — «запрещён».
- Перед проверкой сбросить кэш: https://mebelinside.ru/adminmeb.php?cc&ctpl, страницу открывать в новой вкладке.

## Нельзя

- Не трогать `Disallow: /*features_hash=`, `Sitemap:`, группы ИИ-ботов.
- Не закрывать пагинацию.
- Не добавлять адрес админки.
- Ничего не удалять (страницы, категории, блоки, товары, файлы) — ненужное выключать (статус «Выключено»/«Скрыто»).
- 301-редирект — только если он прямо назван в этой карточке как решённый Михаилом; любой другой — сначала «да» Михаила.
- Не трогать «Пользовательские CSS» (Дизайн → Редактор тем) — однажды это дало белый экран сайта.
- Не выдумывать: предложение с пометкой [?] в видимом тексте не вставлять (убрать целиком); HTML-комментарии `<!-- … -->` на сайте не видны — их можно оставить.

## Отчёт

Одной строкой Михаилу (он перешлёт в «Главный»):

`п. 12 — robots.txt дополнен (<где правится>), проверка Вебмастера: <ок / что не так>`

Дальше: [12b-301-contact.md](https://github.com/michaelspeshnev-1/mebelinside/blob/main/zalivka/12b-301-contact.md)
