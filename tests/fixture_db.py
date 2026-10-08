"""TEST ONLY: named-triple fixture using SemSQL's official SQL schema.

This deliberately does not implement rdftab or relation-graph. It cannot verify
production OWL->SemSQL conversion, anonymous OWL restrictions or reasoning.
Never publish this database as a release artifact.
"""
import sqlite3
from pathlib import Path
import semsql
from rdflib import URIRef,Literal
def create_fixture(graph,path,prefixes):
    schema=Path(semsql.__file__).parent/"builder/sql_schema/semsql.sql"
    def short(value):
        for prefix,base in sorted(prefixes.items(),key=lambda x:-len(x[1])):
            if str(value).startswith(base):return prefix+":"+str(value)[len(base):]
        return str(value)
    con=sqlite3.connect(path);con.executescript(schema.read_text())
    con.executemany("insert into prefix values (?,?)",prefixes.items())
    rows=[]
    for s,p,o in graph:
        if not isinstance(s,URIRef) or not isinstance(o,(URIRef,Literal)):continue
        rows.append((short(s),short(p),short(o) if isinstance(o,URIRef) else None,
                     str(o) if isinstance(o,Literal) else None,
                     short(o.datatype) if isinstance(o,Literal) and o.datatype else None,
                     o.language if isinstance(o,Literal) else None))
    con.executemany("insert into statements (subject,predicate,object,value,datatype,language) values (?,?,?,?,?,?)",rows)
    con.commit();con.close()
