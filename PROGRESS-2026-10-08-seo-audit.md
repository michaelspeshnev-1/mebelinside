# PROGRESS 2026-10-08 — живой аудит сайта (R33) + остатки «30–45 дней» (R27)

Скрипт `tools/seo_audit.py https://mebelinside.ru`, 776 URL из sitemap.xml, запуск 08.10.2026 на ПК. Полная таблица — `audit.csv` (не в git, 750 КБ; пересоздаётся командой).

## Главное
- Редиректов, цепочек, битых canonical, noindex в sitemap, внутренних ссылок на редиректы — **0**. Sitemap чистый.
- **Не 200:** `/hi-max.html` (код 0 — не отвечает/таймаут) — проверить, нужна ли страница, иначе убрать из sitemap.
- **Нет title/description — 55 страниц:** 2 категории фабричных шкафов (`shkafy-kupe-fabrichnye/3-hdvernye/`, `.../shkafy-kupe-stil/`), `/rasschitat-stoimost.html` и ~25 страниц брендов техники/мойки (`/midea.html`, `/franke.html` …; ~149 слов — одновременно «тонкие»).
- **H1 не один:** главная — **0 H1** (!), `/materialy.html` — 9, `/raschet-stoimosti-kuhni.html` и `/raschet-stoimosti-shkafa-kupe.html` — 0, ещё 6 страниц с 2 H1 (кровати, ткани, кожа, гардеробная 2×2, `/vozvrat.html`, `/contact.html`).
- **Тонкие (<150 слов): 49** — калькуляторы (69 слов), бренды техники (149).
- **Дубли title: 6 групп** (столы обеденные, мебель для ванной, диван Инсайд 24, «О компании», «Кухня на заказ - Кухня МДФ + пленка» ×10); **дубли H1: 7 групп** (в т. ч. «Мебель для дома», «Мебель для бизнеса», «Шкафы-купе» по 2×).

## «30–45 дней» (R27)
Найдено **23 страницы** (карточки кухонь + `/proizvodstvo.html` + 1 гардеробная): список — в `audit.csv` (поиск 30–45 в title/description/H1). Исправлять на «45–60 дней» (AGT/Эвоглосс — «от 30») после решения, делать ли это массово по карточкам.

## Выводы для ROADMAP
Новые строки R62–R66 (раздел SEO).

## Вывод скрипта
```
== URL в sitemap: 776
  25/776
  50/776
  75/776
  100/776
  125/776
  150/776
  175/776
  200/776
  225/776
  250/776
  275/776
  300/776
  325/776
  350/776
  375/776
  400/776
  425/776
  450/776
  475/776
  500/776
  525/776
  550/776
  575/776
  600/776
  625/776
  650/776
  675/776
  700/776
  725/776
  750/776
  775/776

== не 200: 1
   (0, 'https://mebelinside.ru/hi-max.html')

== в sitemap, но с редиректом (в sitemap нужны конечные URL): 0

== цепочки >1 редиректа: 0

== canonical не совпадает с URL: 0

== нет canonical: 0

== noindex в sitemap: 0

== нет title / description: 55
   https://mebelinside.ru/mebel-dlya-doma-ru/shkafy-kupe/shkafy-kupe-fabrichnye/3-hdvernye/
   https://mebelinside.ru/mebel-dlya-doma-ru/shkafy-kupe/shkafy-kupe-fabrichnye/shkafy-kupe-stil/
   https://mebelinside.ru/rasschitat-stoimost.html
   https://mebelinside.ru/midea.html
   https://mebelinside.ru/electrolux.html
   https://mebelinside.ru/teka.html
   https://mebelinside.ru/granfest-mramor.html
   https://mebelinside.ru/maunfeld.html
   https://mebelinside.ru/exiteq.html
   https://mebelinside.ru/aeg.html
   https://mebelinside.ru/smeg.html
   https://mebelinside.ru/graude.html
   https://mebelinside.ru/asko.html
   https://mebelinside.ru/ukinox.html
   https://mebelinside.ru/granfest-smart.html
   https://mebelinside.ru/franke.html
   https://mebelinside.ru/granfest-quarz.html
   https://mebelinside.ru/harte.html
   https://mebelinside.ru/granula.html
   https://mebelinside.ru/iddis.html
   https://mebelinside.ru/omoikiri.html
   https://mebelinside.ru/ewigstein.html
   https://mebelinside.ru/longran.html
   https://mebelinside.ru/faber.html
   https://mebelinside.ru/dach.html

== H1 не один: 10
   (0, 'https://mebelinside.ru')
   (2, 'https://mebelinside.ru/mebel-dlya-doma-ru/mebel-dlya-spalni/krovati/')
   (2, 'https://mebelinside.ru/myagkaya-mebel/mebelnye-tkani/tkani/')
   (2, 'https://mebelinside.ru/myagkaya-mebel/mebelnye-tkani/iskusstvennaya-kozha/')
   (2, 'https://mebelinside.ru/mebel-dlya-doma-ru/garderobnye/v-spalnyu/garderobnaya-2-m-na-2-m-v-spalne.html')
   (2, 'https://mebelinside.ru/vozvrat.html')
   (2, 'https://mebelinside.ru/contact.html')
   (9, 'https://mebelinside.ru/materialy.html')
   (0, 'https://mebelinside.ru/raschet-stoimosti-kuhni.html')
   (0, 'https://mebelinside.ru/raschet-stoimosti-shkafa-kupe.html')

== тонкие (<150 слов): 49
   (143, 'https://mebelinside.ru/rasschitat-stoimost.html')
   (69, 'https://mebelinside.ru/raschet-stoimosti-kuhni.html')
   (69, 'https://mebelinside.ru/raschet-stoimosti-shkafa-kupe.html')
   (149, 'https://mebelinside.ru/midea.html')
   (149, 'https://mebelinside.ru/electrolux.html')
   (149, 'https://mebelinside.ru/teka.html')
   (149, 'https://mebelinside.ru/maunfeld.html')
   (149, 'https://mebelinside.ru/exiteq.html')
   (149, 'https://mebelinside.ru/aeg.html')
   (149, 'https://mebelinside.ru/smeg.html')
   (149, 'https://mebelinside.ru/graude.html')
   (149, 'https://mebelinside.ru/asko.html')
   (149, 'https://mebelinside.ru/ukinox.html')
   (149, 'https://mebelinside.ru/franke.html')
   (149, 'https://mebelinside.ru/harte.html')
   (149, 'https://mebelinside.ru/granula.html')
   (149, 'https://mebelinside.ru/iddis.html')
   (149, 'https://mebelinside.ru/omoikiri.html')
   (149, 'https://mebelinside.ru/ewigstein.html')
   (149, 'https://mebelinside.ru/longran.html')
   (149, 'https://mebelinside.ru/faber.html')
   (149, 'https://mebelinside.ru/dach.html')
   (149, 'https://mebelinside.ru/rainford.html')
   (149, 'https://mebelinside.ru/falmec.html')
   (149, 'https://mebelinside.ru/elica.html')

== внутренние ссылки на редиректящие URL: 0

== дубли title: 6
   2× Столы обеденные на заказ в Пятигорске | Мебель Inside
   2× Мебель для ванной на заказ в Пятигорске | Мебель Inside
   10× Кухня на заказ - Кухня МДФ + пленка
   2× Диван Инсайд 24 на заказ в Пятигорске | Мебель Inside
   2× Кухня на заказ -
   2× О компании Мебель Инсайд

== дубли h1: 7
   2× Мебель для бизнеса
   2× Мебель для дома
   2× Шкафы-купе
   2× Столы обеденные
   2× Мебель для ванной
   2× Диван Инсайд 24
   2× Кухни на заказ в Пятигорске и КМВ

CSV: audit.csv
```
