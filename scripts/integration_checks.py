"""Run only after real official SemSQL builds. Never substitute a fixture DB."""
import json,os,shutil,subprocess,sys,uuid
from pathlib import Path
from rdflib import Graph,URIRef
from rdflib.namespace import RDF
from rdflib.compare import to_isomorphic
from cabot_ontology.adapter import OntologyAdapter
root=Path(__file__).resolve().parents[1];release=Path(sys.argv[1]).resolve()
scratch=root/'build/reproducibility'/uuid.uuid4().hex;scratch.mkdir(parents=True)
g=Graph().parse(release/'scaudit-demo.owl')
g.add((URIRef('urn:example:cabot-audit:Supplier_V100'),RDF.type,URIRef('https://example.org/cabot-audit/ontology/Invoice')))
g.serialize(scratch/'inconsistent.owl',format='xml')
p=subprocess.run(['robot','reason','-i',str(scratch/'inconsistent.owl'),'--reasoner','hermit','-o',str(scratch/'bad.owl')],capture_output=True,text=True)
(scratch/'negative.log').write_text(p.stdout+p.stderr)
if p.returncode==0 or 'inconsisten' not in (p.stdout+p.stderr).lower():raise RuntimeError('Negative reasoner acceptance failed')
# A fresh source staging directory forces official Makefile and SemSQL rebuilds.
for folder in ('src','scripts','tests','config','examples'):
    shutil.copytree(root/folder,scratch/folder,ignore=shutil.ignore_patterns('__pycache__','tmp','reports','*.db','scaudit.owl','scaudit-full.owl','scaudit-base.owl','*.db.tmp'))
subprocess.run(['make','sca-build','IMP=false'],cwd=scratch/'src/ontology',check=True)
other=scratch/'build/releases/0.1.0-dev'
for name in ('scaudit.owl','scaudit-demo.owl'):
    if to_isomorphic(Graph().parse(release/name))!=to_isomorphic(Graph().parse(other/name)):
        raise RuntimeError('Non-reproducible semantics: '+name)
a=OntologyAdapter(release/'scaudit-demo.db');b=OntologyAdapter(other/'scaudit-demo.db')
try:
    for term in ('sca:Supplier','sca:REC-03','ex:Finding_INV017','ex:CreditAllocation_Test'):
        if a.get_term(term)!=b.get_term(term) or a.get_relationships(term)!=b.get_relationships(term):
            raise RuntimeError('Non-reproducible query: '+term)
finally:a.close();b.close()
(release/'acceptance.json').write_text(json.dumps({'official_build_and_oak_tests':'passed',
 'hermit_negative':'passed','semantic_reproducibility':'passed','protege_desktop':'pending separate confirmation'},indent=2))
