"""OAK 0.6.23 SqlImplementation with explicit SemSQL backend and prefix handling.

Relationships are named-node assertions/restrictions supported by OAK, not a
lossless OWL axiom export. Use the release OWL for anonymous axioms.
"""
from pathlib import Path
from oaklib.resource import OntologyResource
from oaklib.implementations.sqldb.sql_implementation import SqlImplementation
from semsql.sqla.semsql import Statements

class OntologyAdapter:
    def __init__(self, database):
        path = Path(database).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        self.oak = SqlImplementation(OntologyResource(slug=str(path), scheme="sqlite"))
        self.prefixes = self.oak.prefix_map()
        if self.prefixes.get("sca") != "https://example.org/cabot-audit/ontology/":
            raise ValueError("Missing or unexpected sca prefix; rebuild with config/prefixes.csv")
        versions = self.values("sca:scaudit.owl", "owl:versionInfo")
        if not versions:
            versions = self.values("ex:demo.owl", "owl:versionInfo")
        if len(versions) != 1:
            raise ValueError("Expected one ontology version on the core or demo ontology")
        self.version = versions[0]["value"]

    def close(self):
        self.oak.session.close()
        self.oak.session.bind.dispose()

    def curie(self, identifier):
        for prefix, base in sorted(self.prefixes.items(), key=lambda x: -len(x[1])):
            if identifier.startswith(base):
                return prefix + ":" + identifier[len(base):]
        return identifier

    def iri(self, identifier):
        prefix, sep, local = identifier.partition(":")
        return self.prefixes[prefix] + local if sep and prefix in self.prefixes else identifier

    def values(self, identifier, predicate):
        # The OAK SemSQL session exposes language/datatype without flattening them.
        rows = self.oak.session.query(Statements).filter(
            Statements.subject == self.curie(identifier),
            Statements.predicate == self.curie(predicate)).all()
        return sorted([{"value": r.value, "object": self.iri(r.object) if r.object else None,
                        "language": r.language, "datatype": r.datatype} for r in rows],
                      key=lambda r: str(r))

    def validate_term_reference(self, identifier):
        return bool(self.oak.node_exists(self.curie(identifier)))

    def get_label(self, identifier, language="en"):
        if not self.validate_term_reference(identifier):
            return None
        # Avoid OAK's implicit default-language fallback for an explicit language.
        labels = list(self.oak.multilingual_labels([self.curie(identifier)],
                      langs=[language], allow_none=False))
        return sorted(x[1] for x in labels if x[1] and x[2] == language)[0] if any(
            x[1] and x[2] == language for x in labels) else None

    def get_definition(self, identifier):
        return self.oak.definition(self.curie(identifier)) if self.validate_term_reference(identifier) else None

    def get_term(self, identifier):
        curie = self.curie(identifier)
        found = self.validate_term_reference(curie)
        return {"found": found, "id": curie, "iri": self.iri(curie),
                "labels": {lang: self.get_label(curie, lang) for lang in ("en", "zh")} if found else {},
                "definition": self.get_definition(curie) if found else None,
                "ontology_version": self.version,
                "deprecated": any(x["value"] in ("true", "1") for x in self.values(curie, "owl:deprecated")) if found else None}

    def get_relationships(self, identifier):
        if not self.validate_term_reference(identifier):
            return []
        return [{"subject": self.iri(s), "predicate": self.iri(p), "object": self.iri(o)}
                for s,p,o in sorted(set(self.oak.relationships(subjects=[self.curie(identifier)])))]

    def get_ancestors(self, identifier):
        # Traverse only OAK's named rdfs:subClassOf edges; no part-of/type traversal.
        start = self.curie(identifier)
        seen, pending = set(), [start] if self.validate_term_reference(start) else []
        while pending:
            node = pending.pop()
            for _,_,parent in self.oak.relationships(subjects=[node],
                    predicates=["rdfs:subClassOf"], include_abox=False):
                if parent != start and parent not in seen and not parent.startswith("_:"):
                    seen.add(parent); pending.append(parent)
        return sorted(self.iri(x) for x in seen)

    def search_terms(self, text, language="en"):
        if not text.strip():
            return []
        results = []
        for term in sorted(t for t in self.oak.entities() if t and t.startswith("sca:")):
            aliases = self.values(term, "rdfs:label") + self.values(term, "skos:altLabel")
            matches = [a["value"] for a in aliases if a["language"] == language
                       and a["value"] and text.casefold() in a["value"].casefold()]
            if matches:
                results.append({**self.get_term(term), "matched_labels": matches,
                                "identity_decision": "candidate_only"})
        return results
