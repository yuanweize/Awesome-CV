#!/usr/bin/env python3
"""Governed visual modules: canonical claims, reviewed pixels, one case per page."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
import fitz
import yaml
from PIL import Image
from presentation_model import eligible_claims, claim_digest, tex, compile_tex_pdf


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_file(root, raw):
    root=Path(root).resolve()
    path=root/raw
    if not path.resolve().is_relative_to(root) or any(p.is_symlink() for p in [path,*path.parents]):
        raise ValueError('unsafe asset/source path')
    if not path.is_file():
        raise ValueError('missing asset/source: '+str(raw))
    return path.resolve()


def validate_book(root, book, master, module_ids, family):
    claims=eligible_claims(master)
    if book.get('schema_version')!='1.0' or book.get('document_kind')!='visual_portfolio':
        raise ValueError('visual portfolio schema required')
    if not module_ids or len(set(module_ids))!=len(module_ids):
        raise ValueError('nonempty unique module selection required')
    resolved={}
    for mid in module_ids:
        if mid not in book['modules']:
            raise ValueError('unknown visual module')
        module=book['modules'][mid]
        if family not in module['allowed_families']:
            raise ValueError('module not allowed for family')
        if not module.get('images') or not module.get('details') or not module.get('contribution'):
            raise ValueError('case needs visual proof, contribution and technical details')
        refs=module['claim_ids']
        for cid in refs:
            if cid not in claims or book['claim_fingerprints'].get(cid)!=claim_digest(claims[cid]):
                raise ValueError('ineligible or stale case claim: '+cid)
        public={e['locator'] for e in master['evidence_registry'] if e.get('visibility')=='public'
                and e['id'] in {eid for cid in refs for eid in claims[cid].get('evidence',[])}}
        if module.get('url') and module['url'] not in public:
            raise ValueError('case verification URL lacks mapped public evidence')
        for aid in module['images']:
            asset=book['assets'][aid]
            if not set(asset['claim_ids'])<=set(refs) or asset['project_id']!=module['project_id']:
                raise ValueError('project/image claim mapping mismatch')
            if family not in asset['allowed_families'] or 'recruiter-portfolio' not in asset['allowed_uses']:
                raise ValueError('asset use not allowed')
            if not all(asset.get(k) for k in ('caption','source','derivative','type','represented_version','attribution','restrictions')):
                raise ValueError('asset provenance/caption incomplete')
            image=safe_file(root,asset['derivative'])
            original=safe_file(root,asset['source'])
            if image==original or not any(part in {'curated','generated'} for part in image.parts):
                raise ValueError('renderer requires a recruiter-safe derivative')
            if sha(image)!=asset['sha256'] or sha(original)!=asset['source_sha256']:
                raise ValueError('asset fingerprint mismatch')
            review=asset.get('privacy_review',{})
            if (asset.get('approval_state')!='reviewed-recruiter-safe' or
                asset.get('confidentiality')!='recruiter-safe-private' or
                review.get('sha256')!=sha(image) or review.get('result')!='passed' or
                review.get('findings') or not review.get('reviewed_on') or not review.get('method')):
                raise ValueError('asset privacy review missing, stale or failed')
            with Image.open(image) as im:
                if min(im.size)<200:
                    raise ValueError('image too small for meaningful visual proof')
                im.verify()
            resolved[aid]=image
    return resolved


def render_portfolio(root, book, master, module_ids, family, output):
    images=validate_book(root,book,master,module_ids,family)
    lines=[r'\documentclass[11pt,a4paper]{awesome-cv}',r'\usepackage{modern-resume}',
           r'\geometry{left=1.65cm,right=1.65cm,top=1.4cm,bottom=1.5cm}',
           r'\begin{document}\pagestyle{empty}\raggedright\color{modernText}']
    for index,mid in enumerate(module_ids):
        m=book['modules'][mid]
        if index: lines.append(r'\clearpage')
        lines += [r'{\fontsize{9}{12}\selectfont\color{modernMuted} '+tex(book['owner'])+
                  ' / '+tex(book['family_titles'][family])+r'\hfill '+str(index+1)+r'\par}',
                  r'\vspace{2mm}\hrule\vspace{4mm}',
                  r'{\fontsize{23}{27}\selectfont\bfseries\color{modernNavy} '+tex(m['title'])+r'\par}',
                  r'\vspace{2mm}{\fontsize{11}{14}\selectfont '+tex(m['explanation'])+r'\par}',
                  r'\vspace{2mm}{\fontsize{9}{12}\selectfont\color{modernMuted} '+tex(m['scope'])+r'\par}\vspace{4mm}']
        height=100 if len(m['images'])==1 else 58
        for aid in m['images']:
            path=images[aid].as_posix()
            if any(c in path for c in '{}%#'):
                raise ValueError('unsafe image path for TeX')
            lines += [r'\noindent\makebox[\linewidth][c]{\includegraphics[width=\linewidth,height='+str(height)+r'mm,keepaspectratio]{\detokenize{'+path+'}}}'+r'\par',
                      r'\vspace{1.5mm}{\fontsize{8.5}{11}\selectfont\color{modernMuted} '+tex(book['assets'][aid]['caption'])+r'\par}\vspace{3mm}']
        for title,content in [('Contribution',m['contribution']),('Engineering decisions',m['details']),('Validation and scope',m['validation'])]:
            lines += [r'\vspace{2mm}{\fontsize{10}{13}\selectfont\bfseries\color{modernNavy} '+title+r'\par}',
                      r'{\fontsize{10}{13}\selectfont\color{modernText} '+tex(content)+r'\par}']
        lines += [r'\vfill{\fontsize{9}{12}\selectfont\color{modernMuted} '+tex(m['relevance'])+r'\par}']
        if m.get('url'):
            url=m['url']
            if not re.fullmatch(r'https://[A-Za-z0-9./_?=&#%-]+',url): raise ValueError('unsafe URL')
            lines.append(r'{\fontsize{9}{12}\selectfont\href{'+url+'}{'+tex(url.removeprefix('https://'))+r'}\par}')
    lines.append(r'\end{document}')
    pdf=compile_tex_pdf(root,'\n'.join(lines),output)
    report=audit_visual_pdf(pdf,len(module_ids))
    if not report['ok']: raise ValueError('; '.join(report['errors']))
    return report


def pdf_metrics(path):
    with fitz.open(path) as doc:
        return {'page_count':len(doc),'image_objects':sum(len(p.get_images(full=True)) for p in doc),
                'pages':[{'words':len(p.get_text().split()),'images':len(p.get_image_info()),
                          'image_area':sum(fitz.Rect(i['bbox']).get_area() for i in p.get_image_info())/p.rect.get_area(),
                          'links':len(p.get_links())} for p in doc]}


def audit_visual_pdf(path, expected_pages, cv_path=None):
    metrics=pdf_metrics(path)
    errors=[]
    if metrics['page_count']!=expected_pages: errors.append('case pagination/orphan page mismatch')
    with fitz.open(path) as doc:
        for n,p in enumerate(doc):
            text=p.get_text()
            row=metrics['pages'][n]
            if not row['images'] or row['image_area']<.08: errors.append(f'page {n+1}: missing meaningful embedded visual')
            if row['words']<65: errors.append(f'page {n+1}: nearly empty case/orphan')
            if 'Professional Summary' in text or '\nSkills\n' in text: errors.append('Portfolio duplicates CV structure')
            for im in p.get_image_info():
                rect=fitz.Rect(im['bbox'])
                if not p.rect.contains(rect): errors.append('clipped image')
            if abs(p.rect.width-595.28)>2 or abs(p.rect.height-841.89)>2: errors.append('non-A4 portfolio')
        if cv_path:
            with fitz.open(cv_path) as cv:
                cvtext=' '.join(p.get_text() for p in cv)
            long_lines=[line.strip() for p in doc for line in p.get_text().splitlines() if len(line.strip())>65]
            if long_lines and sum(line in cvtext for line in long_lines)/len(long_lines)>.6:
                errors.append('Portfolio substantially repeats CV text')
    subprocess.run(['qpdf','--check',str(path)],check=True,stdout=subprocess.DEVNULL)
    return {'ok':not errors,'errors':errors,**metrics,'visual_review':'pending'}


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('book',type=Path); p.add_argument('output',type=Path)
    p.add_argument('--family',required=True); p.add_argument('--modules',nargs='+',required=True)
    a=p.parse_args(); root=Path.cwd()
    print(json.dumps(render_portfolio(root,yaml.safe_load(a.book.read_text()),
        yaml.safe_load((root/'meta/master_cv.yaml').read_text()),a.modules,a.family,a.output),indent=2))


if __name__=='__main__': main()
