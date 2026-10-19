"""Refresh checksums of tracked and current non-excluded publication inputs."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'FILE-MANIFEST.json'
old={x['path']:x for x in json.loads(manifest.read_text())['files']}
names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
files=[]
for name in sorted(set(names)):
 path=ROOT/name
 if not name or name=='FILE-MANIFEST.json'or not path.is_file():continue
 row=old.get(name,{'path':name}).copy();data=path.read_bytes();row.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 if name.endswith('Reading-Edition.docx'):row.update(date='2026-10-19',description='Author-edited reading edition with linked article and passage references')
 files.append(row)
manifest.write_text(json.dumps({'algorithm':'SHA-256','files':files},ensure_ascii=False,indent=2)+'\n')
print('Manifest:',len(files),'files')
