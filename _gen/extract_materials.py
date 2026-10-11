import re,json,sys
def parse(path):
    s=open(path,encoding='utf-8').read()
    secs=re.split(r'(?m)^# (?=\d+[а-я]?\. )',s)[1:]
    out=[]
    for sec in secs:
        head=sec.split('\n',1)[0]
        m=re.search(r'`(/[^`]+\.html)`',head)
        if not m or 'создать' not in head: continue
        url=m.group(1)
        t=re.search(r'\*\*Title:\*\*\s*(.+)',sec); d=re.search(r'\*\*Description:\*\*\s*(.+)',sec); h=re.search(r'\*\*H1:\*\*\s*(.+)',sec)
        blocks=re.findall(r'```html\n(.*?)```',sec,flags=re.S)
        out.append(dict(url=url,title=t.group(1).strip() if t else None,desc=d.group(1).strip() if d else None,h1=h.group(1).strip() if h else None,blocks=blocks))
    return out
if __name__=='__main__':
    allp=[]
    for p in ['MATERIALY-stranitsy-teksty.md','MATERIALY-2-stranitsy-teksty.md']:
        allp+=parse(p)
    for x in allp:
        body='\n'.join(x['blocks'])
        links=sorted(set(re.findall(r'href="([^"]+)"',body)))
        print(x['url'],'| blocks',len(x['blocks']),'| len',len(body),'| scripts',body.count('<script'),'| emoji',bool(re.search('[\U00010000-\U0010ffff]',body)),'| [?]',body.count('[?]'),'| title',len(x['title'] or ''),'| desc',len(x['desc'] or ''),'| h1',x['h1'])
    json.dump(allp,open('_gen/materials.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
