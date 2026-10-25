#!/usr/bin/env python3
"""Build a reproducible public-only Skill ZIP; validate it in an isolated install."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/evidence-first-cv/scripts'))
from privacy_check import content_violations


def package(root, output):
    skill = root / 'skills/evidence-first-cv'
    # Allowlist repository-controlled source paths, never recursively archive root.
    paths = sorted(p for p in skill.rglob('*') if p.is_file() and
                   '__pycache__' not in p.parts and p.suffix != '.pyc')
    allowed_suffixes = {'.md', '.py', '.yaml', '.example'}
    for path in paths:
        if path.is_symlink() or any(p.is_symlink() for p in path.parents):
            raise ValueError('package rejects symlinks')
        if path.suffix not in allowed_suffixes and path.name != 'VERSION':
            raise ValueError('unexpected Skill package file: '+path.name)
        if any(part in {'meta','workspace','output','archive','.env'} for part in path.relative_to(skill).parts):
            raise ValueError('private path in Skill package')
    issues = content_violations(root, [p.relative_to(root).as_posix() for p in paths])
    if issues:
        raise ValueError('package privacy gate: '+'; '.join(issues))
    version = (skill/'VERSION').read_text().strip()
    files = {('evidence-first-cv/'+p.relative_to(skill).as_posix()):p.read_bytes() for p in paths}
    files['evidence-first-cv/RELEASE.json'] = json.dumps({
        'version':version,'dependencies':['Python >=3.10','PyYAML','PyMuPDF','Pillow','Awesome-CV checkout for rendering','LuaLaTeX','Poppler','qpdf'],
        'sha256':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()}},sort_keys=True,indent=2).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026,10,24,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    with tempfile.TemporaryDirectory(prefix='cv-skill-install-') as directory:
        with zipfile.ZipFile(output) as archive:
            archive.extractall(directory)
        installed = Path(directory)/'evidence-first-cv'
        subprocess.run([sys.executable,'-m','compileall','-q',str(installed/'scripts')],check=True)
        subprocess.run([sys.executable,str(installed/'scripts/validate_master_cv.py'),
                        str(installed/'assets/master_cv.yaml.example'),'--strict'],check=True)
        subprocess.run([sys.executable,str(installed/'scripts/pack_selection.py'),'--help'],
                       check=True,stdout=subprocess.DEVNULL)
    return {'version':version,'path':str(output),'files':len(files),
            'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'isolated_install':'passed'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    version=(ROOT/'skills/evidence-first-cv/VERSION').read_text().strip()
    p.add_argument('--output',type=Path,default=ROOT/f'output/releases/evidence-first-cv-{version}.zip')
    print(json.dumps(package(ROOT,p.parse_args().output),indent=2))
