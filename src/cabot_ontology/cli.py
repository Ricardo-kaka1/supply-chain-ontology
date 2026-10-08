import argparse, json, sys
from .adapter import OntologyAdapter
def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description="OAK/SemSQL semantic access; synthetic demo only")
    p.add_argument("database");p.add_argument("command",choices=["search","term","ancestors","relationships","evidence"])
    p.add_argument("identifier");p.add_argument("--language",default="en")
    a=p.parse_args();adapter=OntologyAdapter(a.database)
    try:
        if a.command=="search": result=adapter.search_terms(a.identifier,a.language)
        elif a.command=="term": result=adapter.get_term(a.identifier)
        elif a.command=="ancestors": result=adapter.get_ancestors(a.identifier)
        elif a.command=="relationships": result=adapter.get_relationships(a.identifier)
        else:
            nodes=[a.identifier];seen=set();result=[]
            for subject,_,_ in adapter.oak.relationships(objects=[adapter.curie(a.identifier)],
                    predicates=['sca:interpretationOf','sca:reviewedFinding']):
                nodes.append(adapter.iri(subject))
            follow={"findingFromEvaluation","evaluationInRun","evaluationUsesRule","evaluationUsesObservation","recordInDataset","interpretationOf","interpretationEvidence"}
            while nodes:
                node=nodes.pop()
                if node in seen: continue
                seen.add(node)
                rels=adapter.get_relationships(node)
                fields=('observedGrossAmount','observedPaidAmount','observedOutstandingAmount',
                        'signedVarianceAmount','currencyCode','sourceFile','sourceRow','inputHash',
                        'interpretationText','modelId','promptVersion','reviewerId','reviewTime')
                values={field:adapter.values(node,'sca:'+field) for field in fields}
                result.append({"node":adapter.get_term(node),"relationships":rels,
                               "values":{k:v for k,v in values.items() if v}})
                nodes.extend(r["object"] for r in rels if r["predicate"].rsplit("/",1)[-1] in follow)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    finally: adapter.close()
if __name__=="__main__":main()
