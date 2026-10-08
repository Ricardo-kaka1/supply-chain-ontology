# Project extensions; keep the official seed-generated Makefile unchanged.
VERSION = 0.1.0-dev
RELEASEDIR = ../../build/releases/$(VERSION)
ONTBASE = https://example.org/cabot-audit/ontology
PYTHON ?= python
export PYTHONPATH := $(abspath ..):$(PYTHONPATH)
export PYSTOW_HOME := $(abspath ../../build/cache)
CONTEXT_FILE_CSV = config/prefixes.csv

$(EDIT_PREPROCESSED): imports/metadata.owl catalog-v001.xml | $(TMPDIR)
$(SRCMERGED): imports/metadata.owl | $(TMPDIR)
$(REPORT_FILES): profile.txt

.PHONY: sca-qc sca-build sca-test sca-demo sca-formal-release
sca-qc: test
	$(PYTHON) ../../scripts/check.py

sca-build: sca-qc
	mkdir -p $(RELEASEDIR)
	$(MAKE) prepare_release IMP=false
	$(ROBOT) merge -i ../../examples/owl/cabot-demo.owl reason --reasoner hermit annotate --ontology-iri urn:example:cabot-audit:demo.owl --annotation owl:versionInfo $(VERSION) -o $(RELEASEDIR)/scaudit-demo.owl
	$(ROBOT) validate-profile -i $(RELEASEDIR)/scaudit-demo.owl --profile DL -o $(RELEASEDIR)/demo-owl2dl.txt
	semsql make $(RELEASEDIR)/scaudit-demo.db -P config/prefixes.csv
	test -s $(RELEASEDIR)/scaudit-demo.db
	$(PYTHON) ../../scripts/manifest.py $(RELEASEDIR)

sca-test: sca-build
	cd ../.. && CABOT_RELEASE_DIR=$(abspath $(RELEASEDIR)) $(PYTHON) -m unittest discover -s tests -v
	$(PYTHON) ../../scripts/integration_checks.py $(RELEASEDIR)

sca-demo:
	$(PYTHON) -m cabot_ontology.cli $(RELEASEDIR)/scaudit-demo.db evidence ex:Finding_INV017

sca-formal-release:
	$(PYTHON) ../../scripts/check.py --formal
	$(MAKE) sca-test
