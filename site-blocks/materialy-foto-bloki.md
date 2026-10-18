# Блоки с фото для страниц материалов (готово к вставке)

Подготовлено 18.10.2026. Фото уже лежат на хостинге: `/images/companies/1/pages/materialy-foto/` (26 файлов, проверены: все отдаются, 200).
Вставка: админка CS-Cart → Веб-сайт → Страницы → страница → вкладка «Общее» → поле «Описание», режим «Исходный код» (кнопка `</>`) → вставить блок **после вводного абзаца под H1**, перед первым H2 → «Сохранить». Эмодзи не использовать (утф8 обрезает).
Редактор: `jQuery('#elm_page_descr').redactor('code.get'/'code.set')`; сохранять кликом по «Сохранить» (иногда `jQuery(btn).trigger('click')`).
**Пилот — `/fasady-shpon.html`, затем остальные; проверить на живом сайте, IndexNow после каждой.**

Alt-подписи описательные, без утверждений про материал. Пометки `[?]` — для Михаила (материал на фото по каталогу не подтверждён), на сайт не идут.

## Фасады из натурального шпона — `/fasady-shpon.html`

Примечание: [?] shpon-1 в каталоге — «Модульная кухня Беверли Дуб Бурбон»: шпон не подтверждён, при сомнении заменить

```html
<div class="mi-mat-photos" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin:24px 0"><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-shpon-1.jpg" alt="Кухня с островом и фасадами цвета дуба" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-shpon-2.jpg" alt="Шпонированные стеновые панели с рисунком в виде дерева" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-shpon-3.jpg" alt="Кухня с пеналом из шпона ореха и белыми фасадами" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure></div>
```

## МДФ в эмали и с патиной — `/fasady-mdf-emal.html`

Примечание: [?] материал на фото (эмаль) по каталогу не подтверждён — проверить

```html
<div class="mi-mat-photos" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin:24px 0"><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-mdf-emal-1.jpg" alt="Белый распашной шкаф с филёнчатыми фасадами" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-mdf-emal-2.jpg" alt="Шкаф с матовыми коричневыми фасадами" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-mdf-emal-3.jpg" alt="Угловая кухня с белыми глянцевыми фасадами" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure></div>
```

## МДФ в плёнке ПВХ — `/fasady-mdf-plenka.html`

Примечание: [?] материал (плёнка ПВХ) по каталогу не подтверждён

```html
<div class="mi-mat-photos" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin:24px 0"><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-mdf-plenka-1.jpg" alt="Угловая кухня в стиле лофт: тёмные фасады и верх цвета дерева" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-mdf-plenka-2.jpg" alt="Угловая кухня с фасадами цвета мокко и белым верхом" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-mdf-plenka-3.jpg" alt="Кухня графитового цвета со вставками цвета дерева" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure></div>
```

## Пластиковые фасады HPL — `/fasady-plastik.html`

Примечание: [?] HPL на фото не подтверждён

```html
<div class="mi-mat-photos" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin:24px 0"><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-plastik-1.jpg" alt="Угловая кухня в стиле минимализм: графитовые фасады и верх цвета дерева" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-plastik-2.jpg" alt="Угловая кухня с белыми фасадами и верхом цвета дерева" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-plastik-3.jpg" alt="Белая кухня с глянцевыми фасадами" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure></div>
```

## Фасады AGT и EvoGloss — `/fasady-agt.html`

Примечание: [?] что это именно AGT — подтвердить

```html
<div class="mi-mat-photos" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin:24px 0"><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-agt-1.jpg" alt="Прихожая с белыми глянцевыми шкафами и скамьёй" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-agt-2.jpg" alt="Угловая кухня с белыми глянцевыми фасадами" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-agt-3.jpg" alt="Навесная тумба под телевизор, белый глянец" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure></div>
```

## Фасады Cleaf — `/fasady-cleaf.html`

Примечание: [?] Cleaf на фото не подтверждён; кадров только 2

```html
<div class="mi-mat-photos" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin:24px 0"><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-cleaf-1.jpg" alt="Кухня с графитовыми фасадами и вставками цвета дерева" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-cleaf-2.jpg" alt="Кухня с матовыми графитовыми фасадами и панелью цвета дерева" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure></div>
```

## Фасады из массива дерева — `/fasady-massiv.html`

Примечание: каталог: «Ника д’Оро» — «Массив Италия»; остальное не подтверждено. Wilsonart в характеристике этого товара не упоминать

```html
<div class="mi-mat-photos" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin:24px 0"><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-massiv-1.jpg" alt="Кабинет руководителя: шкафы и мебель из массива и шпона" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-massiv-2.jpg" alt="Светлая кухня в стиле неоклассика с витринами и подсветкой" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/fasady-massiv-3.jpg" alt="Кухня «Ника д’Оро» с фасадами из массива" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure></div>
```

## ЛДСП с кромкой ПВХ — `/ldsp-dlya-mebeli.html`

Примечание: [?] ЛДСП на фото 3 не подтверждена

```html
<div class="mi-mat-photos" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin:24px 0"><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/ldsp-dlya-mebeli-1.jpg" alt="Угловая кухня светлого цвета из ЛДСП" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/ldsp-dlya-mebeli-2.jpg" alt="Гардеробная комната из ЛДСП" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/ldsp-dlya-mebeli-3.jpg" alt="Кухня с белой столешницей и графитовыми фасадами" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure></div>
```

## Столешницы: акриловый камень, HPL и ламинат — `/stoleshnicy-akrilovyy-kamen-hpl.html`

Примечание: кадр 3 — наш объект в Баксане (подтверждено Михаилом); кадры 1–2: материал столешницы не подтверждён

```html
<div class="mi-mat-photos" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin:24px 0"><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/stoleshnicy-akrilovyy-kamen-hpl-1.jpg" alt="Подвесная тумба в ванной со столешницей и раковиной" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/stoleshnicy-akrilovyy-kamen-hpl-2.jpg" alt="Белая столешница на кухне с варочной панелью" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure><figure style="margin:0"><img src="/images/companies/1/pages/materialy-foto/stoleshnicy-akrilovyy-kamen-hpl-3.jpg" alt="Барная стойка со столешницей из акрилового камня и обшивкой рейками АГТ (Баксан)" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;display:block"></figure></div>
```
