import re,json,os,subprocess,html as H
tpl=open('site-blocks/tech/backup-2026-10-08/b2b-index.html',encoding='utf-8').read()
pages=json.load(open('_gen/b2b.json',encoding='utf-8'))
want={'/b2b/ofisy/':'Офисы и кабинеты','/b2b/kafe-restorany-bary/':'Кафе, бары, рестораны','/b2b/magaziny/':'Магазины и торговое оборудование','/b2b/dizayneram/':'Дизайнерам и архитекторам'}
cache={}
def status(u):
    if u in cache: return cache[u]
    r=subprocess.run(['curl','-s','-o','/dev/null','-m','25','-w','%{http_code}',u],capture_output=True,text=True)
    cache[u]=r.stdout.strip(); return cache[u]
css_add='''<style>
.prose-sec{background:var(--cream);padding:64px 0}
.prose{max-width:820px;color:#2d2a26;font-size:1.05rem;line-height:1.75}
.prose h2{font-family:'Playfair Display',serif;font-size:clamp(1.5rem,2.6vw,2rem);margin:44px 0 14px;color:#101113}
.prose ul,.prose ol{padding-left:1.3em;margin:0 0 16px}.prose li{margin:0 0 8px}
.prose p{margin:0 0 16px}.prose table{border-collapse:collapse;width:100%;margin:12px 0 24px;font-size:.98rem}
.prose td,.prose th{border:1px solid #e6e0d4;padding:10px 12px;text-align:left;vertical-align:top}
.prose a{color:#15795C}.prose .mi-photo-btn{display:inline-block;padding:12px 22px;border-radius:6px;background:#101113;color:#fff!important;text-decoration:none;font-weight:600}
.prose details{border-bottom:1px solid #e6e0d4;padding:12px 0}.prose summary{cursor:pointer;font-weight:600}
</style>
'''
os.makedirs('_gen/b2b-out',exist_ok=True)
report=[]
for p in pages:
    if p['url'] not in want: continue
    body=p['blocks'][0]; ld=p['blocks'][1] if len(p['blocks'])>1 else ''
    body=re.sub(r'<!--.*?-->','',body,flags=re.S)
    ld=re.sub(r'<!--.*?-->','',ld,flags=re.S)
    body=re.sub(r'<div class="mi-cases">.*?</div>\s*','',body,flags=re.S)
    body=re.sub(r'<img[^>]*src=""[^>]*>','',body)
    body=body.replace('href="#miTz"','href="#miTz"')
    # unwrap dead internal links
    dead=[]
    def fix(m):
        u=m.group(1)
        if u.startswith('https://mebelinside.ru') and not u.endswith('#miTz'):
            base=u.split('#')[0]
            st=status(base)
            if not st.startswith(('2','3')):
                dead.append(u); return '<span>'+m.group(2)+'</span>'
        return m.group(0)
    body=re.sub(r'<a [^>]*?href="([^"]+)"[^>]*>(.*?)</a>',lambda m: fix(m),body,flags=re.S)
    # drop empty "Проекты" heading if nothing follows except removed stuff
    body=re.sub(r'<h2>Проекты</h2>\s*(<p><span>[^<]*</span></p>\s*)?(?=<h2>|$)','',body)
    ld=re.sub(r'\[\?\][^"]*','',ld)
    lead=re.search(r'<p><b>(.*?)</b>',body,flags=re.S)
    desc=p['desc']
    head=tpl[:tpl.find('<body>')]
    head=re.sub(r'<title>.*?</title>','<title>'+H.escape(p['title'],quote=False)+'</title>',head,flags=re.S)
    head=re.sub(r'<meta name="description" content="[^"]*"','<meta name="description" content="'+H.escape(desc)+'"',head)
    head=head.replace('</head>','<link rel="canonical" href="https://mebelinside.ru'+p['url']+'">\n'+css_add+'</head>')
    # relative assets -> absolute
    head=head.replace('href="favicon.png"','href="/b2b/favicon.png"').replace('href="favicon-180.png"','href="/b2b/favicon-180.png"')
    header=tpl[tpl.find('<header class="site">'):tpl.find('</header>')+9]
    cta=tpl[tpl.find('<section class="cta-final">'):tpl.find('</section>',tpl.find('<section class="cta-final">'))+10].replace('<section class="cta-final">','<section class="cta-final" id="miTz">',1)
    footer=tpl[tpl.find('<footer class="site">'):tpl.find('</footer>')+9]
    hero='<section class="hero"><div class="wrap"><span class="eyebrow">Для бизнеса · '+want[p['url']]+'</span><h1>'+H.escape(p['h1'],quote=False)+'</h1><p class="lead">Свой цех в Пятигорске с 2009 года. Проектируем, изготавливаем и монтируем по вашим чертежам и ТЗ. Образцы материалов — до запуска в производство.</p></div></section>'
    page=head+'<body>\n'+header+'\n'+hero+'\n<section class="prose-sec"><div class="wrap"><div class="prose">\n'+body+'\n</div></div></section>\n'+cta+'\n'+footer+'\n'+('\n'+ld if '<script' in ld else '')+'\n<script src="/mi-chrome.js?v=2" defer></script>\n</body>\n</html>\n'
    page=re.sub(r'[\U00010000-\U0010ffff]','',page)
    slug=p['url'].strip('/').split('/')[-1]
    os.makedirs('_gen/b2b-out/'+slug,exist_ok=True)
    open('_gen/b2b-out/'+slug+'/index.html','w',encoding='utf-8',newline='').write(page)
    report.append((slug,len(page),dead,body.count('[?]')))
for r in report: print(r)
