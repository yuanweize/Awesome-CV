#!/usr/bin/env python3
"""Rank reviewed project modules from responsibility tags, never vacancy titles."""
from presentation_model import eligible_claims


def rank_projects(master, book, analysis, available_entries=()):
    claims=eligible_claims(master)
    requirements=analysis.get('responsibilities',[])
    if not requirements: raise ValueError('reviewed responsibility tags required')
    wanted={t for r in requirements for t in r['tags']}
    results=[]; covered=set()
    for mid,m in book['modules'].items():
        refs=m['claim_ids']; covered.update(refs)
        if not all(cid in claims for cid in refs): continue
        overlap=sum(r.get('weight',1)*len(set(r['tags'])&set(m.get('responsibility_tags',[]))) for r in requirements)
        # Proof quality only breaks relevance ties; it cannot rescue an irrelevant case.
        quality=m.get('selection_review',{})
        dimensions=('ownership','integration_depth','validation','maturity','distinctiveness')
        if any(not isinstance(quality.get(d),int) or not 0<=quality[d]<=2 for d in dimensions):
            raise ValueError('reviewed project quality dimensions required')
        depth=min({'strong':2,'moderate':1,'limited':0}.get(claims[c].get('interview_depth'),0) for c in refs)
        score=overlap*100+sum(quality[d] for d in dimensions)+depth+bool(m.get('images')) if overlap else 0
        results.append({'module':mid,'score':score,'responsibility_overlap':overlap,'claim_ids':refs,
                        'evidence_ids':sorted({eid for cid in refs for eid in claims[cid].get('evidence',[])}),
                        'interview_depth':[claims[c].get('interview_depth') for c in refs],
                        'visual_assets':m.get('images',[]),'quality':quality,
                        'catalog_gap':bool(available_entries) and m.get('cv_entry') not in available_entries,
                        'rationale':m['selection_rationale']})
    results.sort(key=lambda x:(-x['score'],x['module']))
    gaps=[cid for cid,c in claims.items() if c.get('type')=='project' and cid not in covered
          and wanted&set(c.get('tags',[]))]
    return {'results':results,'unrepresented_eligible_claims':gaps,
            'hard_gaps':analysis.get('hard_gaps',[]),
            'warning':'Project ranking is not fit approval; hard requirements remain independent.'}
