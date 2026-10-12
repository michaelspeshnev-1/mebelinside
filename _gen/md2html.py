import re,html
def inline(s):
    s=html.escape(s,quote=False)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+|/[^)]*|#[^)]*)\)',r'<a href="\2">\1</a>',s)
    s=re.sub(r'`([^`]+)`',r'\1',s)
    return s
def convert(md, skip_h=(), stop_h=()):
    lines=md.split('\n'); out=[]; i=0; para=[]; lst=[]; skipping=False
    def flush_p():
        nonlocal para
        if para: out.append('<p>'+inline(' '.join(para))+'</p>'); para=[]
    def flush_l():
        nonlocal lst
        if lst: out.append('<ul>'+''.join('<li>'+inline(x)+'</li>' for x in lst)+'</ul>'); lst=[]
    while i<len(lines):
        l=lines[i]
        m=re.match(r'^(#{2,6})\s+(.*)',l)
        if m:
            flush_p(); flush_l()
            t=m.group(2).strip()
            skipping=any(t.startswith(s) for s in skip_h)
            if any(t.startswith(s) for s in stop_h): break
            if not skipping: out.append('<h2>'+inline(t)+'</h2>')
            i+=1; continue
        if skipping: i+=1; continue
        if '[?]' in l:
            # drop the line and its indented continuation
            i+=1
            while i<len(lines) and lines[i].startswith('  ') and lines[i].strip(): i+=1
            continue
        if l.startswith('|'):
            flush_p(); flush_l()
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                rows.append(lines[i]); i+=1
            cells=[[c.strip() for c in r.strip().strip('|').split('|')] for r in rows if not re.match(r'^\|\s*:?-',r)]
            t='<table>'
            for k,r in enumerate(cells):
                tag='th' if (k==0 and any(r)) and False else 'td'
                if k==0 and not any(r): continue
                t+='<tr>'+''.join('<%s>%s</%s>'%(tag,inline(c),tag) for c in r)+'</tr>'
            out.append(t+'</table>'); continue
        if re.match(r'^\s*[-*]\s+',l):
            flush_p(); lst.append(re.sub(r'^\s*[-*]\s+','',l)); i+=1; continue
        if re.match(r'^\s*\d+\.\s+',l):
            flush_p(); lst.append(re.sub(r'^\s*\d+\.\s+','',l)); i+=1; continue
        if l.startswith('>'):
            flush_p(); flush_l(); out.append('<blockquote>'+inline(l.lstrip('> ').strip())+'</blockquote>'); i+=1; continue
        if not l.strip(): flush_p(); flush_l(); i+=1; continue
        if lst and l.startswith('  '): lst[-1]+=' '+l.strip(); i+=1; continue
        para.append(l.strip()); i+=1
    flush_p(); flush_l()
    return '\n'.join(out)
