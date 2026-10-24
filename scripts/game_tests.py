import pathlib,json,subprocess,shutil,zipfile,os,concurrent.futures as cf,time
R=pathlib.Path(__file__).resolve().parents[1];OLD=R.parent/'MCPVP Essentials';BASE=R/'build/game-tests';BASE.mkdir(exist_ok=True)
JAVA=next((OLD/'.tools/java').glob('jdk-*'))/'bin';CACHE=OLD/'.research/runtime-cache';HARNESS=OLD/'.research/runtime-harness'
def compile():
 classes=BASE/'classes';classes.mkdir(exist_ok=True)
 cp=os.pathsep.join([str(next((CACHE/'libraries/net/fabricmc/fabric-loader').rglob('*.jar'))),str(next((CACHE/'libraries/net/fabricmc/sponge-mixin').rglob('*.jar')))])
 subprocess.run([str(JAVA/'javac.exe'),'--release','21','-proc:none','-cp',cp,'-d',str(classes),str(R/'tests/PackSmoke.java')],check=True)
 for variant,name in [('legacy','HiddenLegacyWindow'),('modern','HiddenModernWindow'),('sdl','HiddenSdlWindow')]:
  with zipfile.ZipFile(BASE/(variant+'.jar'),'w',zipfile.ZIP_DEFLATED) as z:
   for f in classes.rglob('*.class'):z.write(f,f.relative_to(classes).as_posix())
   for f in (HARNESS/'classes/local/smoke/mixin').glob('*.class'):z.write(f,'local/smoke/mixin/'+f.name)
   z.writestr('fabric.mod.json',json.dumps({'schemaVersion':1,'id':'packstudio_test','version':'1.0','environment':'client','entrypoints':{'client':['packstudio.test.PackSmoke']},'mixins':['packstudio.mixins.json']}))
   z.writestr('packstudio.mixins.json',json.dumps({'required':True,'package':'local.smoke.mixin','compatibilityLevel':'JAVA_21','client':[name],'injectors':{'defaultRequire':1}}))
def run(v):
 old=OLD/'.research/runtime-tests'/v;old=old if old.exists() else R/'build/game-prepared'/v;run=BASE/v;run.mkdir(exist_ok=True);(run/'mods').mkdir(exist_ok=True);(run/'resourcepacks').mkdir(exist_ok=True)
 conf=json.loads((old/'launch.json').read_text());args=[json.loads(l) for l in (old/'launch.args').read_text().splitlines() if l.strip()]
 for i,a in enumerate(args):
  if str(old).replace('\\','/') in a:args[i]=a.replace(str(old).replace('\\','/'),str(run).replace('\\','/'))
 args[args.index('--username')+1]='PackStudio_Test'
 (run/'natives').mkdir(exist_ok=True)
 for f in (old/'mods').glob('fabric-api*.jar'):shutil.copy2(f,run/'mods'/f.name)
 variant='sdl' if v=='26.3' else 'modern' if v.startswith('26.') else 'legacy';shutil.copy2(BASE/(variant+'.jar'),run/'mods/packstudio-test.jar')
 fixture=R/'build/fixtures'/(v+'.zip');shutil.copy2(fixture,run/'resourcepacks/packstudio-test.zip')
 with zipfile.ZipFile(fixture) as z:(run/'expected-sword.png').write_bytes(z.read('assets/minecraft/textures/item/diamond_sword.png'))
 (run/'options.txt').write_text('version:0\nlang:en_us\nfullscreen:false\nmaxFps:30\nguiScale:2\nrenderDistance:2\nsimulationDistance:5\nsoundCategory_master:0.0\nonboardAccessibility:false\njoinedFirstServer:true\nstartedCleanly:true\nresourcePacks:["vanilla","file/packstudio-test.zip"]\n',encoding='utf-8')
 argfile=run/'launch.args';argfile.write_text('\n'.join(json.dumps(a.replace('\\','/')) for a in args),encoding='utf-8')
 start=time.monotonic();print('Real Minecraft pack test:',v,flush=True)
 with (run/'console.log').open('w',encoding='utf-8') as log:
  p=subprocess.Popen([conf['java'],'-Dfabric.noGui=true','-Dpack.version='+v,'@'+str(argfile)],cwd=run,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:code=p.wait(timeout=240)
  except subprocess.TimeoutExpired:p.kill();p.wait();code=-1
 result=(run/'pack-result.txt').read_text() if (run/'pack-result.txt').exists() else ''
 out={'version':v,'ok':code==0 and result.startswith('PASS'),'exit':code,'seconds':round(time.monotonic()-start,1),'report':result}
 print(out,flush=True)
 return out
if __name__=='__main__':
 compile()
 versions=__import__('sys').argv[1:] or ['1.21.2','1.21.9','1.21.11','26.3']
 results=[]
 for v in versions:
  try:results.append(run(v))
  except Exception as e:results.append({'version':v,'ok':False,'error':str(e)});print(v,e,flush=True)
  (BASE/'results.json').write_text(json.dumps(results,indent=2))

