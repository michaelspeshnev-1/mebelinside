import re,sys,json,urllib.request
urls=sys.argv[1:]
for u in urls:
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    h=urllib.request.urlopen(req,timeout=60).read().decode('utf8','replace')
    print('=====',u,len(h))
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>',h,re.S):
        t=m.group(1).strip()
        try: j=json.loads(t)
        except Exception as e: print('BAD JSON',e); print(t[:300]); continue
        typ=j.get('@type') if isinstance(j,dict) else 'list'
        print('@type',typ,len(t))
        s=json.dumps(j,ensure_ascii=False)
        for k in ('opens','closes','dayOfWeek'):
            for mm in re.finditer(r'"%s": ?("[^"]*"|\[[^\]]*\])'%k,s): print('  ',k,mm.group(1))
        if typ=='FAQPage':
            for q in j.get('mainEntity',[]):
                print('  Q:',q['name']); print('  A:',re.sub('<[^>]+>','',q['acceptedAnswer']['text'])[:400])
