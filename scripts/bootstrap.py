import concurrent.futures as cf, urllib.request as u, json, zipfile, re, pathlib, subprocess, shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
TOOLS=ROOT/'.tools'; TOOLS.mkdir(exist_ok=True)
for d in ['vendor','ui/vendor','ui/library','src','build','dist','tests']:(ROOT/d).mkdir(parents=True,exist_ok=True)
def get(url,path):
    path=pathlib.Path(path)
    if not path.exists():
        print('Downloading',path.name,flush=True)
        with u.urlopen(u.Request(url,headers={'User-Agent':'PackStudio-build/1.0'}),timeout=180) as r,open(str(path)+'.part','wb') as f:shutil.copyfileobj(r,f)
        pathlib.Path(str(path)+'.part').replace(path)
    return path
def compiler():
    d=json.load(u.urlopen('https://api.github.com/repos/mstorsjo/llvm-mingw/releases/latest'))
    a=next(a for a in d['assets'] if 'ucrt-x86_64.zip' in a['name'])
    p=get(a['browser_download_url'],TOOLS/a['name'])
    dest=TOOLS/p.stem
    if not dest.exists():zipfile.ZipFile(p).extractall(TOOLS)
    return str(dest)
def runtime():
    s=u.urlopen('https://developer.microsoft.com/en-us/microsoft-edge/webview2/').read().decode()
    url=next(x for x in re.findall(r'https[^<>\s\x22]+\.x64\.cab',s)).replace('\\u002F','/')
    p=get(url,TOOLS/'runtime.cab');dest=TOOLS/'runtime';dest.mkdir(exist_ok=True)
    if not list(dest.glob('*/msedgewebview2.exe')):
        subprocess.run(['expand.exe','-F:*',str(p),str(dest)],check=True,stdout=subprocess.DEVNULL)
    return str(next(dest.glob('*/msedgewebview2.exe')).parent)
def sdk():
    vs=json.load(u.urlopen('https://api.nuget.org/v3-flatcontainer/microsoft.web.webview2/index.json'))['versions']
    v=next(v for v in reversed(vs) if '-' not in v)
    p=get(f'https://api.nuget.org/v3-flatcontainer/microsoft.web.webview2/{v}/microsoft.web.webview2.{v}.nupkg',TOOLS/'webview2.zip')
    with zipfile.ZipFile(p) as z:
        for name,target in [('build/native/include/WebView2.h',ROOT/'vendor/WebView2.h'),('build/native/x64/WebView2Loader.dll',ROOT/'ui/WebView2Loader.dll')]:target.write_bytes(z.read(name))
    header=(ROOT/'vendor/WebView2.h').read_text()
    decl=[]
    for guid,name in re.findall(r'MIDL_INTERFACE\("([a-fA-F0-9-]+)"\)\s*(\w+)',header):
        if name in ['ICoreWebView2CreateCoreWebView2ControllerCompletedHandler','ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler','ICoreWebView2_3','ICoreWebView2WebMessageReceivedEventHandler','ICoreWebView2CapturePreviewCompletedHandler','ICoreWebView2NavigationStartingEventHandler','ICoreWebView2NavigationCompletedEventHandler']:
            values=[guid[:8],guid[9:13],guid[14:18]]+re.findall('..',guid[19:].replace('-',''))
            decl.append('__CRT_UUID_DECL('+name+','+','.join('0x'+x for x in values)+')')
    (ROOT/'vendor/webview_guids.hpp').write_text('\n'.join(decl))
    return v
def libs():
    for name in ['miniz.c','miniz.h','miniz_common.h','miniz_tdef.c','miniz_tdef.h','miniz_tinfl.c','miniz_tinfl.h','miniz_zip.c','miniz_zip.h']:
        get('https://raw.githubusercontent.com/richgel999/miniz/2.2.0/'+name,ROOT/'vendor'/name)
    (ROOT/'vendor/miniz_export.h').write_text('#define MINIZ_EXPORT\n')
    get('https://raw.githubusercontent.com/nlohmann/json/v3.12.0/single_include/nlohmann/json.hpp',ROOT/'vendor/json.hpp')
    get('https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js',ROOT/'ui/vendor/three.module.js')
    get('https://raw.githubusercontent.com/mrdoob/three.js/r170/LICENSE',ROOT/'ui/vendor/THREE-LICENSE.txt')
    get('https://raw.githubusercontent.com/nlohmann/json/v3.12.0/LICENSE.MIT',ROOT/'vendor/JSON-LICENSE.txt')
    get('https://raw.githubusercontent.com/richgel999/miniz/2.2.0/LICENSE',ROOT/'vendor/MINIZ-LICENSE.txt')
    return 'ok'
if __name__=='__main__':
    with cf.ThreadPoolExecutor(4) as pool:
        futures={pool.submit(f):n for n,f in [('compiler',compiler),('runtime',runtime),('sdk',sdk),('libs',libs)]}
        results={}
        for f in cf.as_completed(futures):
            n=futures[f]
            try:results[n]=f.result();print(n,results[n],flush=True)
            except Exception as e:print(n,'ERROR',repr(e),flush=True);raise
    (TOOLS/'paths.json').write_text(json.dumps(results,indent=2))
