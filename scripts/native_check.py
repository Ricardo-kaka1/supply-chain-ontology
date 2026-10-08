"""Native diagnostics. Explicitly NOT the Docker/ODK acceptance pipeline."""
import os,subprocess,json,sys,hashlib
from pathlib import Path
from rdflib import Graph,URIRef,Namespace,BNode
from rdflib.namespace import RDF,OWL
from rdflib.compare import to_isomorphic
ROOT=Path(__file__).resolve().parents[1]
S=Namespace('https://example.org/cabot-audit/ontology/')
out=ROOT/'build/native';out.mkdir(parents=True,exist_ok=True)
java=ROOT/'.tools/Protege-5.6.9/jre/bin/java.exe';jar=ROOT/'.tools/robot.jar'
os.environ['PYTHONPATH']=str(ROOT/'src')
os.environ['PYSTOW_HOME']=str(ROOT/'build/cache')
results=[]
def run(name,args,cwd=ROOT,expect_failure=False):
    p=subprocess.run([str(x) for x in args],cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace')
    (out/(name+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
    passed=(p.returncode!=0) if expect_failure else (p.returncode==0)
    results.append({'check':name,'passed':passed,'exit_code':p.returncode,'expected_failure':expect_failure})
    if not passed:raise RuntimeError(f'{name} failed: {p.stdout[-1000:]} {p.stderr[-1000:]}')
    return p
robot=[java,'-Xmx2G','-jar',jar]
success=False
try:
    run('python-data-gates',[sys.executable,ROOT/'scripts/check.py'])
    run('oak-named-triple-fixture-tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'])
    source=ROOT/'src/ontology/scaudit-edit.owl'
    run('hermit-core',robot+['reason','--input',source,'--reasoner','hermit','--output',out/'reasoned.owl'],source.parent)
    run('hermit-demo',robot+['merge','--input',ROOT/'examples/owl/cabot-demo.owl','reason','--reasoner','hermit','--output',out/'demo-reasoned.owl'],ROOT/'examples/owl')
    run('owl2dl',robot+['validate-profile','--input',out/'demo-reasoned.owl','--profile','DL','--output',out/'owl2dl.txt'])
    run('metadata-sparql',robot+['verify','--input',source,'--queries',ROOT/'src/sparql/required-metadata-violation.sparql',ROOT/'src/sparql/internal-namespace-violation.sparql','--output-dir',out],source.parent)
    run('robot-report',robot+['report','--input',source,'--profile',ROOT/'src/ontology/profile.txt','--fail-on','ERROR','--output',out/'robot-report.tsv'],source.parent)
    # ROBOT ClassAssertion materializes direct types. Prove the superclass
    # entailment by refutation, rather than requiring an indirect type triple.
    g=Graph().parse(out/'demo-reasoned.owl');not_org=BNode()
    g.add((not_org,RDF.type,OWL.Class));g.add((not_org,OWL.complementOf,S.Organization))
    g.add((URIRef('urn:example:cabot-audit:Supplier_V100'),RDF.type,not_org))
    g.serialize(out/'negated-entailment.owl',format='xml')
    p=run('hermit-superclass-entailment',robot+['reason','--input',out/'negated-entailment.owl','--reasoner','hermit','--output',out/'must-not-entail.owl'],expect_failure=True)
    assert 'inconsisten' in (p.stdout+p.stderr).lower()
    # Merge output has no dynamic imports. Contradict a declared disjoint pair.
    bad=Graph().parse(out/'demo-reasoned.owl')
    bad.add((URIRef('urn:example:cabot-audit:Supplier_V100'),RDF.type,S.Invoice))
    bad.serialize(out/'inconsistent.owl',format='xml')
    p=run('hermit-negative',robot+['reason','--input',out/'inconsistent.owl','--reasoner','hermit','--output',out/'must-not-publish.owl'],expect_failure=True)
    assert 'inconsisten' in (p.stdout+p.stderr).lower(), 'Failure was not a reasoner inconsistency'
    run('hermit-repeat',robot+['reason','--input',source,'--reasoner','hermit','--output',out/'repeat.owl'],source.parent)
    assert to_isomorphic(Graph().parse(out/'reasoned.owl'))==to_isomorphic(Graph().parse(out/'repeat.owl'))
    results.append({'check':'native-semantic-reproducibility','passed':True})
    success=True
finally:
    (out/'status.json').write_text(json.dumps({'mode':'native-diagnostics','passed':success,'checks':results,
      'docker_odk_acceptance':'NOT_RUN','official_semsql_build':'NOT_RUN','protege_desktop':'PENDING_USER_CONFIRMATION'},indent=2),encoding='utf-8')
print('Native diagnostics passed. Docker ODK and desktop acceptance remain separate.')
