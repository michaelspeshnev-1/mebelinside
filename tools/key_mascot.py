"""Вырезает кремовый фон у insaid-3D-final3.png (заливка от краёв) -> *-alpha.png"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops
src = Path(__file__).resolve().parent.parent / "media/mascot/3d/final3/insaid-3D-final3.png"
im = Image.open(src).convert("RGB"); bg = im.getpixel((5, 5))
diff = ImageChops.difference(im, Image.new("RGB", im.size, bg)).convert("L").point(lambda v: 255 if v > 22 else 0)
# 255 = объект; заливаем фон (0) от краёв значением 128
for pt in [(0, 0), (im.width - 1, 0), (0, im.height - 1), (im.width - 1, im.height - 1), (im.width // 2, 0)]:
    if diff.getpixel(pt) == 0: ImageDraw.floodfill(diff, pt, 128)
alpha = diff.point(lambda v: 0 if v == 128 else 255)
px = im.load(); ap = alpha.load()
for y in range(1400, im.height):  # светлая тень у ног — убрать; ботинки тёмные
    for x in range(im.width):
        if sum(px[x, y]) > 330: ap[x, y] = 0
alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
out = im.convert("RGBA"); out.putalpha(alpha)
out.save(src.with_name("insaid-3D-final3-alpha.png")); print(out.getchannel("A").getbbox())
