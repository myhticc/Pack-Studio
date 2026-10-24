import pathlib,urllib.request as u,json,re,zipfile,io,hashlib,html,concurrent.futures as cf
from PIL import Image,ImageDraw
R=pathlib.Path(__file__).resolve().parents[1];D=R/'.tools/art';D.mkdir(parents=True,exist_ok=True)
def get(url):
 p=D/(hashlib.sha256(url.encode()).hexdigest()[:12]+'-'+url.split('/')[-1])
 if not p.exists():p.write_bytes(u.urlopen(url,timeout=120).read())
 return p
pages=['16x16-weapon-rpg-icons','cc0-headgear-icons','cc0-torso-wear-icons','cc0-leggings-icons','cc0-footgear-icons']
def download(p):
 s=u.urlopen('https://opengameart.org/content/'+p).read().decode()
 urls=list(dict.fromkeys(re.findall(r'https://opengameart.org/sites/default/files/[^"<> ]+\.zip',s)))
 if p.startswith('16x16'):urls=urls[:1]
 else:urls=[x for x in urls if any(k in x for k in ['7soul','dcss','ettingrinder','scratchio'])]
 out=[]
 for url in urls:
  f=get(html.unescape(url));print(p,f.name,flush=True);out.append((str(f),url))
 return p,out
if __name__=='__main__':
 with cf.ThreadPoolExecutor(5) as pool:result=dict(pool.map(download,pages))
 (D/'sources.json').write_text(json.dumps(result,indent=2))
 for p,zips in result.items():
  for f,url in zips:
   with zipfile.ZipFile(f) as z:
    names=[n for n in z.namelist() if n.lower().endswith('.png')]
    print(p,len(names),[(n,Image.open(io.BytesIO(z.read(n))).size) for n in names[:8]],flush=True)
