import argparse,json,sys
from pathlib import Path
from cabot_ontology.validation import validate
p=argparse.ArgumentParser();p.add_argument('--formal',action='store_true');a=p.parse_args()
root=Path(__file__).resolve().parents[1]
errors=validate(root,a.formal)
print(json.dumps({'passed':not errors,'errors':errors},ensure_ascii=False,indent=2))
sys.exit(bool(errors))
