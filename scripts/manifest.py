import hashlib,json,subprocess,sys,platform
from pathlib import Path
from importlib.metadata import version
from rdflib import Graph
from rdflib.compare import to_isomorphic
root=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]).resolve()
def git(*args):
    p=subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True)
    return p.stdout.strip() if p.returncode==0 else None
artifacts={}
for p in sorted(out.glob('*')):
    if p.suffix not in ('.owl','.db'):continue
    entry={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    if p.suffix=='.owl':entry['semantic_digest']=str(to_isomorphic(Graph().parse(p)).graph_digest())
    artifacts[p.name]=entry
for required in ('scaudit.owl','scaudit.db','scaudit-demo.owl','scaudit-demo.db'):
    if required not in artifacts:raise RuntimeError('Missing release artifact: '+required)
git_status=git('status','--porcelain')
manifest={'build_mode':'ODK Makefile with official SemSQL builder','source_commit':git('rev-parse','HEAD'),
 'source_dirty':bool(git_status) if git_status is not None else None,'python':platform.python_version(),
 'installed':{x:version(x) for x in ('oaklib','semsql','rdflib')},
 'toolchain':json.loads((root/'config/toolchain.lock.json').read_text()),'artifacts':artifacts,
 'source_files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
  for folder in ('src','scripts','tests','config','examples') for p in sorted((root/folder).rglob('*'))
  if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.owl','.py','.json','.yaml','.sparql','.csv')},
 'acceptance':'build only; test and desktop confirmation required'}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
