"""Накладывает логотип (только буквы) на фартук 3D-Инсайда как печать на ткани. python tools/mascot_logo_on_apron.py"""
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np
K=2
base=Image.open('media/mascot/3d/insaid-3D-1-s-rulenkoy-preview.png').convert('RGB').resize((800*K,800*K),Image.LANCZOS)
a=np.array(base).astype(int);bg=a[5:30,5:30].reshape(-1,3).mean(0)
m=Image.fromarray(((np.abs(a-bg).sum(2)<42)*255).astype('uint8'))
for pt in ((0,0),(m.width-1,0),(0,m.height-1),(m.width-1,m.height-1)):
    if m.getpixel(pt)==255: ImageDraw.floodfill(m,pt,128)
fg=Image.fromarray(((np.array(m)!=128)*255).astype('uint8')).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
alpha=fg.filter(ImageFilter.GaussianBlur(1.4))
B=np.array(base).astype(float)
lum=B.mean(2)
def blur(arr,r):
    n=int(r*3)+1;x=np.arange(-n,n+1);k=np.exp(-x**2/(2*r*r));k/=k.sum()
    o=np.pad(arr.astype('float32'),n,mode='edge')
    o=np.apply_along_axis(lambda v:np.convolve(v,k,'valid'),0,o)
    return np.apply_along_axis(lambda v:np.convolve(v,k,'valid'),1,o)
Lsoft=blur(lum,5);Lmean=blur(lum,40)
grain=lum-blur(lum,2.0)                    # зерно/шум рендера
gy,gx=np.gradient(Lsoft)
# буквы логотипа
lg=np.array(Image.open('media/brand/logo-mebel-inside.jpg').convert('RGB')).astype(int)
crop=lg[345:675,120:905]
r,g,b=crop[...,0],crop[...,1],crop[...,2]
white=(np.minimum(np.minimum(r,g),b)>150)
green=(g>r+45)&(g>90)
txt=np.zeros(crop.shape[:2]+(4,),float)
txt[white]=(238,238,232,255);txt[green]=(8,140,108,255)
tl=Image.fromarray(txt.astype('uint8'),'RGBA')
def font(sz):
    f=ImageFont.truetype('tools/fonts/Manrope-Variable.ttf',sz)
    try:f.set_variation_by_axes([800])
    except Exception:pass
    return f
def build(wid,cx,cy,url,out):
    t=tl.resize((int(wid*K),int(wid*K*tl.height/tl.width)),Image.LANCZOS)
    L=Image.new('RGBA',(800*K,800*K),(0,0,0,0));L.alpha_composite(t,(int(cx*K-t.width/2),int(cy*K-t.height/2)))
    if url:
        f=font(int(15*K));s='mebelinside.ru';dd=ImageDraw.Draw(L);tw=dd.textlength(s,font=f)
        dd.text((cx*K-tw/2,(cy+wid*0.21+14)*K),s,font=f,fill=(238,238,232,255))
    L=L.rotate(3,resample=Image.BICUBIC,center=(cx*K,cy*K))
    la=np.array(L).astype(float)
    # смещение по складкам фартука
    k=0.35
    ys,xs=np.mgrid[0:800*K,0:800*K]
    cl=lambda v:np.clip(v*k,-3*K,3*K)
    sx=np.clip((xs+cl(gx)).round().astype(int),0,800*K-1);sy=np.clip((ys+cl(gy)).round().astype(int),0,800*K-1)
    la=la[sy,sx]
    # мягкая печать: лёгкий блюр под резкость рендера
    A=blur(la[...,3],1.6)/255;col=[blur(la[...,i],1.6) for i in range(3)]
    shade=np.clip(lum/np.maximum(Lmean,1),0.45,1.25)**1.3   # складки/блики ткани
    shade=blur(shade,1.2)
    n=1+grain/60
    res=B.copy()
    for i in range(3):
        c=col[i]*shade*n
        res[...,i]=B[...,i]*(1-A*0.94)+c*A*0.94
    res=np.clip(res,0,255).astype('uint8')
    im=Image.fromarray(res).convert('RGBA');im.putalpha(alpha)
    im.save(out)
    bgc=Image.new('RGBA',im.size,(241,235,221,255));bgc.alpha_composite(im);bgc=bgc.convert('RGB')
    bgc.resize((1000,1000),Image.LANCZOS).save(out.replace('.png','-preview.png'))
    bgc.crop((520,700,1000,1260)).save(out.replace('.png','-krop-apron.png'))
p='media/mascot/3d/final2/'
build(150,378,508,False,p+'insaid-3D-final2-logo-krupno.png')
build(135,378,492,True,p+'insaid-3D-final2-logo-url.png')
a=Image.open(p+'insaid-3D-final2-logo-krupno-preview.png');b=Image.open(p+'insaid-3D-final2-logo-url-preview.png')
W=Image.new('RGB',(2040,1020),(241,235,221));W.paste(a,(10,10));W.paste(b,(1030,10));W.save(p+'collage-final2.png')
