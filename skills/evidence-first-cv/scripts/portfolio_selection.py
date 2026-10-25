"""Select immutable approved master-Portfolio pages; never rewrite case content."""
from pathlib import Path
import subprocess
from visual_portfolio import safe_file,sha,pdf_metrics,audit_visual_pdf
from presentation_model import fingerprint


def selected_portfolio(root,manifest,pack,golden,build=False):
    root=Path(root).resolve()
    selection=manifest.get('portfolio_selection')
    if not selection: return golden['portfolio']
    if str(manifest.get('schema_version'))!='1.5': raise ValueError('module selection requires manifest 1.5')
    if not pack.get('master_portfolio'): raise ValueError('Pack has no approved visual module library')
    parent=pack['master_portfolio']; source=safe_file(root,parent['path'])
    if sha(source)!=parent['sha256']: raise ValueError('master Portfolio hash mismatch')
    ids=selection.get('module_ids',[])
    pages=parent['modules']
    if not ids or len(set(ids))!=len(ids) or not set(ids)<=set(pages): raise ValueError('unknown/duplicate Portfolio module')
    revision=fingerprint({'parent':parent['sha256'],'modules':ids})[:16]
    appid=manifest['application_id']
    if not appid or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in appid): raise ValueError('unsafe application ID')
    path=Path(root)/'workspace/application-variants'/appid/revision/'Portfolio.pdf'
    if not path.resolve().is_relative_to((Path(root)/'workspace/application-variants').resolve()): raise ValueError('unsafe selection path')
    for part in [path,*path.parents]:
        if part.is_symlink(): raise ValueError('symlink selection path')
    nums=[pages[mid] for mid in ids]
    if not all(isinstance(n,int) and 1<=n<=parent['page_count'] for n in nums): raise ValueError('invalid module page map')
    if build:
        if not path.exists():
            path.parent.mkdir(parents=True,exist_ok=True)
            subprocess.run(['qpdf','--empty','--pages',str(source),','.join(map(str,nums)),'--',str(path)],check=True)
        report=audit_visual_pdf(path,len(nums))
        if not report['ok']: raise ValueError('; '.join(report['errors']))
        binding={'parent_sha256':parent['sha256'],'path':path.relative_to(root).as_posix(),'sha256':sha(path),'page_count':len(nums)}
        if selection.get('artifact') and selection['artifact']!=binding: raise ValueError('selection artifact drift')
        selection['artifact']=binding
    binding=selection.get('artifact',{})
    if binding.get('parent_sha256')!=parent['sha256'] or binding.get('path')!=path.relative_to(root).as_posix() or not path.is_file() or sha(path)!=binding.get('sha256'):
        raise ValueError('unverified Portfolio selection')
    # Verify actual content/order against immutable parent, not just a self-declared hash.
    import fitz
    with fitz.open(source) as src,fitz.open(path) as dst:
        if len(dst)!=len(nums): raise ValueError('selection page count drift')
        for i,n in enumerate(nums):
            if src[n-1].get_pixmap().samples!=dst[i].get_pixmap().samples: raise ValueError('selection pixels/order differ from parent')
    return {'path':path,'sha256':sha(path),'page_count':len(nums)}
