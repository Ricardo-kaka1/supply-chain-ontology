import json,os,unittest,uuid,subprocess,shutil
from pathlib import Path
from decimal import Decimal
from rdflib import Graph,URIRef,Literal
from rdflib.namespace import RDF,RDFS,OWL,XSD
from cabot_ontology.validation import load,validate,metadata_errors,data_errors,S,E,D
from cabot_ontology.adapter import OntologyAdapter
from fixture_db import create_fixture
ROOT=Path(__file__).resolve().parents[1]
class MVPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g=load(ROOT,True)
        cls.work=ROOT/"build/tests"/uuid.uuid4().hex
        cls.work.mkdir(parents=True)
        release=os.environ.get("CABOT_RELEASE_DIR")
        if release:
            cls.db=Path(release)/"scaudit-demo.db"
            cls.core=OntologyAdapter(Path(release)/"scaudit.db")
        else:
            cls.db=cls.work/"TEST-ONLY-named-triples.db"
            prefixes=json.loads((ROOT/"src/ontology/config/context.json").read_text())["@context"]
            create_fixture(cls.g,cls.db,prefixes)
            cls.core=None
        cls.a=OntologyAdapter(cls.db)
    @classmethod
    def tearDownClass(cls):
        cls.a.close()
        if cls.core:cls.core.close()
    def test_01_metadata_data(self):self.assertEqual([],validate(ROOT))
    def test_02_missing_definition(self):
        g=load(ROOT);g.remove((S.Supplier,D,None))
        self.assertIn('definition:'+str(S.Supplier),metadata_errors(g))
    def test_03_illegal_namespace(self):
        g=load(ROOT);g.add((URIRef('https://wrong.example/Supplier'),RDF.type,OWL.Class))
        self.assertTrue(any(x.startswith('namespace:') for x in metadata_errors(g)))
    def test_04_bad_reference(self):
        self.assertTrue(metadata_errors(load(ROOT),{'mappings':[{'term':str(S.NotDefined)}]}))
    def test_05_formal_release_blocked(self):
        self.assertIn('formal-release:temporary-namespace',metadata_errors(load(ROOT),formal=True))
    def test_06_evidence_required(self):
        g=load(ROOT,True);g.remove((E.Evaluation_INV017,S.evaluationUsesObservation,None))
        self.assertTrue(any('evaluationUsesObservation' in x for x in data_errors(g)))
    def test_07_two_observations(self):
        g=self.g
        self.assertEqual(Decimal('5500'),g.value(E.supplier_INV_017,S.observedGrossAmount).toPython())
        self.assertEqual(Decimal('5000'),g.value(E.cabot_INV_017,S.observedGrossAmount).toPython())
        self.assertEqual(g.value(E.supplier_INV_017,S.observationAboutDocument),g.value(E.cabot_INV_017,S.observationAboutDocument))
        self.assertNotEqual(g.value(E.supplier_INV_017,S.recordInDataset),g.value(E.cabot_INV_017,S.recordInDataset))
    def test_08_bridge(self):
        g=self.g
        left=Decimal(str(g.value(E.SupplierSnapshot_V100,S.normalizedNetPayableAmount)))
        right=Decimal(str(g.value(E.CabotSnapshot_V100,S.normalizedNetPayableAmount)))
        expected=json.loads((ROOT/'examples/expected_results/v100.json').read_text())
        self.assertEqual(Decimal('22300'),left);self.assertEqual(Decimal('18800'),right)
        self.assertEqual(Decimal('3500'),left-right)
        self.assertEqual(left-right,sum(map(Decimal,expected['bridge'])))
        for snapshot in (E.SupplierSnapshot_V100,E.CabotSnapshot_V100):
            self.assertEqual(Decimal(str(g.value(snapshot,S.normalizedNetPayableAmount))),
                sum(Decimal(str(g.value(obs,S.observedOutstandingAmount))) for obs in g.objects(snapshot,S.snapshotUsesObservation)))
    def test_09_credit(self):
        g=self.g;credit=E.Credit_Test
        allocated=sum(Decimal(str(g.value(a,S.allocationAmount))) for a in g.subjects(S.allocationCredit,credit))
        self.assertEqual(Decimal('200'),allocated)
        self.assertEqual(Decimal('400'),Decimal(str(g.value(credit,S.creditFaceAmount)))-allocated)
        self.assertEqual(Decimal('400'),Decimal(str(g.value(credit,S.remainingCreditAmount))))
    def test_10_search_labels(self):
        self.assertEqual('供应商',self.a.get_label('sca:Supplier','zh'))
        self.assertTrue(any(x['id']=='sca:Supplier' for x in self.a.search_terms('Vendor','en')))
        self.assertTrue(self.a.search_terms('供应商','zh'))
        self.assertEqual([],self.a.search_terms('Vendor','zh'))
    def test_11_term_definition(self):
        t=self.a.get_term('sca:Supplier')
        self.assertTrue(t['found']);self.assertTrue(t['definition']);self.assertEqual('0.1.0-dev',t['ontology_version'])
        self.assertFalse(t['deprecated']);self.assertEqual(str(S.Supplier),t['iri'])
    def test_12_ancestors(self):
        self.assertIn(str(S.Organization),self.a.get_ancestors('sca:Supplier'))
        self.assertNotIn(str(S.Organization),self.a.get_ancestors('sca:SupplierAccount'))
        self.assertNotIn(str(S.Supplier),self.a.get_ancestors('ex:Supplier_V100'))
    def test_13_curie_unknown(self):
        self.assertEqual('sca:Supplier',self.a.curie(str(S.Supplier)))
        self.assertEqual(str(S.Supplier),self.a.iri('sca:Supplier'))
        self.assertFalse(self.a.get_term('sca:DoesNotExist')['found'])
        self.assertIsNone(self.a.get_label('sca:DoesNotExist'))
        self.assertEqual([],self.a.get_ancestors('sca:DoesNotExist'))
    def test_14_finding_evidence(self):
        rels=self.a.get_relationships('ex:Finding_INV017')
        self.assertTrue(any(r['object']==str(E.Evaluation_INV017) for r in rels))
        rels=self.a.get_relationships('ex:Evaluation_INV017')
        for target in (S['REC-03'],E.Run_V100,E.supplier_INV_017,E.cabot_INV_017):
            self.assertTrue(any(r['object']==str(target) for r in rels),str(target))
    def test_15_interpretation_review(self):
        self.assertIn((E.Interpretation_INV017,RDF.type,S.FindingInterpretation),self.g)
        self.assertIn((E.Review_INV017,RDF.type,S.ReviewDecision),self.g)
        self.assertEqual(S.NeedsEvidence,self.g.value(E.Review_INV017,S.hasReviewDisposition))
        self.assertIsNone(self.g.value(E.Interpretation_INV017,S.modelId))
    def test_16_seven_rule_definitions(self):
        self.assertEqual(7,len(set(self.g.subjects(RDF.type,S.AuditRule))))
        for i in range(1,8):self.assertTrue(self.a.get_definition(f'sca:REC-{i:02d}'))
    def test_17_production_separation(self):
        self.assertFalse(any(str(s).startswith(str(E)) for s in load(ROOT).subjects()))
        if self.core:self.assertFalse(self.core.validate_term_reference('ex:Finding_INV017'))
    def test_18_oak_amount_language(self):
        vals=self.a.values('ex:supplier_INV_017','sca:observedGrossAmount')
        self.assertEqual(Decimal('5500'),Decimal(vals[0]['value']))
        self.assertEqual('xsd:decimal',vals[0]['datatype'])
        self.assertIsNone(self.a.get_label('sca:Supplier','fr'))
    def test_19_credit_oak(self):
        rels=self.a.get_relationships('ex:CreditAllocation_Test')
        self.assertTrue(any(r['object']==str(E.Credit_Test) for r in rels))
        self.assertEqual(Decimal('200'),Decimal(self.a.values('ex:CreditAllocation_Test','sca:allocationAmount')[0]['value']))
        self.assertTrue(any(r['object']==str(E.Credit_Observation) for r in rels))
    def test_20_synthetic_source_hash(self):
        import hashlib
        source=ROOT/'examples/synthetic_inputs/v100.csv'
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(digest,str(self.g.value(E.Supplier_Dataset,S.inputHash)))
    def test_21_missing_currency(self):
        g=load(ROOT,True);g.remove((E.CreditAllocation_Test,S.currencyCode,None))
        self.assertTrue(data_errors(g))
    def test_22_invalid_date(self):
        g=load(ROOT,True);g.set((E.CreditAllocation_Test,S.allocationDate,Literal('2025-02-30',datatype=XSD.string)))
        self.assertTrue(any(x.startswith('date:') for x in data_errors(g)))
    def test_23_inverse_review_links(self):
        links=list(self.a.oak.relationships(objects=['ex:Finding_INV017'],predicates=['sca:interpretationOf','sca:reviewedFinding']))
        self.assertEqual({'ex:Interpretation_INV017','ex:Review_INV017'},{x[0] for x in links})
    def test_24_sparql_negative(self):
        g=load(ROOT);g.remove((S.Supplier,D,None))
        q=(ROOT/'src/sparql/required-metadata-violation.sparql').read_text()
        self.assertTrue(any(row[0]==S.Supplier for row in g.query(q)))
if __name__=='__main__':unittest.main()
