import re,json,sys
s=open('B2B-teksty.md',encoding='utf-8').read()
secs=re.split(r'(?m)^(?=# \d+\. `/b2b)',s)
out=[]
for sec in secs:
    m=re.match(r'# (\d+)\. `(/b2b/[^`]*)`',sec)
    if not m: continue
    g=lambda k:(re.search(r'\*\*'+k+r'[^*]*\*\*\s*(.+)',sec) or [None,None])[1]
    blocks=re.findall(r'```html\n(.*?)```',sec,flags=re.S)
    out.append(dict(n=m.group(1),url=m.group(2),h1=g('H1'),title=re.sub(r'\s*\(\d+\)\s*$','',g('Title') or ''),desc=re.sub(r'\s*\(\d+\)\s*$','',g('Description') or ''),blocks=blocks))
json.dump(out,open('_gen/b2b.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for o in out: print(o['n'],o['url'],'|',o['h1'],'|',o['title'],'|',len(o['blocks']),[len(b) for b in o['blocks']],'[?]',sum(b.count('[?]') for b in o['blocks']),'script',sum(b.count('<script') for b in o['blocks']))
