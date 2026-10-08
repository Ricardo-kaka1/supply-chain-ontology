import json,subprocess,hashlib
from pathlib import Path
from importlib.metadata import version
root=Path(__file__).resolve().parents[1]
lock=json.loads((root/'config/toolchain.lock.json').read_text())
if hashlib.sha256((root/'src/ontology/imports/metadata.owl').read_bytes()).hexdigest()!=lock['metadata_bridge_sha256']:
    raise RuntimeError('Local metadata dependency differs from reviewed hash')
for name in ('oaklib','semsql'):
    actual=version(name)
    if actual!=lock[name+'_version']:raise RuntimeError(f'{name}: expected {lock[name+"_version"]}, got {actual}')
p=subprocess.run(['robot','--version'],check=True,text=True,capture_output=True)
if lock['robot_version'] not in p.stdout+p.stderr:raise RuntimeError('Unexpected ROBOT version')
print(json.dumps({'robot':p.stdout.strip(),'oaklib':version('oaklib'),'semsql':version('semsql'),'mount':str(root)},indent=2))
