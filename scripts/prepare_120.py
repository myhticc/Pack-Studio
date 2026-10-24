import pathlib,json,urllib.request as u,concurrent.futures as cf,importlib.util,os,zipfile
R=pathlib.Path(__file__).resolve().parents[1];OLD=R.parent/'MCPVP Essentials'
spec=importlib.util.spec_from_file_location('runtime_tools',OLD/'.research/runtime_tests.py');rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
run=R/'build/game-prepared/1.20';run.mkdir(parents=True,exist_ok=True);(run/'mods').mkdir(exist_ok=True);(run/'natives').mkdir(exist_ok=True)
m=json.loads((R/'.tools/metadata/1.20.json').read_text())['manifest'];profile=json.load(u.urlopen('https://meta.fabricmc.net/v2/versions/loader/1.20/0.19.5/profile/json'))
def lib(x):
 a=x.get('downloads',{}).get('artifact',{});rel=a.get('path',rt.maven_path(x['name']));url=a.get('url',x.get('url','https://libraries.minecraft.net/').rstrip('/')+'/'+rel)
 return rt.obtain(url,rt.CACHE/'libraries'/rel,a.get('sha1'),a.get('size'),[rt.MODRINTH/'libraries'/rel])
libs=[x for x in m['libraries']+profile['libraries'] if rt.allowed(x) and not any(k in x['name'] for k in ['natives-linux','natives-macos','natives-windows-arm64','natives-windows-x86'])]
with cf.ThreadPoolExecutor(12) as pool:cp=list(pool.map(lib,libs))
c=m['downloads']['client'];cp.append(rt.obtain(c['url'],rt.CACHE/'versions/1.20/client.jar',c['sha1'],c['size']))
a=m['assetIndex'];index=rt.obtain(a['url'],rt.CACHE/'assets/indexes'/(a['id']+'.json'),a['sha1'],a['size'],[rt.MODRINTH/'assets/indexes'/(a['id']+'.json')]);objects=json.loads(index.read_text())['objects'];unique={x['hash']:x['size'] for x in objects.values()}
print('Minecraft 1.20 assets:',len(unique),flush=True)
def asset(kv):
 h,size=kv;rel=h[:2]+'/'+h
 return rt.obtain('https://resources.download.minecraft.net/'+rel,rt.CACHE/'assets/objects'/rel,h,size,[rt.MODRINTH/'assets/objects'/rel,rt.LOOM/'assets/objects'/rel])
with cf.ThreadPoolExecutor(20) as pool:list(pool.map(asset,unique.items()))
url='https://api.modrinth.com/v2/project/fabric-api/version?game_versions=%5B%221.20%22%5D&loaders=%5B%22fabric%22%5D';rows=json.load(u.urlopen(url));f=next(x for x in rows[0]['files'] if x['primary']);rt.obtain(f['url'],run/'mods'/f['filename'],f['hashes']['sha1'],f['size'])
java=next((OLD/'.tools/java').glob('jdk-*'))/'bin/java.exe';args=['-Xms256M','-Xmx1536M','-Dfile.encoding=UTF-8','-Djava.library.path='+str(run/'natives'),'-Djna.tmpdir='+str(run/'natives'),'-Dorg.lwjgl.system.SharedLibraryExtractPath='+str(run/'natives'),'-cp',os.pathsep.join(map(str,cp))]+profile.get('arguments',{}).get('jvm',[])+[profile['mainClass'],'--username','PackStudio_Test','--version','1.20','--gameDir',str(run),'--assetsDir',str(rt.CACHE/'assets'),'--assetIndex',a['id'],'--uuid','00000000000000000000000000000001','--accessToken','0','--userType','legacy','--versionType','release','--width','1000','--height','650']
(run/'launch.args').write_text('\n'.join(json.dumps(x.replace('\\','/')) for x in args));(run/'launch.json').write_text(json.dumps({'java':str(java)}));print('Minecraft 1.20 runtime prepared',flush=True)
