import pathlib,json,subprocess,zipfile,struct,hashlib
R=pathlib.Path(__file__).resolve().parents[1];paths=json.loads((R/'.tools/paths.json').read_text());BIN=pathlib.Path(paths['compiler'])/'bin';B=R/'build';B.mkdir(exist_ok=True)
def run(args):subprocess.run([str(x) for x in args],cwd=R,check=True)
for n in ['miniz','miniz_tdef','miniz_tinfl','miniz_zip']:
 src=R/'vendor'/(n+'.c');out=B/(n+'.o')
 if not out.exists() or src.stat().st_mtime>out.stat().st_mtime:run([BIN/'x86_64-w64-mingw32-clang.exe','-O2','-Ivendor','-c',src,'-o',out])
run([BIN/'x86_64-w64-mingw32-windres.exe','-I.','src/app.rc',str(B/'app.res')])
run([BIN/'x86_64-w64-mingw32-clang++.exe','-std=c++20','-O2','-fms-extensions','-D_WIN32_WINNT=0x0A00','-DUNICODE','-D_UNICODE','-Isrc','-Ivendor','src/main.cpp',B/'app.res',*[B/(n+'.o') for n in ['miniz','miniz_tdef','miniz_tinfl','miniz_zip']],'-static','-municode','-mwindows','-lwindowscodecs','-lole32','-loleaut32','-luuid','-lwinhttp','-lcrypt32','-lshell32','-lshlwapi','-lcomdlg32','-ladvapi32','-o',B/'PackStudio-host.exe'])
if '--package' in __import__('sys').argv:
 runtime=pathlib.Path(paths['runtime']);payload=B/'payload.zip'
 with zipfile.ZipFile(payload,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for folder,prefix in [(R/'ui','ui'),(runtime,'runtime')]:
   for f in sorted(folder.rglob('*')):
    if f.is_file():z.write(f,prefix+'/'+f.relative_to(folder).as_posix())
 target=R/'dist/PackStudio.exe';target.parent.mkdir(exist_ok=True)
 with target.open('wb') as out:
  out.write((B/'PackStudio-host.exe').read_bytes())
  with payload.open('rb') as p:__import__('shutil').copyfileobj(p,out)
  out.write(struct.pack('<Q',payload.stat().st_size));out.write(hashlib.sha256(payload.read_bytes()).digest()[:8]);out.write(b'PSPACK01')
 print(target,target.stat().st_size,'bytes',hashlib.sha256(target.read_bytes()).hexdigest())
