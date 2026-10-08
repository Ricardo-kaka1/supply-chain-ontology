"""Closed-world MVP data gates, separate from OWL/HermiT reasoning."""
import json
from datetime import date
from pathlib import Path
from decimal import Decimal
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
S=Namespace("https://example.org/cabot-audit/ontology/")
E=Namespace("urn:example:cabot-audit:")
D=URIRef("http://purl.obolibrary.org/obo/IAO_0000115")

def load(root, demo=False):
    root=Path(root); g=Graph()
    g.parse(root/"src/ontology/scaudit-edit.owl")
    g.parse(root/"src/ontology/imports/metadata.owl")
    if demo: g.parse(root/"examples/owl/cabot-demo.owl")
    return g

def metadata_errors(g, mappings=None, formal=False):
    errors=[]
    types=(OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.NamedIndividual)
    for term in set(s for t in types for s in g.subjects(RDF.type,t)):
        if not isinstance(term,URIRef): continue
        if str(term).startswith(str(S)):
            if not any(str(x).strip() for x in g.objects(term,D)): errors.append(f"definition:{term}")
            for lang in ("en","zh"):
                if not any(x.language==lang and str(x).strip() for x in g.objects(term,RDFS.label)):
                    errors.append(f"label-{lang}:{term}")
        elif not str(term).startswith(("http://www.w3.org/", "http://purl.org/", "http://purl.obolibrary.org/", str(E))):
            errors.append(f"namespace:{term}")
    for triple in g:
        if triple[1] in (OWL.versionIRI, OWL.imports, RDFS.isDefinedBy): continue
        for term in (triple[1],triple[2]):
            if isinstance(term,URIRef) and str(term).startswith(str(S)) and not any(g.triples((term,RDF.type,None))):
                errors.append(f"unknown-reference:{term}")
    for row in (mappings or {}).get("mappings",[]):
        if not any(g.triples((URIRef(row["term"]),RDF.type,None))): errors.append("mapping:"+row["term"])
    if formal and any(str(s).startswith(str(S)) for s in g.subjects()):
        errors.append("formal-release:temporary-namespace")
    return sorted(set(errors))

def data_errors(g):
    errors=[]
    required={
      S.SupplierAccount:[S.accountSupplier,S.accountBuyer],
      S.RecordObservation:[S.recordInDataset,S.observationForAccount,S.observationAboutDocument,S.sourceRecordId,S.sourceRow],
      S.SourceDataset:[S.datasetFromSystem,S.sourceFile,S.inputHash,S.snapshotTime,S.isCompleteSnapshot],
      S.SupplierStatementLine:[S.lineOfStatement,S.recordInDataset,S.observationForAccount,S.observationAboutDocument,S.sourceRecordId,S.sourceRow,S.currencyCode,S.observedGrossAmount],
      S.InternalAPRecord:[S.recordInDataset,S.observationForAccount,S.observationAboutDocument,S.sourceRecordId,S.sourceRow,S.currencyCode,S.observedGrossAmount],
      S.ReconciliationRun:[S.runHasScope,S.runId,S.runUsesDataset],
      S.ReconciliationScope:[S.scopeForAccount,S.currencyCode,S.cutoffTime],
      S.RuleEvaluation:[S.evaluationUsesRule,S.evaluationInRun,S.hasCheckOutcome,S.evaluationUsesObservation],
      S.AuditFinding:[S.findingFromEvaluation,S.hasFindingType,S.hasFindingStatus,S.findingFingerprint],
      S.FindingInterpretation:[S.interpretationOf,S.interpretationEvidence,S.interpretationText],
      S.ReviewDecision:[S.reviewedFinding,S.hasReviewDisposition,S.reviewerId,S.reviewTime],
      S.BalanceSnapshot:[S.snapshotForScope,S.snapshotFromDataset,S.snapshotTime,S.currencyCode,S.normalizedNetPayableAmount,S.snapshotUsesObservation],
      S.CreditAllocation:[S.allocationCredit,S.allocationToInvoice,S.allocationAmount,S.allocationDate,S.currencyCode],
      S.PaymentAllocation:[S.allocationPayment,S.allocationToInvoice,S.allocationAmount,S.allocationDate,S.currencyCode]}
    multivalued={S.runUsesDataset,S.evaluationUsesObservation,S.interpretationEvidence,S.snapshotUsesObservation}
    for cls,props in required.items():
        for node in g.subjects(RDF.type,cls):
            for prop in props:
                vals=list(g.objects(node,prop))
                if not vals or (prop not in multivalued and len(vals)!=1): errors.append(f"cardinality:{node}:{prop}")
                for v in vals:
                    if isinstance(v,URIRef):
                        rng=g.value(prop,RDFS.range)
                        if rng and not any((v,RDF.type,c) in g for c in g.transitive_subjects(RDFS.subClassOf,rng)):
                            errors.append(f"range:{node}:{prop}:{v}")
    for prop in g.subjects(RDFS.range,XSD.decimal):
        for node,value in g.subject_objects(prop):
            if not isinstance(value,Literal) or value.datatype!=XSD.decimal:
                errors.append(f"decimal:{node}:{prop}");continue
            try:
                if not Decimal(str(value)).is_finite(): raise ValueError()
            except Exception: errors.append(f"decimal:{node}:{prop}")
            if not g.value(node,S.currencyCode): errors.append(f"currency:{node}:{prop}")
    for node,value in g.subject_objects(S.currencyCode):
        if len(str(value))!=3 or not str(value).isascii() or not str(value).isupper(): errors.append(f"currency-code:{node}")
    for prop in (S.invoiceDate,S.paymentDate,S.allocationDate):
        for node,value in g.subject_objects(prop):
            try:
                if date.fromisoformat(str(value)).isoformat()!=str(value):raise ValueError()
            except ValueError:errors.append(f"date:{node}:{prop}")
    for cls in (S.CreditAllocation,S.PaymentAllocation):
        for node in g.subjects(RDF.type,cls):
            amount=g.value(node,S.allocationAmount)
            if amount and Decimal(str(amount))<0: errors.append(f"negative-allocation:{node}")
    for node in set(g.subjects()):
        if str(node).startswith(str(E)) and (node,RDF.type,OWL.Ontology) not in g and g.value(node,S.isSynthetic)!=Literal(True): errors.append(f"synthetic:{node}")
    return sorted(set(errors))

def validate(root, formal=False):
    root=Path(root)
    return metadata_errors(load(root),json.loads((root/"config/term-mappings.json").read_text()),formal)+data_errors(load(root,True))
