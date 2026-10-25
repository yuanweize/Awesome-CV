"""Title-only derivatives of an immutable legacy TeX Pack, without model migration."""
from pathlib import Path
import re

from presentation_model import claim_digest, eligible_claims, fingerprint, tex, compile_tex_pdf
from golden_pack_audit import source_fingerprint


def prepare(root, pack_id, pack, changes, catalog_path):
    from application_variant import safe_path
    from application_delivery_matrix import load_yaml, file_sha256
    if set(changes) != {'headline'}:
        raise ValueError('legacy variant permits headline only')
    snapshot = safe_path(root, pack['source_snapshot'], 'workspace/golden-packs')
    profile = safe_path(root, pack['source_profile'], 'workspace/profiles')
    if any(source_fingerprint(p) != pack['source_sha256'] for p in [snapshot, profile]):
        raise ValueError('Golden source fingerprint mismatch')
    catalog_path = safe_path(root, catalog_path, 'meta/title_catalogs')
    catalog = load_yaml(catalog_path, 'title catalog')
    if catalog.get('parent') != {'pack_id': pack_id, 'source_sha256': pack['source_sha256']}:
        raise ValueError('title catalog parent mismatch')
    if catalog.get('review', {}).get('status') != 'reviewed':
        raise ValueError('title catalog requires evidence review')
    title = changes['headline']
    if not isinstance(title, str) or len(title) > 95 or any(c in title for c in '\n\\{}|'):
        raise ValueError('invalid headline')
    item = catalog.get('headlines', {}).get(title)
    if not item or not item.get('rationale') or not item.get('claim_ids'):
        raise ValueError('headline lacks reviewed evidence mapping')
    claims = eligible_claims(load_yaml(root/'meta/master_cv.yaml', 'master'))
    for cid in item['claim_ids']:
        if cid not in claims or catalog.get('claim_fingerprints', {}).get(cid) != claim_digest(claims[cid]):
            raise ValueError('headline claim is stale or ineligible')
    config = (snapshot/'config.tex').read_text()
    # Legacy config has one complete position command on its own line. Reject other forms.
    pattern = r'(?m)^\\position\{[^\n]*\}\s*$'
    matches = list(re.finditer(pattern, config))
    if len(matches) != 1:
        raise ValueError('legacy config requires exactly one single-line position command')
    position = r'\position{'+tex(title)+'}'
    updated = config[:matches[0].start()]+position+'\n'+config[matches[0].end():]
    renderer = {str(p.relative_to(root)):file_sha256(p) for p in sorted((root/'src').rglob('*')) if p.is_file()}
    return snapshot, updated, {'catalog':catalog_path.relative_to(root).as_posix(),
        'catalog_sha256':file_sha256(catalog_path), 'renderer':renderer,
        'selected_claim_ids':sorted(item['claim_ids']),
        'field_diff':{'headline':{'before':matches[0].group().strip(), 'after':title}}}


def source_for(root, snapshot, config_path):
    source = (root/'src/main.tex').read_text()
    source = source.replace('workspace/current/config.tex', str(config_path))
    return source.replace('workspace/current/sections', str(snapshot/'sections'))


def verify(root, manifest, pack, golden, record, record_path):
    from application_variant import safe_path
    from application_delivery_matrix import file_sha256, pdf_page_count, qpdf_check
    snapshot, config, facts = prepare(root, manifest['golden_pack']['selected_pack'], pack,
                                     record['changes'], record['title_review']['catalog'])
    if record['title_review'] != facts or record['change_whitelist'] != ['headline']:
        raise ValueError('legacy title review or renderer changed')
    config_path = record_path.parent/'config.tex'
    if config_path.read_text() != config:
        raise ValueError('legacy variant config differs from title-only derivation')
    pdf = safe_path(root, record['artifact']['path'], f"workspace/application-variants/{manifest['application_id']}")
    if pdf.with_suffix('.tex').read_text() != source_for(root, snapshot, config_path):
        raise ValueError('legacy variant rendered source mismatch')
    digest = file_sha256(pdf)
    if digest != record['artifact']['variant_cv_sha256'] or digest != manifest['application_variant']['variant_cv_sha256']:
        raise ValueError('legacy variant artifact hash mismatch')
    pages = pdf_page_count(pdf)
    if pages != golden['cv']['page_count'] or pages != record['artifact']['page_count']:
        raise ValueError('title-only variant changed page count')
    qpdf_check(pdf)
    return {'path':pdf, 'sha256':digest, 'page_count':pages}


def build(root, manifest_path, manifest, pack_id, pack, golden, changes):
    from application_variant import safe_path, verify_variant
    from application_delivery_matrix import save_yaml, file_sha256, pdf_page_count
    catalog_path = f'meta/title_catalogs/{pack_id}.yaml'
    snapshot, config, facts = prepare(root, pack_id, pack, changes, catalog_path)
    revision = fingerprint({'parent':pack['source_sha256'], 'changes':changes, 'review':facts})[:16]
    dest = safe_path(root, f"workspace/application-variants/{manifest['application_id']}/{revision}", 'workspace/application-variants')
    record_path = dest/'variant.yaml'
    if dest.exists():
        if manifest.get('application_variant', {}).get('record') != record_path.relative_to(root).as_posix():
            raise ValueError('existing revision is not manifest-bound')
        verify_variant(root, manifest, pack, golden)
        return {'mode':'legacy-title', **manifest['application_variant']}
    dest.mkdir(parents=True)
    config_path = dest/'config.tex'
    config_path.write_text(config)
    pdf = compile_tex_pdf(root, source_for(root, snapshot, config_path), dest/'CV.pdf')
    record = {'schema_version':'1.0', 'mode':'legacy-title', 'application_id':manifest['application_id'],
        'parent':{'pack_id':pack_id,'version':pack['version'],'golden_cv_sha256':golden['cv']['sha256'], 'source_sha256':pack['source_sha256']},
        'requested_target_title':manifest['target']['title'], 'rendered_headline':changes['headline'],
        'changes':changes,'change_whitelist':['headline'],'title_review':facts,
        'artifact':{'path':pdf.relative_to(root).as_posix(),'variant_cv_sha256':file_sha256(pdf),'page_count':pdf_page_count(pdf)},
        'quality':{'visual':'pending','first_screen':'pending editorial review'}}
    save_yaml(record_path, record)
    manifest['schema_version']='1.5'
    manifest['application_variant']={'record':record_path.relative_to(root).as_posix(),
        'record_sha256':file_sha256(record_path),'golden_cv_sha256':golden['cv']['sha256'],'variant_cv_sha256':file_sha256(pdf)}
    manifest['stage']='drafted'
    manifest['quality']={k:'pending' for k in ['claim_audit','ats_text_check','visual_check','privacy_check']}
    verify_variant(root, manifest, pack, golden)
    save_yaml(manifest_path, manifest)
    return {'mode':'legacy-title', **manifest['application_variant']}
