import pathlib,json,zipfile,io,hashlib,shutil,random
from PIL import Image,ImageDraw,ImageEnhance
R=pathlib.Path(__file__).resolve().parents[1];D=R/'ui/library';D.mkdir(exist_ok=True)
sources=json.loads((R/'.tools/art/sources.json').read_text());items=[];credits=[];seen=set()
def add(im,name,category,source,author,style='RPG/Fantasy',kind='icon',**extra):
 im=im.convert('RGBA');h=hashlib.sha256(im.tobytes()+str(im.size).encode()).hexdigest()
 if h in seen:return
 seen.add(h);ident=f'{len(items):04d}';im.save(D/(ident+'.png'))
 items.append(dict(id=ident,name=name,category=category,file='library/'+ident+'.png',width=im.width,height=im.height,source=source,author=author,license='CC0-1.0',style=style,kind=kind,**extra))
for page,archives in sources.items():
 url='https://opengameart.org/content/'+page
 for f,download in archives:
  with zipfile.ZipFile(f) as z:
   author='Shade' if page.startswith('16x16') else next((a for k,a in [('7soul','7Soul1 / Henrique Lazarini'),('dcss','Dungeon Crawl Stone Soup contributors'),('ettingrinder','ETTiNGRiNDER'),('scratchio','ScratchIO')] if k in f),'AntumDeluge and credited original artists')
   credits.append(dict(source=url,download=download,author=author,license='CC0-1.0'))
   for n in z.namelist():
    if not n.lower().endswith('.png'):continue
    im=Image.open(io.BytesIO(z.read(n))).convert('RGBA')
    if page.startswith('16x16'):
     if 'preview' in n:continue
     metal=pathlib.Path(n).stem.split('-')[0].title()
     for y in range(10):
      for x in range(12):
       if metal!='Iron' and y>=3:continue
       tile=im.crop((x*16,y*16,x*16+16,y*16+16))
       add(tile,f'{metal} {['Rapier','Katana','Sword','Greatsword'][x//3]} {y*3+x%3+1:02}', 'sword',url,author)
       if metal=='Iron' and x in [0,3,6,9] and y<3:
        for part in ['Blade','Guard','Grip']:
         component=tile.copy()
         for py in range(16):
          for px in range(16):
           keep=(px+py<20) if part=='Blade' else (20<=px+py<24) if part=='Guard' else (px+py>=24)
           if not keep:component.putpixel((px,py),(0,0,0,0))
         if component.getbbox():add(component,f'{part} {x//3*3+y+1:02}','parts',url,author,kind='part',part=part)
    elif n.startswith('32x32/'):
     cat={'cc0-headgear-icons':'helmet','cc0-torso-wear-icons':'chestplate','cc0-leggings-icons':'leggings','cc0-footgear-icons':'boots'}[page]
     name=pathlib.Path(n).stem.replace('_',' ').title()
     add(im,name,cat,url,author)
   for n in z.namelist():
    if n.lower().endswith(('.txt','.md')):
     dest=D/'licenses';dest.mkdir(exist_ok=True)
     (dest/(hashlib.sha1((f+n).encode()).hexdigest()[:8]+'-'+pathlib.Path(n).name)).write_bytes(z.read(n))
palettes=[('Obsidian','#2b2942','#ae8bff'),('Glacier','#387a91','#b5f3fa'),('Crimson','#752b42','#ff877e'),('Emerald','#235e52','#8ee0aa'),('Royal','#343c83','#b1bbff'),('Sunforge','#82522d','#ffe4a1'),('Ash','#414957','#ced6df'),('Rose','#894763','#ffb9d4'),('Copper','#805441','#e8aa78'),('Ocean','#23465e','#6ed7ef'),('Moss','#4b6234','#c7d789'),('Ivory','#89877c','#fff5d3')]
def rgb(s):return tuple(bytes.fromhex(s[1:]))
def armor(base,accent,layer,pattern):
 im=Image.new('RGBA',(64,32));d=ImageDraw.Draw(im);b=rgb(base);a=rgb(accent)
 def box(u,v,w,h,depth):
  faces=[(u+depth,v,w,depth),(u+depth+w,v,w,depth),(u,v+depth,depth,h),(u+depth,v+depth,w,h),(u+depth+w,v+depth,depth,h),(u+2*depth+w,v+depth,w,h)]
  for k,(x,y,fw,fh) in enumerate(faces):
   c=tuple(min(255,int(t*(.72+.065*k))) for t in b)
   d.rectangle((x,y,x+fw-1,y+fh-1),fill=(*c,255))
   d.line((x,y,x+fw-1,y),fill=(*a,255));d.line((x,y+fh-1,x+fw-1,y+fh-1),fill=(*a,255))
   if pattern%3==0:d.line((x+fw//2,y,x+fw//2,y+fh-1),fill=(*a,255))
   if pattern%3==1:
    for yy in range(y+2,y+fh-1,3):d.line((x,yy,x+fw-1,yy),fill=(*a,255))
   if pattern%3==2 and fw>3 and fh>3:d.rectangle((x+1,y+1,x+fw-2,y+fh-2),outline=(*a,255))
 if layer==1:
  box(0,0,8,8,8);box(16,16,8,12,4);box(40,16,4,12,4);box(0,16,4,12,4)
  d.rectangle((0,16,15,25),fill=(0,0,0,0))
 else:box(16,16,8,12,4);box(0,16,4,12,4)
 return im
def gear_icon(category,b,a):
 im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im);base=rgb(b);accent=rgb(a);edge=tuple(int(x*.45) for x in base)
 if category=='helmet':
  d.rectangle((2,2,13,10),fill=(*base,255),outline=(*edge,255));d.rectangle((4,6,11,11),fill=(0,0,0,0));d.line((3,3,12,3),fill=(*accent,255));d.line((2,4,2,10),fill=(*accent,255))
 elif category=='chestplate':
  d.polygon([(2,3),(5,3),(6,5),(9,5),(10,3),(13,3),(15,8),(12,10),(11,8),(11,14),(4,14),(4,8),(3,10),(0,8)],fill=(*base,255),outline=(*edge,255));d.line((4,6,4,13),fill=(*accent,255));d.line((5,13,11,13),fill=(*accent,255));d.line((1,7,3,4),fill=(*accent,255))
 elif category=='leggings':
  d.rectangle((3,2,12,6),fill=(*base,255),outline=(*edge,255));d.rectangle((3,6,6,14),fill=(*base,255),outline=(*edge,255));d.rectangle((9,6,12,14),fill=(*base,255),outline=(*edge,255));d.line((4,3,11,3),fill=(*accent,255));d.line((4,7,4,13),fill=(*accent,255));d.line((10,7,10,13),fill=(*accent,255))
 else:
  for x in [2,9]:
   d.rectangle((x,5,x+3,12),fill=(*base,255),outline=(*edge,255));d.rectangle((x-1,11,x+4,14),fill=(*base,255),outline=(*edge,255));d.line((x,6,x+2,6),fill=(*accent,255));d.line((x,13,x+3,13),fill=(*accent,255))
 return im
for i,(name,b,a) in enumerate(palettes):
 for cat in ['helmet','chestplate','leggings','boots']:add(gear_icon(cat,b,a),name+' '+cat.title(),cat,'Pack Studio original pixel art','Pack Studio','Minecraft/PvP')
 for layer in [1,2]:add(armor(b,a,layer,i),f'{name} Armor — {'Body' if layer==1 else 'Leggings'}','armor','Pack Studio original templates','Pack Studio','Minecraft/PvP',kind='armor',armorLayer=layer,set=name)
 # Deliberately drawn 16px short swords, different palettes and blade silhouettes.
 im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im)
 for step in range(3,12):
  x=step;y=15-step;thickness=1+(i%3)
  d.line((x,y,x+thickness,y+thickness),fill=(*rgb(b),255));d.point((x,y),fill=(*rgb(a),255))
 d.line((2,11,5,14),fill=(*rgb(a),255),width=2);d.line((1,14,3,12),fill=(105,74,56,255),width=2)
 add(im,name+' Short Sword','sword','Pack Studio original pixel art','Pack Studio','Minecraft/PvP')
 for pattern in ['Tiles','Bricks']:
  im=Image.new('RGBA',(16,16),(*rgb(b),255));d=ImageDraw.Draw(im)
  for y in range(0,16,4):
   d.line((0,y,15,y),fill=(*rgb(a),255))
   for x in range((y//4%2)*4 if pattern=='Bricks' else 0,16,8):d.line((x,y,x,y+3),fill=(*rgb(a),255))
  add(im,name+' '+pattern,'block','Pack Studio original pixel art','Pack Studio','Minecraft/PvP')
(R/'ui/library.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'ui/credits.json').write_text(json.dumps(credits,indent=2))
print('Library:',len(items),'assets; categories:',{c:sum(i['category']==c for i in items) for c in sorted({i['category'] for i in items})})
