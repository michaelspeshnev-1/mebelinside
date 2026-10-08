# 14k-materialy-ssylki · Материалы: плитки хаба и ссылки из категорий кухонь

Задание: п. 14 · ~20 мин · Админка: https://mebelinside.ru/adminmeb.php

## Что сделать

1. Хаб (карточка 14a): раскомментировать/добавить плитки и строки таблицы раздела 6 — только для страниц, которые уже 200.
2. В описание каждой категории кухонь из таблиц разделов 5 и 7 — одна строка-ссылка (в конец описания, отдельным `<p>`).
3. Страницы брендов (`/arpa.html`, `/evogloss.html`, `/egger.html`, `/lamarty.html`, `/agt.html`, `/renner.html`, `/staron-ru.html`, `/hi-max.html`, `/grandex.html`, `/slotex.html`): строка «Где используем — <ссылка на материал>», только если страница бренда открывается.
4. `/wood/` — вне CS-Cart: если не правится из админки — пропустить, записать.

## Что вставить

Копия из [`MATERIALY-stranitsy-teksty.md`](https://github.com/michaelspeshnev-1/mebelinside/blob/main/MATERIALY-stranitsy-teksty.md), раздел 5:

### 5. Обратные ссылки (куда добавить ссылки на новые страницы)

По `ARHITEKTURA-sayta-v2.md` п. 1.2 и 3 — в описание каждой категории кухонь одна строка со ссылкой на материал:

| Категория | Строка в описание |
|---|---|
| `https://mebelinside.ru/mebel-dlya-doma-ru/kuhni/kuhni-na-zakaz-v-pyatigorske/kuhni-s-fasadami-mdf-emal-patina/` | Чем хороша эмаль и как за ней ухаживать — <a href="https://mebelinside.ru/fasady-mdf-emal.html">МДФ в эмали и с патиной</a>. |
| `https://mebelinside.ru/mebel-dlya-doma-ru/kuhni/kuhni-na-zakaz-v-pyatigorske/kuhni-s-fasadami-mdf-plastik/` | Плюсы, минусы и уход — <a href="https://mebelinside.ru/fasady-plastik.html">пластиковые фасады HPL</a>. (Сюда же 301 со старой категории «пластик в алюминиевом профиле».) |
| `https://mebelinside.ru/mebel-dlya-doma-ru/kuhni/kuhni-na-zakaz-v-pyatigorske/agt-uv-lak/` | Почему такие кухни делаются от 30 дней — <a href="https://mebelinside.ru/fasady-agt.html">фасады AGT и EvoGloss</a>. |
| `https://mebelinside.ru/mebel-dlya-doma-ru/kuhni/kuhni-na-zakaz-v-pyatigorske/kuhni-iz-laminirovannogo-dsp-kromka-pvh/` | Что важно знать о кромке и уходе — <a href="https://mebelinside.ru/ldsp-dlya-mebeli.html">ЛДСП с кромкой ПВХ</a>. |

Плюс: в блоке 2.4 «Материалы и фурнитура» на посадочной кухонь (`PAGES-glavnaya-i-kuhni-drafty.md`) ссылку «материалы и декоры» оставить на хаб `/materialy/`; на страницы брендов `/arpa.html`, `/evogloss.html`, `/egger.html`, `/lamarty.html`, `/agt.html` добавить строку «Где используем — <ссылка на материал>» (сейчас на них ведёт только подвал).

Копия из [`MATERIALY-2-stranitsy-teksty.md`](https://github.com/michaelspeshnev-1/mebelinside/blob/main/MATERIALY-2-stranitsy-teksty.md), разделы 6–7:

### 6. Хаб `/materialy/`: плитки и таблица (дополнить)

Когда страницы залиты — раскомментировать плитки 5–9 в блоке 0.2 `MATERIALY-stranitsy-teksty.md`:
```html
<a class="mi-mat-tile" href="https://mebelinside.ru/fasady-mdf-plenka.html"><img src="" alt="МДФ в плёнке ПВХ — фасады кухни" loading="lazy"><b>МДФ в плёнке ПВХ</b><span>Мат, глянец, металлик, можно с фрезеровкой.</span></a>
<a class="mi-mat-tile" href="https://mebelinside.ru/fasady-cleaf.html"><img src="" alt="Фасады Cleaf — фактура дерева и бетона" loading="lazy"><b>Cleaf</b><span>Итальянские плиты с фактурой дерева и камня.</span></a>
<a class="mi-mat-tile" href="https://mebelinside.ru/fasady-shpon.html"><img src="" alt="Фасады из натурального шпона" loading="lazy"><b>Шпон</b><span>Настоящее дерево на стабильной основе МДФ.</span></a>
<a class="mi-mat-tile" href="https://mebelinside.ru/fasady-massiv.html"><img src="" alt="Фасады из массива дерева — классическая кухня" loading="lazy"><b>Массив дерева</b><span>Дуб, ясень, бук. Фрезеровка и патина для классики.</span></a>
<a class="mi-mat-tile" href="https://mebelinside.ru/stoleshnicy-akrilovyy-kamen-hpl.html"><img src="" alt="Столешница из акрилового камня" loading="lazy"><b>Столешницы</b><span>Акриловый камень, HPL и ламинат.</span></a>
```
Строки в таблицу 0.3 «Как выбрать материал фасадов»:
```html
<tr><td><a href="https://mebelinside.ru/fasady-mdf-plenka.html">МДФ в плёнке ПВХ</a></td><td>мат, глянец, металлик, фрезеровка</td><td>доступно, торцы без кромки</td><td>не любит жар и пар у техники</td><td>45–60 дней</td></tr>
<tr><td><a href="https://mebelinside.ru/fasady-cleaf.html">Cleaf</a></td><td>фактура дерева, камня, бетона</td><td>натуральный вид и рельеф</td><td>только прямой, дорогая коллекция</td><td>45–60 дней</td></tr>
<tr><td><a href="https://mebelinside.ru/fasady-shpon.html">Шпон</a></td><td>натуральное дерево, тонировка, лак</td><td>вид дерева, стабильнее массива</td><td>рисунок не повторить, выгорает на солнце</td><td>45–60 дней, ближе к верхней границе</td></tr>
<tr><td><a href="https://mebelinside.ru/fasady-massiv.html">Массив дерева</a></td><td>фрезеровка, патина, резьба</td><td>долговечность, реставрация</td><td>самый дорогой, боится перепадов влажности</td><td>45–60 дней, ближе к верхней границе</td></tr>
```

### 7. Обратные ссылки (в описания категорий кухонь)

| Категория | Строка в описание |
|---|---|
| `https://mebelinside.ru/mebel-dlya-doma-ru/kuhni/kuhni-na-zakaz-v-pyatigorske/kuhni-s-fasadami-mdf-plenka-matovaya-glyancevaya-metallik/` | Чем хороша плёнка и как за ней ухаживать — <a href="https://mebelinside.ru/fasady-mdf-plenka.html">МДФ в плёнке ПВХ</a>. |
| `https://mebelinside.ru/mebel-dlya-doma-ru/kuhni/kuhni-na-zakaz-v-pyatigorske/kuhni-s-fasadami-cleaf/` | Что такое Cleaf, плюсы и минусы — <a href="https://mebelinside.ru/fasady-cleaf.html">фасады Cleaf</a>. |
| `https://mebelinside.ru/mebel-dlya-doma-ru/kuhni/kuhni-na-zakaz-v-pyatigorske/kuhni-iz-massiva-dereva/` | Как живёт дерево и как за ним ухаживать — <a href="https://mebelinside.ru/fasady-massiv.html">фасады из массива</a>. |
| `https://mebelinside.ru/mebel-dlya-doma-ru/kuhni/kuhni-na-zakaz-v-pyatigorske/kuhnya-s-barnoy-stoykoy/` | Из чего сделать стойку и столешницу — <a href="https://mebelinside.ru/stoleshnicy-akrilovyy-kamen-hpl.html">акриловый камень, HPL и ламинат</a>. |
| `/wood/` | Ссылки на <a href="https://mebelinside.ru/fasady-shpon.html">шпон</a> и <a href="https://mebelinside.ru/fasady-massiv.html">массив</a>. |

Плюс на страницы брендов (строка «Где используем — …»): `/renner.html` → эмаль, шпон, массив; `/staron-ru.html`,
`/hi-max.html`, `/grandex.html`, `/slotex.html` → столешницы; `/arpa.html` → пластик и столешницы.
На странице `/fasady-plastik.html` фразу про Slotex можно дополнить ссылкой на столешницы.

*(конец раздела «Что вставить»)*

## Проверка

- В каждой из категорий кухонь внизу описания — строка со ссылкой на материал, ссылка 200.
- Перед проверкой сбросить кэш: https://mebelinside.ru/adminmeb.php?cc&ctpl, страницу открывать в новой вкладке.

## Нельзя

- Ничего не удалять (страницы, категории, блоки, товары, файлы) — ненужное выключать (статус «Выключено»/«Скрыто»).
- 301-редирект — только если он прямо назван в этой карточке как решённый Михаилом; любой другой — сначала «да» Михаила.
- Не трогать «Пользовательские CSS» (Дизайн → Редактор тем) — однажды это дало белый экран сайта.
- Не выдумывать: предложение с пометкой [?] в видимом тексте не вставлять (убрать целиком); HTML-комментарии `<!-- … -->` на сайте не видны — их можно оставить.

## Отчёт

Одной строкой Михаилу (он перешлёт в «Главный»):

`п. 14 — ссылки на материалы: категорий N, брендов M, плитки хаба <…>; пропущено: <…>`

Дальше: [15a-kuhni-klassicheskie.md](https://github.com/michaelspeshnev-1/mebelinside/blob/main/zalivka/15a-kuhni-klassicheskie.md)
