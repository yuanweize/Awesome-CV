import copy
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/evidence-first-cv/scripts'))
from legacy_title_variant import prepare, source_for
from application_variant import build_variant, verify_variant
from application_delivery_matrix import selected_pack, file_sha256, pdf_page_count, merge_pdfs, build_matrix, audit_matrix_data
from presentation_model import claim_digest, compile_tex_pdf
from golden_pack_audit import source_fingerprint
from application_manifest import new_manifest


class LegacyTitleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='legacy-title-test-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        shutil.copytree(ROOT/'src',self.root/'src')
        self.profile=self.root/'workspace/profiles/example'
        self.snapshot=self.root/'workspace/golden-packs/v1/example'
        self.profile.mkdir(parents=True)
        (self.profile/'sections').mkdir()
        (self.profile/'sections/summary.tex').write_text('% legacy main template presence check\n')
        (self.profile/'config.tex').write_text('\\name{Alex}{Example}\n\\position{Systems Engineer{\\enskip\\cdotp\\enskip}Cloud and Software}\n\\email{alex@example.org}\n')
        (self.profile/'sections/order.tex').write_text('\\cvsection{Experience}\nOperated a personal network monitoring service.\\par\n')
        shutil.copytree(self.profile,self.snapshot)
        self.claim={'id':'project.network','status':'verified','cv_eligible':True,'statement':'Operated a personal network monitoring service.'}
        self.pack={'version':'v1','status':'approved','approved_at':'2026-10-25','source_profile':str(self.profile.relative_to(self.root)),'source_snapshot':str(self.snapshot.relative_to(self.root)),'source_sha256':source_fingerprint(self.profile),'role_families':['systems']}
        self.catalog={'parent':{'pack_id':'example','source_sha256':self.pack['source_sha256']},'review':{'status':'reviewed'},'headlines':{'Network Systems Engineer':{'claim_ids':['project.network'],'rationale':'Focus on demonstrated network operation.'}},'claim_fingerprints':{'project.network':claim_digest(self.claim)}}
        self.catalog_path=self.root/'meta/title_catalogs/example.yaml'
        self.catalog_path.parent.mkdir(parents=True)
        self.catalog_path.write_text(yaml.safe_dump(self.catalog))
        (self.root/'meta/master_cv.yaml').write_text(yaml.safe_dump({'personal_information':{'full_name':'Alex Example'},'claim_registry':[self.claim]}))

    def test_only_title_and_current_evidence(self):
        before=source_fingerprint(self.profile)
        _,config,_=prepare(self.root,'example',self.pack,{'headline':'Network Systems Engineer'},'meta/title_catalogs/example.yaml')
        self.assertIn('\\position{Network Systems Engineer}',config)
        self.assertIn('\\email{alex@example.org}',config)
        for request in [{'headline':'Senior Network Architect'}, {'headline':'Network Systems Engineer','summary':['new']}]:
            with self.assertRaises(ValueError):prepare(self.root,'example',self.pack,request,'meta/title_catalogs/example.yaml')
        changed=copy.deepcopy(self.claim);changed['statement']='Changed evidence'
        (self.root/'meta/master_cv.yaml').write_text(yaml.safe_dump({'claim_registry':[changed]}))
        with self.assertRaisesRegex(ValueError,'stale'):prepare(self.root,'example',self.pack,{'headline':'Network Systems Engineer'},'meta/title_catalogs/example.yaml')
        self.assertEqual(before,source_fingerprint(self.profile))

    @unittest.skipUnless(all(shutil.which(x) for x in ['lualatex','qpdf','pdftotext']), 'requires PDF tools')
    def test_real_legacy_derivative_and_tamper_rejection(self):
        root=self.root
        cv=compile_tex_pdf(root,source_for(root,self.snapshot,self.snapshot/'config.tex'),root/'output/pdf/golden-packs/v1/CV.pdf')
        portfolio=cv.parent/'Portfolio.pdf';shutil.copyfile(cv,portfolio)
        combined=cv.parent/'Combined.pdf';merge_pdfs((cv,portfolio),combined)
        self.pack['artifacts']={k:{'path':str(p.relative_to(root)),'sha256':file_sha256(p),'page_count':pdf_page_count(p)} for k,p in [('cv',cv),('portfolio',portfolio),('combined',combined)]}
        (root/'meta/golden_packs.yaml').write_text(yaml.safe_dump({'schema_version':'1.0','packs':{'example':self.pack}}))
        app=root/'meta/applications/example-role';app.mkdir(parents=True)
        jd=app/'jd.md';jd.write_text('Senior Infrastructure Specialist: maintain network monitoring.')
        data=new_manifest('example-role','Example','Senior Infrastructure Specialist','systems',str(jd.relative_to(root)),file_sha256(jd),'example-role')
        data['golden_pack']={'selected_pack':'example','version':'v1','cv_sha256':file_sha256(cv)}
        manifest=app/'application.yaml';manifest.write_text(yaml.safe_dump(data))
        request=app/'request.yaml';request.write_text(yaml.safe_dump({'headline':'Network Systems Engineer'}))
        before=file_sha256(cv)
        result=build_variant(root,manifest,request)
        self.assertEqual(result['mode'],'legacy-title')
        self.assertEqual(before,file_sha256(cv))
        self.assertEqual(build_variant(root,manifest,request)['record'],result['record'])
        updated=yaml.safe_load(manifest.read_text());_,pack,golden=selected_pack(root,updated,root/'meta/golden_packs.yaml')
        effective=verify_variant(root,updated,pack,golden)
        import fitz
        text=''.join(p.get_text() for p in fitz.open(effective['path']))
        self.assertIn('Network Systems Engineer',text)
        self.assertIn('Operated a personal network monitoring service.',text)
        self.assertNotIn('Senior Infrastructure Specialist',text)
        # The letter shares the personal headline, while the employer title stays a subject.
        cfg=(root/result['record']).parent/'config.tex'
        letter_source=source_for(root,self.snapshot,cfg).split(r'\begin{document}')[0]
        letter_source+=r'\begin{document}\makecvheader[L]\par Application: Senior Infrastructure Specialist\par Dear Hiring Team,\par I operate a personal network monitoring service.\par Kind regards, Alex Example\end{document}'
        cl=compile_tex_pdf(root,letter_source,root/'workspace/build/Cover_Letter.pdf')
        updated['artifacts'].update(cover_letter_pdf=str(cl.relative_to(root)),cover_letter_sha256=file_sha256(cl),cover_letter_page_count=pdf_page_count(cl))
        manifest.write_text(yaml.safe_dump(updated))
        matrix=build_matrix(root,manifest,registry_path=root/'meta/golden_packs.yaml')
        self.assertTrue(matrix['ok'],matrix)
        updated=yaml.safe_load(manifest.read_text())
        self.assertEqual(updated['artifacts']['cv_sha256'],result['variant_cv_sha256'])
        self.assertTrue(audit_matrix_data(root,updated,root/'meta/golden_packs.yaml')['ok'])
        letter_text=''.join(p.get_text() for p in fitz.open(cl))
        self.assertIn('Network Systems Engineer',letter_text)
        self.assertIn('Senior Infrastructure Specialist',letter_text)
        config=(root/result['record']).parent/'config.tex';config.write_text(config.read_text()+'\\name{Fake}{Name}')
        with self.assertRaisesRegex(ValueError,'title-only'):verify_variant(root,updated,pack,golden)


if __name__=='__main__':unittest.main()
