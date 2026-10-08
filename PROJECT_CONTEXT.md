# PROJECT_CONTEXT.md

> **Project:** Supply Chain Ontology + AI Agent Platform  
> **Primary stack:** Protégé + ODK + ROBOT + OAK (Ontology Access Kit) + SemSQL/SQLite  
> **Purpose of this file:** Give Codex enough project context to understand the architecture, conventions, responsibilities, and next implementation steps before modifying the repository.

---

## 0. Instructions for Codex

Read this file before making architectural changes.

This project is not simply a chatbot or a standalone ontology. The target is a **governed supply-chain semantic layer** that can be consumed by an AI Agent together with enterprise data sources such as a graph database, data warehouse, and contract documents.

When working in this repository:

1. Treat the OWL ontology as the **semantic source of truth** for domain concepts, relationships, constraints, identifiers, and definitions.
2. Do not put large volumes of transactional business data directly into the ontology unless there is a clear reason.
3. Keep ontology engineering, ontology runtime access, and business-data integration as separate layers.
4. Prefer reproducible pipelines over manual transformations.
5. Preserve stable IRIs/CURIEs once published.
6. Use Git for version control and review ontology changes through pull requests where possible.
7. Use ODK/ROBOT workflows for validation, quality control, reasoning, imports, and releases rather than inventing parallel ontology build logic.
8. Use OAK / `oaklib` as the preferred programmatic ontology-access layer.
9. Use SemSQL/SQLite as a practical query/runtime representation where relational querying and local performance are useful.
10. Before executing version-sensitive commands, inspect the repository configuration and installed tool versions. Commands in this document describe the intended workflow and may need small version-specific adjustments.
11. Never confuse **OAK = Ontology Access Kit** with unrelated tools/projects named “Oak”.
12. Do not silently redesign the ontology namespace, repository layout, or release process. Propose major changes first.

---

# 1. Business Background

The company is a **supply-chain transformation and procurement consulting company**.

The broader goal is to build an internal **AI Agent / digital intelligence platform** that can understand supply-chain and procurement concepts consistently across:

- structured enterprise databases,
- graph databases,
- data warehouses,
- supplier master data,
- contracts and other unstructured documents,
- analytical applications,
- and natural-language Agent interactions.

A central problem is semantic inconsistency.

For example, different systems may use different names or structures for concepts such as:

- Supplier
- Vendor
- Contract
- Purchase Order
- Material
- Category
- Commodity
- Business Unit
- Site
- Spend
- Payment Term
- Risk
- Lead Time
- Delivery
- Invoice
- Procurement Event

The ontology provides a machine-readable semantic layer so that applications and Agents can reason about these concepts consistently.

---

# 2. Target Outcome

The intended platform should eventually support a user asking questions such as:

> Which strategic suppliers have contracts expiring in the next six months?

> Which suppliers in category X have both high spend and elevated supply risk?

> Show all contracts associated with suppliers belonging to the same parent organization.

> What does “preferred supplier” mean in our internal procurement model?

> Find suppliers that are subclasses or instances of a specific sourcing category.

> Which contractual clauses are associated with termination risk?

The Agent should not rely only on vector similarity or LLM memory.

Instead, it should combine:

1. **Ontology semantics**
2. **Structured enterprise data**
3. **Graph relationships**
4. **Document retrieval**
5. **LLM reasoning/tool orchestration**

---

# 3. High-Level Architecture

```text
                         ┌─────────────────────────┐
                         │       Business User     │
                         └────────────┬────────────┘
                                      │ Natural language
                                      ▼
                         ┌─────────────────────────┐
                         │        AI Agent         │
                         │  planning + tool use    │
                         └───────┬───────┬─────────┘
                                 │       │
                    ontology     │       │ business retrieval
                    semantics    │       │
                                 ▼       ▼
                  ┌──────────────────┐   ┌─────────────────────────┐
                  │ Ontology Service │   │ Enterprise Data Layer   │
                  │ OAK / oaklib     │   │                         │
                  │ + SemSQL/SQLite  │   │ Graph DB                │
                  └────────┬─────────┘   │ Data Warehouse          │
                           │             │ Contract Documents      │
                           │             │ APIs / Master Data      │
                           │             └────────────┬────────────┘
                           │                          │
                           └────────────┬─────────────┘
                                        ▼
                              semantic reconciliation
                                        │
                                        ▼
                              final Agent response
```

The ontology is the **semantic control plane**.

The data warehouse remains the main location for analytical facts and measures.

The graph database may store large-scale operational relationships or materialized business knowledge.

The document store / search system remains responsible for contract text and other unstructured evidence.

---

# 4. Core Technology Responsibilities

## 4.1 Protégé

**Role:** ontology authoring and interactive inspection.

Use Protégé to:

- create/edit OWL classes;
- define object properties;
- define data properties;
- add labels and definitions;
- create class hierarchies;
- inspect logical axioms;
- add selected individuals where appropriate;
- review ontology modules;
- run supported reasoners interactively when useful.

Examples:

```text
Class:
  Supplier

Class:
  Contract

ObjectProperty:
  hasSupplier

Domain:
  Contract

Range:
  Supplier
```

Protégé is primarily the **human ontology modeling interface**.

It should not be the only place where project governance happens.

Ontology files must live in Git.

---

## 4.2 Git

**Role:** version control and collaboration.

Git should track:

- ontology source files;
- templates;
- import configuration;
- SPARQL quality-control queries;
- ROBOT/ODK configuration;
- scripts;
- documentation;
- tests;
- release metadata.

Recommended development flow:

```text
feature branch
    ↓
edit ontology / templates
    ↓
run QC
    ↓
review diff
    ↓
pull request
    ↓
CI
    ↓
merge
    ↓
release
```

For ontology projects, version control is especially important because semantic changes can affect downstream systems even when file-level changes appear small.

---

## 4.3 ODK — Ontology Development Kit

**Role:** ontology repository lifecycle management.

ODK should be considered the **engineering framework around the ontology**.

It provides a reproducible project structure and workflows for tasks such as:

- repository initialization;
- imports;
- quality control;
- automated release workflows;
- ontology builds;
- continuous integration;
- packaging ontology engineering tools;
- maintaining reproducible environments.

ODK is not a replacement for Protégé.

A simplified division is:

```text
Protégé = model the ontology
ODK     = engineer and govern the ontology project
```

ODK makes heavy use of automation and typically integrates tools such as ROBOT.

Prefer stable ODK releases for the project unless there is a specific requirement for development snapshots.

---

## 4.4 ROBOT

**Role:** command-line ontology automation.

ROBOT is a major execution engine used in ontology engineering workflows.

Typical uses include:

- `report` — quality-control checks;
- `reason` — automated reasoning/classification;
- `merge` — combine ontologies/imports/modules;
- `convert` — serialization conversion;
- `query` — SPARQL queries;
- filtering;
- annotation;
- extraction;
- release assembly.

Conceptually:

```text
source ontology
      │
      ├── ROBOT report  → QC report
      │
      ├── ROBOT merge   → assembled ontology
      │
      ├── ROBOT reason  → inferred ontology
      │
      └── ROBOT convert → normalized release format
```

A release should fail when serious ontology QC errors occur.

Do not create a second custom validation framework if ROBOT/SPARQL/ODK can express the requirement cleanly.

---

## 4.5 OAK — Ontology Access Kit

**Important:** In this project, **OAK means Ontology Access Kit**.

Python package:

```text
oaklib
```

CLI:

```text
runoak
```

**Role:** provide a common programmatic API over ontology resources and different ontology backends.

OAK should be used by the application/Agent layer to perform ontology operations such as:

- search concepts;
- retrieve labels;
- resolve identifiers;
- inspect ancestors;
- inspect descendants;
- traverse relationships;
- retrieve definitions;
- inspect mappings;
- work with ontology backends;
- query an ontology without forcing the application to understand raw OWL serialization.

Conceptually:

```python
Agent
  ↓
Ontology tool
  ↓
OAK / oaklib
  ↓
OWL / SemSQL / other supported ontology backend
```

The Agent should call a controlled ontology-service interface rather than generating arbitrary ontology queries whenever possible.

---

## 4.6 SemSQL

**Role:** relational SQL representation/access layer for RDF/OWL ontology content.

SemSQL provides SQL tables/views that make ontology information queryable using SQL.

This is useful because:

- SQLite is lightweight;
- SQL is familiar;
- ontology lookups can be fast;
- downstream applications can use relational tooling;
- complex joins can sometimes be easier in SQL;
- OAK can work with SemSQL-backed ontology resources.

Important conceptual distinction:

```text
OWL
= ontology semantic representation

SemSQL
= SQL schema/views for accessing ontology statements

SQLite
= database engine/file used to store/query a SemSQL build
```

These are related but not the same thing.

---

## 4.7 SQLite

SQLite is the database engine used for the local relational ontology representation.

Expected artifact:

```text
db/supply-chain.db
```

This database is **not** intended to replace the enterprise data warehouse.

It is primarily a convenient ontology runtime/query artifact.

Possible use:

```sql
SELECT ...
FROM ...
WHERE ...
```

for ontology-derived labels, edges, statements, mappings, or other semantic structures.

---

# 5. Core Ontology Concepts

## 5.1 TBox

**TBox = Terminological Box**

This is the ontology **schema / conceptual model**.

It defines what kinds of things exist and how they relate.

Examples:

```text
Supplier
Contract
PurchaseOrder
Material
Category
Risk

Contract hasSupplier Supplier
Supplier belongsToCategory Category
PurchaseOrder ordersMaterial Material
```

Think:

> TBox = the grammar / structure of the domain.

---

## 5.2 ABox

**ABox = Assertional Box**

This contains facts about concrete entities/individuals.

Example:

```text
supplier:SUP_001 rdf:type scp:Supplier
contract:CTR_001 rdf:type scp:Contract
contract:CTR_001 scp:hasSupplier supplier:SUP_001
```

Think:

> ABox = actual facts expressed using the TBox vocabulary.

For this enterprise project, do **not automatically place every operational record into OWL ABox**.

Large transactional datasets are usually better kept in operational databases, graph databases, or warehouses and semantically mapped to ontology identifiers.

---

## 5.3 IRI

**IRI = Internationalized Resource Identifier**

An IRI is the globally unique machine identifier for an ontology entity.

Example:

```text
https://example.company/ontology/supply-chain/Supplier
```

Labels can change.

IRIs should usually remain stable.

For example:

```text
IRI:
https://example.company/ontology/supply-chain/Supplier

English label:
Supplier

Chinese label:
供应商
```

Changing the label does not need to change the IRI.

---

## 5.4 CURIE

**CURIE = Compact URI Expression**

A CURIE is a shortened representation of an IRI.

Example:

```text
Prefix:
scp: https://example.company/ontology/supply-chain/

CURIE:
scp:Supplier

Expanded IRI:
https://example.company/ontology/supply-chain/Supplier
```

CURIEs improve readability in code, data mappings, documentation, and SPARQL.

---

# 6. Proposed Supply-Chain Ontology Scope

The initial ontology should be small enough to govern properly.

Do not attempt to model the entire supply-chain universe in version 1.

Suggested core modules:

## 6.1 Organization

```text
Organization
Supplier
Customer
BusinessUnit
LegalEntity
Site
ParentOrganization
```

Possible relationships:

```text
hasParentOrganization
hasSite
belongsToBusinessUnit
```

---

## 6.2 Procurement

```text
Procurement
SourcingEvent
PurchaseOrder
PurchaseOrderLine
Category
Commodity
Material
Service
Buyer
```

Possible relationships:

```text
ordersMaterial
belongsToCategory
purchasedFrom
managedByBuyer
```

---

## 6.3 Contract

```text
Contract
ContractClause
PaymentTerm
TerminationClause
RenewalClause
EffectiveDate
ExpirationDate
```

Possible relationships:

```text
hasSupplier
hasClause
hasPaymentTerm
governsPurchase
```

---

## 6.4 Risk

```text
Risk
SupplierRisk
FinancialRisk
GeopoliticalRisk
OperationalRisk
ComplianceRisk
```

Possible relationships:

```text
hasRisk
affectsSupplier
affectsCategory
hasRiskLevel
```

---

## 6.5 Logistics / Operations

Possible later concepts:

```text
Shipment
Warehouse
Inventory
LeadTime
Delivery
Carrier
Route
```

Do not expand this module until concrete business use cases require it.

---

# 7. Ontology Modeling Principles

## 7.1 Start from competency questions

Before creating classes, define questions the ontology needs to answer.

Example:

> Which contracts involve a supplier?

This implies concepts/relations such as:

```text
Contract
Supplier
hasSupplier
```

Another:

> Which suppliers belong to an indirect procurement category?

This may require:

```text
Supplier
Category
belongsToCategory
subcategory hierarchy
```

Modeling should follow business questions rather than abstract taxonomy-building for its own sake.

---

## 7.2 Separate concepts from database fields

A database column is not automatically an ontology property.

Example:

```text
supplier_table.supplier_name
```

is a system field.

Ontology concept:

```text
scp:Supplier
rdfs:label
```

The ontology describes meaning.

The data model describes storage.

Mapping connects them.

---

## 7.3 Reuse before reinventing

Before inventing generic concepts, investigate whether a suitable external vocabulary exists.

However:

- do not import huge external ontologies unnecessarily;
- import only what is useful;
- preserve internal business concepts when they have company-specific meaning.

---

## 7.4 Keep identifiers stable

Avoid identifiers like:

```text
scp:GoodSupplier
```

if the term may later be renamed.

Prefer stable semantic/entity IDs or controlled names.

Once downstream systems reference a published identifier, changing it can create breaking changes.

---

## 7.5 Labels are not identifiers

Example:

```text
scp:Supplier
    rdfs:label "Supplier"@en
    rdfs:label "供应商"@zh
```

A multilingual label strategy should not alter the underlying identifier.

---

# 8. Authoring → Governance → Runtime Pipeline

The intended end-to-end workflow is:

```text
1. Business requirements / competency questions
                  ↓
2. Ontology modeling in Protégé
                  ↓
3. Save OWL source in Git repository
                  ↓
4. ODK-managed build environment
                  ↓
5. ROBOT validation / report / reason / merge
                  ↓
6. CI quality gate
                  ↓
7. Versioned OWL release
                  ↓
8. Build/query-friendly SemSQL SQLite artifact
                  ↓
9. OAK ontology-access layer
                  ↓
10. Agent ontology tools
                  ↓
11. Combine ontology semantics with enterprise data/document tools
```

---

# 9. OWL → SemSQL/SQLite Flow

The target flow is:

```text
supply-chain.owl
      ↓
normalize/validate serialization if needed
      ↓
SemSQL build process
      ↓
supply-chain.db
      ↓
OAK / SQL queries
```

SemSQL currently expects an RDF/OWL representation suitable for its build process; the exact build command and dependencies should be verified against the installed version.

ROBOT can be used for format normalization when required.

The generated SQLite file should be treated as a **build artifact**, not manually edited.

Source of truth:

```text
OWL source
```

Derived artifact:

```text
SQLite / SemSQL database
```

Never make ontology changes only inside the SQLite file.

---

# 10. Versioning and Release Governance

Recommended semantic versioning pattern:

```text
v0.1.0
v0.2.0
v1.0.0
v1.1.0
v2.0.0
```

Suggested interpretation:

```text
PATCH
- label typo
- annotation correction
- non-breaking metadata fix

MINOR
- new class
- new property
- compatible extension

MAJOR
- breaking semantic change
- identifier change
- removed published concept
- incompatible restructuring
```

Before release:

```text
ontology source
      ↓
QC checks
      ↓
reasoning / consistency validation
      ↓
import validation
      ↓
review
      ↓
build release artifacts
      ↓
tag version
```

Example target:

```text
v1.0.0 passes QC before release.
```

---

# 11. Quality-Control Strategy

QC should include at least:

## Structural checks

- missing labels;
- duplicate labels where prohibited;
- missing definitions for important business concepts;
- invalid identifiers;
- unexpected namespaces;
- malformed mappings.

## Logical checks

- unsatisfiable classes;
- inconsistent axioms;
- incorrect domain/range interactions;
- unintended equivalent classes.

## Governance checks

- prohibited identifier changes;
- missing release metadata;
- import failures;
- incorrect ontology version IRI;
- unintended deprecated-term reuse.

## Business checks

Possible custom SPARQL rules:

- every Contract class/instance used operationally must map to an approved contract type;
- every Supplier category mapping must resolve to a valid category;
- deprecated procurement terms may not be introduced in new mappings;
- certain high-value concepts must have Chinese and English labels.

Custom business checks can live in:

```text
src/ontology/sparql/
```

or the equivalent ODK-generated QC directory.

---

# 12. Proposed Repository Structure

Codex should **prefer the actual ODK-generated structure** if the repository is initialized by ODK.

The following is the conceptual repository layout, not a requirement to overwrite ODK conventions:

```text
supply-chain-ontology/
│
├── PROJECT_CONTEXT.md
├── README.md
├── .gitignore
├── .env.example
├── pyproject.toml
│
├── src/
│   │
│   ├── ontology/
│   │   ├── supply-chain-edit.owl
│   │   ├── imports/
│   │   ├── modules/
│   │   ├── templates/
│   │   ├── sparql/
│   │   ├── reports/
│   │   ├── Makefile
│   │   └── ... ODK-generated files
│   │
│   └── app/
│       ├── ontology_service/
│       │   ├── __init__.py
│       │   ├── adapter.py
│       │   ├── search.py
│       │   ├── traversal.py
│       │   └── identifiers.py
│       │
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── tools.py
│       │   ├── router.py
│       │   └── prompts.py
│       │
│       └── connectors/
│           ├── graph_db.py
│           ├── warehouse.py
│           └── contracts.py
│
├── db/
│   └── .gitkeep
│
├── scripts/
│   ├── qc.sh
│   ├── build_ontology.sh
│   ├── build_semsql.sh
│   └── release.sh
│
├── mappings/
│   ├── warehouse/
│   ├── contracts/
│   └── graph/
│
├── tests/
│   ├── ontology/
│   ├── ontology_service/
│   ├── agent/
│   └── integration/
│
├── docs/
│   ├── architecture.md
│   ├── ontology-model.md
│   ├── mappings.md
│   └── release-process.md
│
└── releases/
    └── README.md
```

Do not commit secrets or production credentials.

Whether generated SQLite databases belong in Git should be decided based on size and release policy. In many cases, they should be CI/release artifacts instead.

---

# 13. Ontology Service Boundary

The AI Agent should not need to know how OWL is serialized.

Create a service/API boundary around OAK.

Suggested internal functions:

```python
search_concepts(text)
get_label(curie)
get_definition(curie)
get_entity(curie)
get_ancestors(curie)
get_descendants(curie)
get_relationships(curie)
get_mappings(curie)
resolve_identifier(text)
validate_curie(curie)
```

Later:

```python
find_path(source_curie, target_curie)
get_property_values(curie, property_curie)
get_related_entities(curie, relation_curie)
```

The Agent receives structured results.

Example:

```json
{
  "id": "scp:Supplier",
  "label": "Supplier",
  "definition": "...",
  "parents": ["scp:Organization"]
}
```

This makes Agent behavior easier to test and prevents coupling prompts directly to ontology storage details.

---

# 14. Agent Integration Pattern

The Agent should have multiple specialized tools.

Example conceptual toolset:

```text
ontology.search
ontology.get_entity
ontology.get_relationships

warehouse.query
graph.query
contracts.search
contracts.get_document
```

Example question:

> Which strategic suppliers have contracts expiring within six months?

Possible Agent plan:

```text
1. ontology.search("strategic supplier")
       ↓
2. resolve the approved ontology concept
       ↓
3. identify semantic mappings to supplier/category fields
       ↓
4. warehouse.query(...)
       ↓
5. retrieve relevant contract records
       ↓
6. contracts.search(...) if clause-level evidence is needed
       ↓
7. synthesize response
```

The LLM plans.

Tools retrieve facts.

The ontology constrains/clarifies meaning.

---

# 15. Graph Database Integration

A graph database may be useful for large connected business datasets such as:

```text
Supplier
  ├── supplies → Material
  ├── signs → Contract
  ├── locatedIn → Country
  ├── belongsTo → ParentCompany
  └── exposedTo → Risk
```

Possible graph:

```text
Supplier A
   │
   ├── supplies → Material M1
   │
   ├── hasContract → Contract C001
   │
   └── locatedIn → Region R1
                         │
                         └── exposedTo → Risk X
```

Important:

**Ontology ≠ graph database.**

The ontology defines semantic meaning and schema.

The graph database can materialize large numbers of business entities/relationships.

The two should be linked through stable identifiers and mappings.

---

# 16. Data Warehouse Integration

The warehouse should remain responsible for quantitative and analytical data such as:

```text
supplier_id
spend
purchase_order_count
on_time_delivery_rate
defect_rate
invoice_amount
currency
period
category_id
business_unit_id
```

The ontology should explain concepts such as:

```text
Supplier
Spend
Category
BusinessUnit
```

Mappings connect ontology concepts to warehouse models.

Example conceptual mapping:

```yaml
ontology_entity: scp:Supplier
warehouse_table: dim_supplier
key_column: supplier_id
label_column: supplier_name
```

The exact mapping format can be designed later.

Do not hard-code semantic mappings only inside prompts.

Store them as explicit configuration where possible.

---

# 17. Contract Document Integration

Contracts are unstructured/semi-structured evidence.

A document pipeline might include:

```text
PDF/DOCX contract
      ↓
text extraction
      ↓
document metadata
      ↓
chunking
      ↓
embedding / keyword index
      ↓
clause extraction
      ↓
link extracted concepts to ontology identifiers
```

Example:

```text
"termination for convenience"
      ↓
mapped to
scp:TerminationClause
```

The contract system may store:

```text
document_id
supplier_id
contract_id
effective_date
expiration_date
clause_type
chunk_id
text
ontology_curie
```

The Agent can then combine semantic reasoning with textual evidence.

---

# 18. Why Not Put Everything Into One Database?

Avoid creating one giant system that mixes:

- ontology schema;
- raw contracts;
- transaction records;
- analytics;
- embeddings;
- graph edges;
- Agent memory.

Different systems solve different problems.

Recommended division:

| Layer | Primary responsibility |
|---|---|
| OWL ontology | semantic model / meaning |
| Protégé | human ontology authoring |
| ODK | ontology lifecycle engineering |
| ROBOT | ontology automation / QC / reasoning |
| SemSQL + SQLite | relational ontology query representation |
| OAK | ontology access API |
| Graph DB | connected operational/business relationships |
| Data warehouse | analytical structured facts |
| Document/RAG store | contract/document evidence |
| LLM Agent | orchestration, reasoning, tool selection |

---

# 19. Required Software

## Core

- Git
- GitHub or another Git hosting service
- Docker
- Protégé
- Python 3
- Java (when required by ontology tooling such as ROBOT)
- ODK
- ROBOT
- OAK / `oaklib`
- SemSQL
- SQLite

## Likely later

- graph database, e.g. Neo4j or enterprise equivalent;
- warehouse connector;
- document parser;
- vector/search engine;
- Agent framework;
- CI/CD environment;
- secrets management.

Do not choose a graph database or Agent framework purely because it is popular. Choose based on actual enterprise constraints and existing infrastructure.

---

# 20. Required Skills

The project combines several skill groups.

## Ontology engineering

- OWL
- RDF
- RDFS
- ontology modeling
- classes/properties/axioms
- TBox/ABox
- IRI/CURIE
- SPARQL
- reasoning
- ontology imports
- mappings

## Software engineering

- Git
- pull requests
- Python
- CLI tools
- Docker
- testing
- CI/CD
- configuration management

## Data engineering

- SQL
- SQLite
- warehouse modeling
- ETL/ELT concepts
- identifiers
- data mapping
- data quality

## AI Agent engineering

- tool calling
- retrieval
- structured outputs
- prompt/tool boundary design
- Agent evaluation
- hallucination control
- RAG
- semantic grounding

## Business domain

- procurement
- sourcing
- suppliers
- contracts
- categories
- spend analysis
- supply risk
- purchasing processes

---

# 21. Required Business Resources

Technology alone is insufficient.

The project requires access to business/domain resources such as:

- procurement glossary;
- supplier master-data dictionary;
- contract taxonomy;
- category taxonomy;
- procurement process documentation;
- ERP field definitions;
- warehouse schema/data dictionary;
- representative contract samples;
- supplier/category mappings;
- risk definitions;
- subject-matter experts;
- example business questions.

A strong ontology requires agreement on domain meaning.

---

# 22. Suggested Development Phases

## Phase 0 — Environment

Deliverables:

- Git repository
- Docker working
- Protégé installed
- Python environment
- basic CI
- PROJECT_CONTEXT.md
- README

---

## Phase 1 — Ontology MVP

Model a deliberately small domain:

```text
Supplier
Contract
Category
Material
PurchaseOrder
Risk
```

and approximately 10–20 important relationships.

Deliverables:

- initial OWL ontology;
- namespace/prefix policy;
- naming convention;
- competency questions;
- definitions;
- labels.

---

## Phase 2 — ODK + ROBOT Governance

Deliverables:

- ODK-managed repository;
- automated QC;
- ROBOT reports;
- reasoning checks;
- import workflow;
- CI;
- release process.

Success criterion:

```text
v0.x release can be generated reproducibly from Git.
```

---

## Phase 3 — SemSQL Runtime Artifact

Deliverables:

```text
supply-chain.owl
      ↓
supply-chain.db
```

Tests should verify that important ontology entities can be found in the SQLite/SemSQL representation.

---

## Phase 4 — OAK Ontology Service

Build a small Python interface.

Minimum operations:

```text
search
label
definition
ancestors
descendants
relationships
identifier resolution
```

Deliverables:

- Python service;
- tests;
- clear structured outputs.

---

## Phase 5 — Agent Ontology Tool

Expose the ontology service to the Agent.

Example:

```text
User:
"What is a strategic supplier?"

Agent:
→ ontology.search("strategic supplier")
→ ontology.get_entity(...)
→ response
```

At this phase, ontology-only questions should work before integrating production data.

---

## Phase 6 — Warehouse Integration

Map selected ontology concepts to warehouse entities.

Start with one use case such as:

```text
Supplier + Category + Spend
```

Do not integrate the entire warehouse at once.

---

## Phase 7 — Contract Integration

Start with:

```text
Supplier
Contract
ExpirationDate
ContractClause
```

Then add clause-level semantic mappings.

---

## Phase 8 — Graph Integration

Introduce graph storage only when relationship traversal or business use cases justify it.

Examples:

- parent/child supplier structures;
- multi-tier supplier networks;
- material dependencies;
- risk propagation.

---

## Phase 9 — Evaluation

Create a fixed evaluation set.

Examples:

```text
ontology lookup questions
hierarchy questions
supplier-spend questions
contract questions
cross-system questions
ambiguous terminology questions
```

Measure:

- concept-resolution accuracy;
- retrieval accuracy;
- grounding;
- factual correctness;
- latency;
- tool-selection quality;
- hallucination rate.

---

# 23. Immediate MVP Use Case

Recommended first vertical slice:

> **Supplier + Contract semantic assistant**

Model:

```text
Supplier
Contract
ContractType
ContractClause
PaymentTerm
ExpirationDate
Category
```

Implement ontology relationships such as:

```text
Contract hasSupplier Supplier
Contract hasClause ContractClause
Supplier belongsToCategory Category
Contract hasPaymentTerm PaymentTerm
```

Then support:

```text
"What is a supplier?"
"What contracts are associated with supplier X?"
"What does payment term mean?"
"Which contracts expire soon?"
```

This is much more useful than trying to model every procurement concept before testing the architecture.

---

# 24. Example Semantic Flow

Suppose a user asks:

> Show me high-risk suppliers whose contracts expire soon.

Agent flow:

```text
User question
      ↓
LLM parses intent
      ↓
Ontology service resolves:
  high-risk supplier
  contract
  expiration
      ↓
Ontology determines approved concepts/relations
      ↓
Warehouse/graph tool finds supplier/risk facts
      ↓
Contract tool finds expiration dates/documents
      ↓
Join by stable business identifiers
      ↓
LLM generates grounded answer
```

The ontology helps determine what the business terms mean.

It does not invent the actual current supplier risk or contract expiration facts.

---

# 25. Example Ontology-to-Enterprise Mapping

Conceptual mapping:

```text
scp:Supplier
       │
       ├── maps to warehouse dim_supplier
       │
       ├── maps to graph node :Supplier
       │
       └── maps to contract metadata supplier_id
```

Stable shared business identifier:

```text
supplier_id = SUP_000123
```

This allows the Agent to connect semantic meaning with distributed evidence.

---

# 26. Testing Strategy

## Ontology tests

Test:

- required labels;
- required definitions;
- hierarchy constraints;
- namespace rules;
- logical consistency;
- competency questions.

## OAK tests

Example expected behavior:

```text
search("supplier") → contains scp:Supplier
get_label("scp:Supplier") → "Supplier"
```

## Mapping tests

Example:

```text
scp:Supplier ↔ dim_supplier
```

must resolve correctly.

## Agent tests

The Agent should not:

- invent ontology terms;
- use deprecated terms without warning;
- claim warehouse facts without querying data;
- claim contract clauses without document evidence.

---

# 27. Security / Enterprise Considerations

Later implementation should address:

- access control;
- contract confidentiality;
- supplier-sensitive information;
- row/column-level warehouse permissions;
- audit logging;
- prompt injection from documents;
- tool authorization;
- data lineage;
- output provenance;
- secrets management.

Ontology metadata itself may be less sensitive than contract/business data, but internal definitions can still be proprietary.

---

# 28. Design Decisions Already Made

The following are current project assumptions and should be treated as intentional unless changed explicitly:

### Decision 1
Use **Protégé** for ontology editing.

### Decision 2
Use **Git** for ontology source control.

### Decision 3
Use **ODK** for ontology lifecycle/repository engineering.

### Decision 4
Use **ROBOT** for automated ontology operations, validation, reasoning, merge, and release-related tasks where appropriate.

### Decision 5
Use **OAK / Ontology Access Kit (`oaklib`, `runoak`)** as the main programmatic ontology-access layer.

### Decision 6
Use **SemSQL + SQLite** as a practical runtime/query representation of ontology content.

### Decision 7
The AI Agent will eventually combine:

```text
Ontology
+ Graph Database
+ Data Warehouse
+ Contract Documents
```

rather than relying on one storage system.

### Decision 8
OWL remains the ontology source of truth.

Generated SQLite/SemSQL artifacts are derivative.

### Decision 9
The ontology should describe domain semantics, not absorb all enterprise transactional data.

### Decision 10
Start with a narrow procurement/supplier/contract MVP before expanding the ontology.

---

# 29. Open Architecture Decisions

Codex should not silently decide these without evidence from the existing environment:

1. Production graph database vendor.
2. Production data warehouse technology.
3. Agent framework.
4. Vector database/search engine.
5. Contract extraction engine.
6. Authentication/authorization architecture.
7. Deployment platform.
8. Internal ontology base IRI/domain.
9. Final multilingual label policy.
10. Whether SemSQL DB artifacts are committed to Git or published only as release artifacts.
11. Whether runtime ontology access is embedded in the Agent service or exposed as a standalone API.

These should be recorded through ADRs or explicit documentation once chosen.

---

# 30. Recommended Architecture Decision Records

Create an `docs/adr/` directory later.

Potential ADRs:

```text
ADR-001 ontology namespace strategy
ADR-002 ODK governance model
ADR-003 OAK ontology access boundary
ADR-004 SemSQL runtime representation
ADR-005 ontology vs enterprise-data responsibility
ADR-006 graph database selection
ADR-007 Agent tool architecture
ADR-008 contract retrieval architecture
```

---

# 31. First Tasks for Codex

When first opened in Codex, proceed in this order unless the repository already contains some of these pieces.

## Task 1 — Inspect

Inspect:

- current directory structure;
- existing OWL files;
- existing Git configuration;
- existing Python environment;
- existing Docker configuration;
- existing ODK files;
- existing scripts;
- existing documentation.

Do not overwrite working files.

---

## Task 2 — Report current state

Summarize:

```text
what exists
what is missing
what appears experimental
what appears production-intended
```

---

## Task 3 — Establish environment

If missing, propose/create:

- Python environment;
- dependency file;
- `.gitignore`;
- minimal README;
- test structure;
- Docker strategy.

Do not add unnecessary frameworks.

---

## Task 4 — Ontology skeleton

If no ontology exists, create a small initial supply-chain ontology containing only the agreed MVP concepts.

Do not attempt to create hundreds of classes.

---

## Task 5 — ODK/ROBOT workflow

Set up or validate:

```text
edit
→ report
→ reason
→ release
```

Add reproducible commands and documentation.

---

## Task 6 — SemSQL build

Create a reproducible build path:

```text
OWL
→ validated/normalized OWL
→ SemSQL SQLite
```

Place generated files in an appropriate build/release directory.

---

## Task 7 — OAK access layer

Implement a minimal Python ontology adapter.

First milestone:

```python
search_concepts()
get_label()
get_definition()
get_ancestors()
get_descendants()
```

Add unit tests.

---

## Task 8 — Agent tool interface

Create a clean ontology tool interface, but do not prematurely build a large autonomous Agent.

First prove that structured ontology retrieval works correctly.

---

# 32. Definition of Done for the First Technical Milestone

The first milestone is complete when all of the following are true:

- [ ] ontology repository is version-controlled;
- [ ] ontology opens correctly in Protégé;
- [ ] core Supplier / Contract / Category concepts exist;
- [ ] ontology QC runs from command line;
- [ ] logical validation passes;
- [ ] reproducible OWL release can be generated;
- [ ] SemSQL SQLite artifact can be generated reproducibly;
- [ ] Python can access ontology through OAK;
- [ ] search for `supplier` resolves to the approved ontology concept;
- [ ] tests execute locally;
- [ ] README documents setup and common commands;
- [ ] no production credentials are stored in repository.

---

# 33. Terminology Cheat Sheet

| Term | Meaning in this project |
|---|---|
| OWL | Primary ontology representation |
| RDF | Graph data model underlying ontology statements |
| TBox | Conceptual/schema layer |
| ABox | Concrete assertion/instance layer |
| IRI | Stable global identifier |
| CURIE | Compact identifier such as `scp:Supplier` |
| Protégé | Ontology authoring UI |
| ODK | Ontology project/lifecycle engineering toolkit |
| ROBOT | Ontology command-line automation tool |
| OAK | Ontology Access Kit |
| `oaklib` | Python package for OAK |
| `runoak` | OAK command-line interface |
| SemSQL | SQL schema/views for ontology data |
| SQLite | Local relational database engine |
| SPARQL | RDF/ontology query language |
| Reasoner | Software that checks/infers OWL logical relationships |
| Graph DB | Store for large connected business data |
| Data warehouse | Store for structured analytical facts |
| RAG | Retrieval-augmented generation |
| Agent tool | Controlled function the LLM can invoke |

---

# 34. Architecture Principle in One Sentence

> **Use OWL to define what supply-chain concepts mean, ODK/ROBOT to govern that semantic model, SemSQL/OAK to make it accessible to software, and the AI Agent to combine those semantics with real facts from enterprise databases and documents.**

---

# 35. References / Tool Identity

These references are included mainly so future developers/Codex can verify tool identity and current behavior rather than accidentally using a similarly named project.

- Ontology Development Kit (ODK):  
  https://github.com/INCATools/ontology-development-kit

- ROBOT documentation:  
  https://robot.obolibrary.org/

- Ontology Access Kit (OAK):  
  https://github.com/INCATools/ontology-access-kit

- SemSQL / Semantic SQL:  
  https://github.com/INCATools/semantic-sql

---

# 36. Final Note to Codex

The priority is **not** to maximize the number of technologies.

The priority is to build a semantic platform that is:

```text
understandable
→ testable
→ versioned
→ reproducible
→ queryable
→ integrable
→ governable
```

Keep the first implementation narrow.

Make the ontology reliable first.

Then expose it through OAK.

Then connect one real business data source.

Then connect the Agent.

Expand only after the vertical slice works.
