#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
image=$(python3 -c 'import json; print(json.load(open("config/toolchain.lock.json"))["odk_image"])')
docker run --rm --platform linux/amd64 --mount "type=bind,source=$(pwd),target=/work" -w /work/src/ontology -e PYSTOW_HOME=/work/build/cache "$image" python /work/scripts/tool_versions.py
docker run --rm --platform linux/amd64 --mount "type=bind,source=$(pwd),target=/work" -w /work/src/ontology -e PYSTOW_HOME=/work/build/cache "$image" make sca-test IMP=false
