from pathlib import Path
import copy,json,shutil,sys,tempfile,unittest,zipfile
import fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/evidence-first-cv/scripts'))
from presentation_model import claim_digest,derive_model
from visual_portfolio import validate_book,render_portfolio,audit_visual_pdf,pdf_metrics,sha
from project_selection import rank_projects
from release_bundle import package_release,verify_zip
from portfolio_selection import selected_portfolio
from test_vnext_workflow import fixture


def visual_fixture(root):
    master,model=fixture(); cid='project.signalwatch-features'
    source=root/'raw.png'; derivative=root/'assets/curated/view.png'
    derivative.parent.mkdir(parents=True)
    Image.new('RGB',(1000,600),'navy').save(source); shutil.copyfile(source,derivative)
    asset=dict(project_id='example',claim_ids=[cid],source='raw.png',derivative='assets/curated/view.png',
        type='technical-workflow',caption='Synthetic example workflow diagram, not real user evidence.',
        represented_version='test',attribution='Synthetic test fixture',restrictions='Test only',
        allowed_families=['systems'],allowed_uses=['recruiter-portfolio'],approval_state='reviewed-recruiter-safe',
        confidentiality='recruiter-safe-private',sha256=sha(derivative),source_sha256=sha(source),
        privacy_review=dict(result='passed',sha256=sha(derivative),reviewed_on='2026-10-24',method='Synthetic fixture review',findings=[]))
    module=dict(project_id='example',title='Example system',explanation='A synthetic network diagnostics case.',scope='Synthetic test only',
        claim_ids=[cid],images=['view'],allowed_families=['systems'],url='',
        contribution='This example explains the relationship between scheduled observations and the service that retains their results. It contains no private user data and does not claim real commercial deployment.',
        details='The case separates collection from analysis and makes the interface boundary visible. This is a synthetic fixture for testing the presentation machinery, not a source of career facts.',
        validation='Image presence, selected page order and artifact hashes are verified independently. Human review remains necessary for a real case because a passing parser cannot determine whether a screenshot is truthful.',
        relevance='A distinct visual workflow supports the text-only CV.',responsibility_tags=['network'],cv_entry='example',
        selection_review=dict(ownership=2,integration_depth=2,validation=1,maturity=1,distinctiveness=2),selection_rationale='Direct network responsibility')
    book=dict(schema_version='1.0',document_kind='visual_portfolio',owner='Alex Example',family_titles={'systems':'Systems'},
        assets={'view':asset},modules={'example':module},claim_fingerprints=model['claim_fingerprints'])
    return master,model,book


class VisualGovernanceTests(unittest.TestCase):
    def test_missing_assets_and_stale_pixel_review_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); master,_,book=visual_fixture(root)
            validate_book(root,book,master,['example'],'systems')
            a=book['assets']['view']; a['privacy_review']['findings']=['simulated credential and private endpoint visible']
            with self.assertRaisesRegex(ValueError,'privacy'): validate_book(root,book,master,['example'],'systems')
            a['privacy_review']['findings']=[]; a['privacy_review']['sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'privacy'): validate_book(root,book,master,['example'],'systems')
            (root/a['derivative']).unlink()
            with self.assertRaisesRegex(ValueError,'missing'): validate_book(root,book,master,['example'],'systems')

    def test_raw_original_and_wrong_family_or_caption_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); master,_,book=visual_fixture(root)
            for field,value in [('derivative','raw.png'),('caption',''),('allowed_families',['other'])]:
                changed=copy.deepcopy(book); changed['assets']['view'][field]=value
                with self.assertRaises(ValueError): validate_book(root,changed,master,['example'],'systems')

    def test_project_responsibilities_override_title_and_catalog_gap_is_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            master,_,book=visual_fixture(Path(tmp))
            for mid,tags in [('ai',['ai-integration','backend']),('reliability',['guarded-execution']),('forms',['full-stack','backend'])]:
                m=copy.deepcopy(book['modules']['example']); m['responsibility_tags']=tags; m['cv_entry']=mid
                book['modules'][mid]=m
            for tags,expected in [(['ai-integration','backend'],'ai'),(['network'],'example'),(['guarded-execution'],'reliability'),(['full-stack','backend'],'forms')]:
                report=rank_projects(master,book,{'title':'Misleading senior robotics title','responsibilities':[{'tags':tags}]},['legacy'])
                self.assertEqual(report['results'][0]['module'],expected)
                self.assertTrue(report['results'][0]['catalog_gap'])

    def test_reviewed_catalog_entry_can_be_selected_without_mutating_parent(self):
        master,model=fixture(); other=copy.deepcopy(model['entry_catalog'][0]); other['id']='alternative'
        model['entry_catalog'].append(other); model['allowed_entries']=['project','alternative']
        changed,diff=derive_model(model,{'entries':['alternative']},master)
        self.assertEqual(model['entries'],['project']); self.assertEqual(changed['entries'],['alternative'])


@unittest.skipUnless(shutil.which('lualatex') and shutil.which('qpdf'),'PDF toolchain required')
class VisualArtifactTests(unittest.TestCase):
    def test_real_visual_pdf_selection_release_and_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); master,_,book=visual_fixture(root); shutil.copytree(ROOT/'src',root/'src')
            pdf=root/'output/pdf/golden-packs/v1/example.pdf'
            report=render_portfolio(root,book,master,['example'],'systems',pdf)
            self.assertTrue(report['ok']); self.assertEqual(report['image_objects'],1)
            self.assertNotIn('Professional Summary',fitz.open(pdf)[0].get_text())
            pack={'master_portfolio':{'path':pdf.relative_to(root).as_posix(),'sha256':sha(pdf),'page_count':1,'modules':{'example':1}}}
            app={'schema_version':'1.5','application_id':'fictional','portfolio_selection':{'module_ids':['example']}}
            effective=selected_portfolio(root,app,pack,{},build=True)
            self.assertEqual(effective['page_count'],1)
            selected_portfolio(root,app,pack,{})
            a={'path':pdf.relative_to(root).as_posix(),'zip_path':'example/Portfolio.pdf','kind':'portfolio',
               'sha256':sha(pdf),'metrics':pdf_metrics(pdf),'review':{'sha256':sha(pdf),'visual':'passed'}}
            manifest={'authoritative_root':'output/pdf/golden-packs/v1','artifacts':[a]}
            archive=root/'release.zip'; self.assertTrue(package_release(root,manifest,archive)['verified'])
            self.assertTrue(verify_zip(archive,manifest))
            with zipfile.ZipFile(archive,'a') as z: z.writestr('unexpected.pdf',b'stale')
            with self.assertRaises(ValueError): verify_zip(archive,manifest)
            with self.assertRaisesRegex(ValueError,'already exists'): package_release(root,manifest,archive)

    def test_zero_image_and_orphan_pages_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'text.pdf'; doc=fitz.open(); page=doc.new_page(width=595.28,height=841.89)
            page.insert_text((40,50),'Professional Summary'); doc.new_page(width=595.28,height=841.89); doc.save(p); doc.close()
            result=audit_visual_pdf(p,1)
            self.assertFalse(result['ok'])
            self.assertTrue(any('missing meaningful' in e for e in result['errors']))
            self.assertTrue(any('orphan' in e for e in result['errors']))

if __name__=='__main__': unittest.main()
