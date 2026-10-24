import urllib.request as u,json,io,zipfile,pathlib,concurrent.futures as cf
R=pathlib.Path(__file__).resolve().parents[1];CACHE=R/'.tools/metadata';CACHE.mkdir(parents=True,exist_ok=True)
VERSIONS='1.20 1.20.1 1.20.2 1.20.3 1.20.4 1.20.5 1.20.6 1.21 1.21.1 1.21.2 1.21.3 1.21.4 1.21.5 1.21.6 1.21.7 1.21.8 1.21.9 1.21.10 1.21.11 26.1 26.1.1 26.1.2 26.2 26.3'.split()
class Remote(io.RawIOBase):
 def __init__(self,url,size):self.url=url;self.size=size;self.pos=0;self.cache=[]
 def seekable(self):return True
 def seek(self,o,w=0):self.pos=o if w==0 else self.pos+o if w==1 else self.size+o;return self.pos
 def tell(self):return self.pos
 def read(self,n=-1):
  n=self.size-self.pos if n<0 else min(n,self.size-self.pos)
  if n<=0:return b''
  for start,data in self.cache:
   if start<=self.pos and self.pos+n<=start+len(data):out=data[self.pos-start:self.pos-start+n];self.pos+=n;return out
  start=self.pos;end=min(self.size,start+max(n,65536))-1
  with u.urlopen(u.Request(self.url,headers={'Range':f'bytes={start}-{end}'}),timeout=120) as r:
   data=r.read();actual=start if r.status==206 else 0
  self.cache.append((actual,data));out=data[start-actual:start-actual+n];self.pos+=len(out);return out
manifest=json.load(u.urlopen('https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'))
def one(v):
 p=CACHE/(v+'.json')
 if p.exists():
  cached=json.loads(p.read_text())
  if "resources" in cached:return cached
 m=json.load(u.urlopen(next(x['url'] for x in manifest['versions'] if x['id']==v)))
 c=m['downloads']['client']
 with zipfile.ZipFile(Remote(c['url'],c['size'])) as z:
  ver=json.loads(z.read('version.json'));pv=ver['pack_version'];pack=pv['resource'] if 'resource' in pv else [pv['resource_major'],pv['resource_minor']]
  resources=sorted(n for n in z.namelist() if n.startswith('assets/') and ((('/textures/' in n) and n.endswith('.png')) or (('/models/' in n or '/items/' in n) and n.endswith('.json'))))
  textures=sorted(n for n in z.namelist() if n.startswith(('assets/minecraft/textures/item/','assets/minecraft/textures/block/')) and n.endswith('.png'))
 result={'id':v,'format':pack,'modernArmor':VERSIONS.index(v)>=VERSIONS.index('1.21.2'),'minorMetadata':VERSIONS.index(v)>=VERSIONS.index('1.21.9'),'client':c,'manifest':m,'textures':textures,'resources':resources}
 p.write_text(json.dumps(result));print(v,pack,len(textures),flush=True);return result
if __name__=='__main__':
 with cf.ThreadPoolExecutor(6) as pool:rows=list(pool.map(one,VERSIONS))
 (R/'ui/versions.json').write_text(json.dumps([{k:v for k,v in row.items() if k not in ['manifest','textures','resources']} for row in rows],indent=2))
 (R/'ui/catalog.json').write_text(json.dumps({row['id']:row['textures'] for row in rows}))


 (R/'ui/resources.json').write_text(json.dumps({row['id']:row['resources'] for row in rows}))
