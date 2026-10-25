#!/usr/bin/env python3
"""Package only manifest-authoritative recruiter PDFs, then inspect ZIP bytes."""
import json
from pathlib import Path
import tempfile
import zipfile
from visual_portfolio import sha, safe_file, pdf_metrics


def verify_zip(archive_path, manifest):
    with zipfile.ZipFile(archive_path) as z, tempfile.TemporaryDirectory(prefix='cv-release-check-') as tmp:
        expected={a['zip_path']:a for a in manifest['artifacts']}
        if set(z.namelist())!=set(expected)|{'release.json'}:
            raise ValueError('ZIP contains missing, stale or unexpected entries')
        if json.loads(z.read('release.json'))!=manifest: raise ValueError('ZIP manifest mismatch')
        for name,a in expected.items():
            p=Path(tmp)/Path(name).name
            p.write_bytes(z.read(name))
            if sha(p)!=a['sha256'] or pdf_metrics(p)!=a['metrics']:
                raise ValueError('packaged artifact differs from manifest: '+name)
    return True


def package_release(root, manifest, output):
    if Path(output).exists(): raise ValueError('release ZIP already exists; refuse silent replacement')
    for a in manifest['artifacts']:
        p=safe_file(root,a['path'])
        if not p.is_relative_to((Path(root)/manifest['authoritative_root']).resolve()):
            raise ValueError('mixed release source directories')
        if sha(p)!=a['sha256'] or pdf_metrics(p)!=a['metrics']:
            raise ValueError('stale release artifact')
        if a.get('review',{}).get('sha256')!=a['sha256'] or a['review'].get('visual')!='passed':
            raise ValueError('exact artifact visual review required')
        if a['kind'] in {'portfolio','master_portfolio'} and not a['metrics']['image_objects']:
            raise ValueError('visual portfolio cannot have zero images')
        if Path(a['zip_path']).is_absolute() or '..' in Path(a['zip_path']).parts:
            raise ValueError('unsafe ZIP member')
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        for a in manifest['artifacts']:
            info=zipfile.ZipInfo(a['zip_path'],(2026,10,24,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(Path(root)/a['path']).read_bytes())
        info=zipfile.ZipInfo('release.json',(2026,10,24,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2))
    verify_zip(output,manifest)
    return {'sha256':sha(output),'verified':True}
